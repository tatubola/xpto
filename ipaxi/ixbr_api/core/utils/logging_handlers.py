import logging


def log_object(message, object, severity=logging.INFO, user=None, **kwargs):
    logger = logging.getLogger('root')
    context = {**{'object': object, 'user': user}, **kwargs}

    logger.log(severity, message, extra=context)
