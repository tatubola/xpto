from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from ..models import Channel, SwitchPortRange, create_all_ports
from ..utils.constants import SWITCH_MODEL_CHANNEL_PREFIX


def __migrate_switch_attributes(old_switch, new_switch):
    new_switch.management_ip = old_switch.management_ip
    new_switch.is_pe = old_switch.is_pe
    old_switch.management_ip = ''
    old_switch.is_pe = False
    old_switch.save()
    new_switch.save()


def __migrate_switch_ports(old_switch, new_switch):
    unavailable_ports = old_switch.get_unavailable_ports()
    ports_of_new_switch = list(new_switch.port_set.all())
    names_of_ports = [port.name for port in ports_of_new_switch]

    for i in range(len(unavailable_ports)):
        # Two ports cannot have the same name in a switch.
        try:
            index = names_of_ports.index(unavailable_ports[i].name)
        except ValueError:
            index = i

        ports_of_new_switch[index].delete()
        unavailable_ports[i].switch = new_switch
        unavailable_ports[i].save()

    old_switch.port_set.all().delete()
    if old_switch.create_ports:
        create_all_ports(old_switch)


def __update_names_of_connected_channels(old_switch, new_switch):
    channels = Channel.get_channels_of_switch(new_switch)
    for channel in channels:
        channel.name = channel.name.replace(
            SWITCH_MODEL_CHANNEL_PREFIX[old_switch.model.vendor],
            '')
        index_of_hyphen = channel.name.index('-')
        channel.name = \
            channel.name[0:index_of_hyphen + 1] + \
            SWITCH_MODEL_CHANNEL_PREFIX[new_switch.model.vendor] + \
            channel.name[index_of_hyphen + 1:]
        channel.save()


def migrate_switch(old_switch, new_switch):
    """ Migrates this switch to a new switch.
    All ports from this switch are migrated to the new switch.

    Args:
    old_switch : Switch instance
    new_switch : Switch instance
    """

    if old_switch.pix != new_switch.pix:
        raise ValueError(_("Switches must be in the same pix"))
    if(old_switch.get_unavailable_ports().count() >
       SwitchPortRange.get_number_of_ports(new_switch.model)):
        raise ValidationError(
            "Insufficient number of ports of selected model")

    __migrate_switch_attributes(old_switch, new_switch)
    __migrate_switch_ports(old_switch, new_switch)
    __update_names_of_connected_channels(old_switch, new_switch)
