import logging
import pprint

from .globals import set_current_user


class RequestLogging(object):
    """Django middleware for logging user access"""

    def __init__(self, get_response):
        self.logger = logging.getLogger('root')

        self.get_response = get_response

    def __call__(self, request):
        pp = pprint.PrettyPrinter(indent=4)

        self.logger.info("User access", exc_info=True,
                         extra={'request': pp.pformat(request.__dict__)})        


        return self.get_response(request)

class SaveCurrentUser(object):
    """
    Stores the user associated with the request in local thread memory
    It is currently used so models can get the user, since they don't directly
    have access to the request 
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user'):
            set_current_user(request.user)

        return self.get_response(request)
