from django.utils.translation import gettext as _

from ..models import ChannelPort, CoreChannel, DownlinkChannel, UplinkChannel

NOT_PE_ERROR = _("PE switch must be connected with other pe")
UPLINK_NOT_PE = _("UplinkChannel does not apply on pe Switch")


def create_uplink_channel_use_case(**kwargs):
    """ Function to instantiate and link Uplink and Downlink

    Args:
        origin_ports = List of Port objects 
        dest_ports =  List of Port objects
        channel_origin_name = Str channel name
        channel_dest_name = Str channel name
        create_tags = Bool 
        ticket = Integer

    Returns:
        channel_origin = PK of created UplinkChannel
        channel_dest = PK of created DownlinkChannel
    """

    origin_ports = kwargs.pop('origin_ports')
    dest_ports = kwargs.pop('dest_ports')
    channel_origin_name = kwargs.pop('channel_origin_name')
    channel_dest_name = kwargs.pop('channel_dest_name')
    create_tags = kwargs.pop('create_tags')
    ticket = kwargs.pop('ticket')

    channel_origin_name = "ul-{0}".format(channel_origin_name)
    channel_dest_name = "dl-{0}".format(channel_dest_name)

    if origin_ports[0].switch.is_pe:

        raise ValueError(UPLINK_NOT_PE)

    else:
        channel_port_origin = ChannelPort.objects.create(
            last_ticket=ticket,
            tags_type='Indirect-Bundle-Ether',
            create_tags=False)

    if dest_ports[0].switch.is_pe:

        channel_port_dest = ChannelPort.objects.create(
            last_ticket=ticket,
            tags_type='Direct-Bundle-Ether',
            create_tags=False)

    else:

        channel_port_dest = ChannelPort.objects.create(
            last_ticket=ticket,
            tags_type='Indirect-Bundle-Ether',
            create_tags=False)

    for port in origin_ports:
        channel_port_origin.port_set.add(port)
        port.channel_port = channel_port_origin
        port.status = 'UNAVAILABLE'
        port.save()
        channel_port_origin.save()

    for port in dest_ports:
        channel_port_dest.port_set.add(port)
        port.channel_port = channel_port_dest
        port.status = 'UNAVAILABLE'
        port.save()
        channel_port_dest.save()

    channel_port_dest.create_tags = create_tags
    channel_port_dest.save()
    origin_mclag = len(set([port.switch for port in origin_ports])) > 1
    dest_mclag = len(set([port.switch for port in dest_ports])) > 1

    origin_lag = len(origin_ports) > 1
    dest_lag = len(dest_ports) > 1

    downlink = DownlinkChannel.objects.create(
        last_ticket=ticket,
        name=channel_dest_name,
        is_lag=dest_lag,
        is_mclag=dest_mclag,
        channel_port=channel_port_dest)

    uplink = UplinkChannel.objects.create(
        last_ticket=ticket,
        name=channel_origin_name,
        is_lag=origin_lag,
        is_mclag=origin_mclag,
        channel_port=channel_port_origin,
        downlink_channel=downlink)

    for port in origin_ports:
        port.status = 'INFRASTRUCTURE'
        port.save()

    for port in dest_ports:
        port.status = 'INFRASTRUCTURE'
        port.save()

    return uplink.pk, downlink.pk


def create_core_channel_use_case(**kwargs):
    """ Function to instantiate and link two CoreChannels

    Args:
        origin_ports = List of Port objects 
        dest_ports =  List of Port objects
        channel_origin_name = Str channel name
        channel_dest_name = Str channel name
        create_tags = Bool 
        ticket = Integer

    Returns:
        channel_origin = PK of created CoreChannel
        channel_dest = PK of created CoreChannel
    """

    origin_ports = kwargs.pop('origin_ports')
    dest_ports = kwargs.pop('dest_ports')
    channel_origin_name = kwargs.pop('channel_origin_name')
    channel_dest_name = kwargs.pop('channel_dest_name')
    create_tags = kwargs.pop('create_tags')
    ticket = kwargs.pop('ticket')

    channel_origin_name = "cc-{0}".format(channel_origin_name)
    channel_dest_name = "cc-{0}".format(channel_dest_name)

    if not origin_ports[0].switch.is_pe:

        raise ValueError(NOT_PE_ERROR)

    else:

        channel_port_origin = ChannelPort.objects.create(
            last_ticket=ticket,
            tags_type='Core',
            create_tags=False)

    if dest_ports[0].switch.is_pe:

        channel_port_dest = ChannelPort.objects.create(
            last_ticket=ticket,
            tags_type='Core',
            create_tags=create_tags)

    else:

        raise ValueError(NOT_PE_ERROR)

    for port in origin_ports:
        channel_port_origin.port_set.add(port)
        port.channel_port = channel_port_origin
        port.status = 'UNAVAILABLE'
        port.save()
        channel_port_origin.save()

    for port in dest_ports:
        channel_port_dest.port_set.add(port)
        port.channel_port = channel_port_dest
        port.status = 'UNAVAILABLE'
        port.save()
        channel_port_dest.save()

    origin_mclag = len(set([port.switch for port in origin_ports])) > 1
    dest_mclag = len(set([port.switch for port in dest_ports])) > 1

    origin_lag = len(origin_ports) > 1
    dest_lag = len(dest_ports) > 1

    core_origin = CoreChannel.objects.create(
        last_ticket=ticket,
        name=channel_origin_name,
        channel_port=channel_port_origin,
        is_lag=origin_lag,
        is_mclag=origin_mclag)

    core_dest = CoreChannel.objects.create(
        last_ticket=ticket,
        name=channel_dest_name,
        channel_port=channel_port_dest,
        is_lag=dest_lag,
        is_mclag=dest_mclag)

    core_origin.other_core_channel = core_dest
    core_dest.other_core_channel = core_origin
    core_origin.save()
    core_dest.save()

    for port in origin_ports:
        port.status = 'INFRASTRUCTURE'
        port.save()

    for port in dest_ports:
        port.status = 'INFRASTRUCTURE'
        port.save()

    return core_origin.pk, core_dest.pk


def create_uplink_core_channel_use_case(**kwargs):
    """ Function to instantiate and link between two generic channels

    Args:
        origin_ports = List of Port objects 
        dest_ports =  List of Port objects
        channel_origin_name = Str channel name
        channel_dest_name = Str channel name
        create_tags = Bool 
        ticket = Integer
        channel_type = Choice [Uplink, Core]

    Returns:
        origin = PK of created Channel
        dest = PK of created Channel
    """

    origin_ports = kwargs.pop('origin_ports')
    dest_ports = kwargs.pop('dest_ports')
    channel_origin_name = kwargs.pop('channel_origin_name')
    channel_dest_name = kwargs.pop('channel_dest_name')
    create_tags = kwargs.pop('create_tags')
    ticket = kwargs.pop('ticket')
    channel_type = kwargs.pop('channel_type')

    if channel_type == 'CORE':

        origin, dest = create_core_channel_use_case(
            origin_ports=origin_ports,
            dest_ports=dest_ports,
            channel_origin_name=channel_origin_name,
            channel_dest_name=channel_dest_name,
            create_tags=create_tags,
            ticket=ticket)

    elif channel_type == 'UPLINK':

        origin, dest = create_uplink_channel_use_case(
            origin_ports=origin_ports,
            dest_ports=dest_ports,
            channel_origin_name=channel_origin_name,
            channel_dest_name=channel_dest_name,
            create_tags=create_tags,
            ticket=ticket)

    else:
        raise ValueError(_("Invalid value on channel_type"))

    return origin, dest
