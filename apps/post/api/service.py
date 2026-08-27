import logging


def _safe_notify(func, *args, **kwargs):

    try:
        func(*args, **kwargs)
    except Exception as exc:           
        logger = logging.getLogger(__name__)
        logger.warning("Notification %s failed: %s", func.__name__, exc)    