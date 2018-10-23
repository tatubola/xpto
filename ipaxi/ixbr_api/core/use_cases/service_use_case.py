from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from ..models import Service


def delete_service_use_case(**kwargs):
    """ Delete a Service object

    Args:
        pk: kwarg -> Service primary key

    """

    service_pk = kwargs.pop('pk')
    try:
        service = Service.get_objects_filter('pk', service_pk).pop(0)
        if service.status != 'ALLOCATED':
            raise ValidationError(_("Service must be ALLOCATED to be removed"))
        for mac in service.mac_addresses.all():
            mac.delete()
        if service.tag.status != 'AVAILABLE':
            service.tag.update_status('AVAILABLE')
        service.delete()
        return {}
    except IndexError as e:
        raise ValidationError(_("Invalid service primary key"))
