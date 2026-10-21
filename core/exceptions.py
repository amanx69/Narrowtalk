import logging
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from django.db import IntegrityError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger('django.request')


class Exe(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


def custom_exception_handler(exc, context):
    """
    Global custom exception handler for Django REST Framework.
    
    1. Handles DRF and Django built-in exceptions cleanly.
    2. Intercepts database IntegrityErrors (duplicate entries, foreign key issues).
    3. Intercepts unhandled 500 exceptions, logs the full trace internally,
       and returns a safe, non-revealing error response to clients.
    4. Normalizes error payloads so frontend can reliably read `error`, `message`, or `detail`.
    """
    # 1. Map Django exceptions to DRF responses
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            detail = exc.message_dict
        elif hasattr(exc, 'messages'):
            detail = exc.messages
        else:
            detail = str(exc)
        return Response({'error': detail}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, Http404):
        return Response({'error': 'Resource not found.'}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, DjangoPermissionDenied):
        return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, IntegrityError):
        logger.warning(f"Database IntegrityError in {context.get('view', '')}: {exc}")
        err_str = str(exc).lower()
        if 'unique' in err_str or 'duplicate' in err_str:
            clean_msg = "An entry with this information already exists."
        else:
            clean_msg = "A database constraint conflict occurred. Please review your request."
        return Response({'error': clean_msg}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Call standard DRF exception handler
    response = exception_handler(exc, context)

    # 3. Unhandled Server Exceptions (500)
    if response is None:
        view = context.get('view')
        view_name = view.__class__.__name__ if view else 'Unknown'
        logger.error(
            f"Unhandled Exception in {view_name}: {exc}",
            exc_info=True,
            extra={'context': context}
        )

        # Notify Sentry if installed and active
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(exc)
        except Exception:
            pass

        return Response(
            {
                'error': 'Something went wrong. Please try again later.',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 4. Normalize response data payload
    if response.data is not None:
        if isinstance(response.data, list):
            first_msg = response.data[0] if response.data else "Validation error"
            response.data = {
                'error': str(first_msg),
                'details': response.data
            }
        elif isinstance(response.data, dict):
            # If 'error' or 'message' is not explicitly present, extract primary message
            if 'error' not in response.data and 'message' not in response.data:
                if 'detail' in response.data:
                    response.data['error'] = response.data['detail']
                else:
                    # Pick the first field error as a top-level error message for mobile snackbars
                    for key, val in response.data.items():
                        if isinstance(val, list) and val:
                            response.data['error'] = f"{key}: {val[0]}"
                            break
                        elif isinstance(val, str):
                            response.data['error'] = f"{key}: {val}"
                            break

    return response