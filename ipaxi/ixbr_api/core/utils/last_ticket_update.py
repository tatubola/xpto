""" This script creates decorators to update service's last ticket
"""

# System imports
import inspect
import re

# Third-party imports
import wrapt
from django.db.models import Q

# Local source tree imports
from ixbr_api.core import models
from ixbr_api.core.utils.regex import Regex
from ixbr_api.core.views import form_views


@wrapt.decorator
def updatelastticket(wrapped, instance, args, kwargs):
    """ Decorator to updates service's last_ticket attribute

    This routine implements a decorator to be used in methods or functions
    that updates or creates new services for a given AS. The ticker id will
    be used to inform the last ticket that was used to make changes in a
    service.

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
            return wrapped(*args, **kwargs)
        # If decorator is applied to a Function or Staticmethod
        else:
            return wrapped(*args, **kwargs)
    else:
        # If decorator is applied to a classmethod
        if inspect.isclass(instance):
            return wrapped(*args, **kwargs)
        # If decorator is applied to an instancemethod
        else:
            raw_ticket_post = args[0]['last_ticket']
            last_ticket = parse_html_ticket(str(raw_ticket_post))

            raw_path = instance.request.path
            service_uuid = parse_service_uuid_in_url(str(raw_path))

            # Add Mac to a Service
            if type(instance) is form_views.AddMACServiceFormView:
                update_last_ticket(last_ticket,
                                   find_customer_channel(service_uuid))
            # Add a new service to a Channel
            elif type(instance) is form_views.GenericMLPAUsedChannelFormView:
                update_last_ticket(last_ticket, service_uuid)
            else:
                print("Last Ticket Update not Implemented for this method")
                print("Instance: {}".format(instance))
            return wrapped(*args, **kwargs)


def parse_html_ticket(html_string):
    """ Removes all HTML tags and symbols and extract a ticket number

    Args:
        html_string: The HTML string to be processed

    Returns: An integer representing a ticket id

    """
    ticket_regex = re.compile("value=\"(\d{1,10})\"")
    last_ticket = ticket_regex.findall(html_string)
    return last_ticket[0]


def parse_service_uuid_in_url(raw_path):
    """ Removes all unnecessary characters from a post path

    Args:
        raw_path: A path in format /something/something/.../<UUID>/something...

    Returns: A valid UUID extracted from the URL

    """
    uuid_regex = re.compile(Regex().uuid)
    service_uuid = uuid_regex.findall(raw_path)
    if len(service_uuid) == 1:
        return service_uuid[0]
    else:
        return service_uuid[1]


def find_customer_channel(service_uuid):
    """ Find the customer channel using a sub service UUID

    Args:
        ticket: The ticket number to be updated
        service_uuid: Service UUID to have the filed updated

    Returns: The customer channel UUID of a given service

    """
    cur_customer_channel = models.CustomerChannel.objects.filter(
        Q(mlpav4__pk=service_uuid) |
        Q(mlpav6__pk=service_uuid) |
        Q(bilateralpeer__pk=service_uuid) |
        Q(monitorv4__pk=service_uuid))
    return cur_customer_channel[0].uuid


def update_last_ticket(new_ticket, uuid):
    """ Updates on DB the new ticket of a given customer channel

    Args:
        old_ticket: Ticket before the update
        new_ticket: New ticket to be used in DB
        uuid: The customer channel UUID

    Returns:

    """
    cur_customer_channel = models.CustomerChannel.objects.filter(pk=uuid)
    old_ticket = cur_customer_channel[0].last_ticket
    cur_customer_channel.update(last_ticket=new_ticket)

    log_service_ticket_update(old_ticket, new_ticket, uuid)


def log_service_ticket_update(ticket_before_update, ticket_after_update, uuid):
    """ Routine to log ticket updates

    Args:
        ticket_before_update: Ticket # before the update
        ticket_after_update:  Ticket # to be updated
        uuid: Service UUID where the ticket is being updated

    Returns:

    """
    print("Service UUID {} Ticket Updated: From {} To {}.".format(uuid,
                                                        ticket_before_update,
                                                        ticket_after_update))
