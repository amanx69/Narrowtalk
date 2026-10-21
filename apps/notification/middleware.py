# middleware.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        access_token = AccessToken(token)
        return User.objects.get(id=access_token["user_id"])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Secure JWT Authentication Middleware for Channels WebSockets.
    Authenticates via:
    1. HTTP Authorization Header ('Bearer <token>') - Most Secure
    2. Sec-WebSocket-Protocol Header
    3. Query parameter fallback ('?token=<token>') for backward compatibility
    """
    async def __call__(self, scope, receive, send):
        token = None

        # 1. Extract from Authorization Header (Never logged in URL query strings)
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        elif auth_header:
            token = auth_header.strip()

        # 2. Extract from Sec-WebSocket-Protocol Header
        if not token:
            subprotocols = headers.get(b"sec-websocket-protocol", b"").decode("utf-8")
            if subprotocols:
                token = subprotocols.split(",")[0].strip()

        # 3. Fallback to query parameter (?token=...)
        if not token:
            query_string = scope.get("query_string", b"").decode("utf-8")
            params = parse_qs(query_string)
            token_list = params.get("token")
            if token_list:
                token = token_list[0]

        scope["user"] = await get_user(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)
