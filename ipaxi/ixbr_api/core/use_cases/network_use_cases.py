from ..models import DownlinkChannel, Switch, UplinkChannel


def next_switch(**kwargs):

    """ Function to take the adjacent switches for a given switch

    Args:
        switch: kwarg -> A Switch Model object

    Returns:
        list of tuples (Switch, DownlinkChannel): the neighboors switches list,
            composed by tuples of switch and the DownlinkChannel that connect
            it.
    """
    current_switch = kwargs.pop('switch')

    uplinks = UplinkChannel.objects.filter(
        channel_port__in=current_switch.port_set.all().values_list(
            'channel_port', flat=True))
    downlinks = DownlinkChannel.objects.filter(uplinkchannel__in=uplinks)

    switches = [(downlink.channel_port.port_set.first().switch, downlink)
                for downlink in downlinks]

    return switches

def bfs_switch(**kwargs):
    """ Breadth-first search for switch to find the PE node

    Args:
        origin_vertex: kwarg -> A Switch Model object

    Returns:
        tuple (Switch, DownlinkChannel): A tuple containing the is_pe Switch
            and the DownlinkChannel to get it.

    This funciton is dependent of the following functions:
        next_switch
    """
    origin_vertex = kwargs.pop('origin_vertex')
    checklist = set()
    checklist.add((origin_vertex, None))
    while len(checklist) > 0:
        current_vertex = checklist.pop()
        if current_vertex[0].is_pe:
            return current_vertex
        else:
            [checklist.add(switch_and_downlink)
                for switch_and_downlink in next_switch(switch=current_vertex[0])]


def get_pe_channel_by_channel(**kwargs):
    """ gets the DownlinkChannel of the is_pe switch from a starting
        channel

    Args:
        channel: kwarg -> The origin Channel
        ix: kwarg -> the owner IX
    Returns:
        DownlinkChannel: The is_pe Switch's DownlinkChannel

    This funciton is dependent of the following functions:
        bfs_switch
        next_switch
    """
    channel = kwargs.pop('channel')
    ix = kwargs.pop('ix')

    switch = Switch.objects.filter(
        port__pk__in=channel.channel_port.port_set.values_list(
            'pk', flat=True), pix__ix=ix)

    pe = switch.filter(is_pe=True)
    if pe:
        return channel
    else:
        switch = switch.first()
        channel = bfs_switch(origin_vertex=switch)

        if not channel:
            return []
        return channel[1]
