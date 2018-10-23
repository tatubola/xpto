""" This script creates decorators to log users activities
"""
import inspect

import wrapt


@wrapt.decorator
def ixapilog(wrapped, instance, args, kwargs):
    """ Log decorator for the system.
    This routine implements a decorator to be used in methods or functions
    where log is necessary.

    Args:
        wrapped: the function or method decorated
        instance: if the method decorated is a method, it store the class
        args: all arguments passed to the function or routine
        kwargs: dict that stores all parameters

    Returns: Wrapped function/method itself with args and kwargs

    """
    if instance is None:
        # If decorator is applied to a class
        if inspect.isclass(wrapped):
            print("Decorator Applied to a Class")
            print("Class Name: {}".format(wrapped))
            return wrapped(*args, **kwargs)
        # If decorator is applied to a Function or Staticmethod
        else:
            if len(args) > 0:
                if hasattr(args[0], 'user'):
                    user = args[0].user
                else:
                    user = None
                if hasattr(args[0], 'path'):
                    path = args[0].path
                else:
                    path = None
                msg = "User: {}, Path: {}, Function: {}, Args: {}".format(user,
                                                                    path,
                                                                    wrapped,
                                                                    kwargs)
                print(msg)
            else:
                print("Access to Function: {}, Args: {}".format(wrapped,
                                                                kwargs))
            return wrapped(*args, **kwargs)
    else:
        # If decorator is applied to a classmethod
        if inspect.isclass(instance):
            print("Decorator applied to a classmethod")
            return wrapped(*args, **kwargs)
        # If decorator is applied to an instancemethod
        else:
            user = instance.request.user
            path = instance.request.path
            print("User: {}, Path: {}, Method Called: {}, Args: {}".format(
                                                                    user,
                                                                    path,
                                                                    wrapped,
                                                                    args))
            return wrapped(*args, **kwargs)
