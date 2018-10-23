from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from ..models import Port, SwitchModule, SwitchPortRange


def create_module_ports_use_case(**kwargs):
    """create all the ports of a given switch module
        to a Switch

    Args:
        switch: kwarg -> the switch to be associated
        module: kwarg -> the port's switch module
        begin: kwarg -> the initial port name
        end: kwarg -> the last port name

    """
    ticket = kwargs.pop('ticket')
    switch = kwargs.pop('switch')
    module = kwargs.pop('module')
    begin = kwargs.pop('begin')
    end = kwargs.pop('end')
    begin = int(begin)
    end = int(end)

    if begin > end:
        raise ValidationError(_("Begin must be equal or smaller than end"))
    if begin == 0:
        raise ValidationError(_("Begin must be greater than zero"))

    for port_number in range(begin, end + 1):
        port = Port.objects.create(
            name=module.name_format.format(port_number),
            capacity=module.capacity,
            configured_capacity=module.capacity,
            connector_type=module.connector_type,
            status='AVAILABLE',
            switch=switch,
            switch_module=module,
            last_ticket=ticket)
        port.save()


def associate_ports_switch_use_case(**kwargs):
    """ associate all the ports of a given switch module
        to a Switch

    Args:
        switch: kwarg -> the switch to be associated
        module: kwarg -> the port's switch module

    """

    switch = kwargs.pop('switch')
    module = kwargs.pop('module')

    for port in module.port_set.all():
        port.switch = switch
        switch.port_set.add(port)
        port.save()
        switch.save()


def create_switch_module_use_case(**kwargs):
    """ Instantiate a switch module

    Args:
        ticket: kwarg -> the orgin ticket
        port_range: kwarg -> switch port range instance
        model: kwarg -> the module model
        vendor: kwarg -> the module vendor
    Returns:
        Module: The created module

    """

    ticket = kwargs.pop('ticket')
    port_quantity = kwargs.pop('port_quantity')
    model = kwargs.pop('model')
    vendor = kwargs.pop('vendor')
    capacity = kwargs.pop('capacity')
    connector_type = kwargs.pop('connector_type')
    name_format = kwargs.pop('name_format')

    module = SwitchModule.objects.create(
        last_ticket=ticket,
        model=model,
        vendor=vendor,
        port_quantity=port_quantity,
        capacity=capacity,
        connector_type=connector_type,
        name_format=name_format)

    # TODO: It's necessary?
    # associate_ports_switch_use_case(
    #     switch=switch, module=module)

    return module


def create_switch_module_with_ports_use_case(**kwargs):
    """ Instantiate a switch module and all his ports

    Args:
        ticket: kwarg -> the orgin ticket
        port_range: kwarg -> switch port range instance
        switch: kwarg -> the switch to be associated
        model: kwarg -> the module model
        vendor: kwarg -> the module vendor
        capacity: kwarg -> ports capacity
        connector: kwarg -> ports connector
        name: kwarg -> name format
        begin: kwarg -> firts port
        end: kwarg -> last port
    Returns:
       SwitchModule instance

    """
    ticket = kwargs.pop('ticket')
    switch = kwargs.pop('switch')
    model = kwargs.pop('model')
    vendor = kwargs.pop('vendor')
    capacity = kwargs.pop('capacity')
    connector = kwargs.pop('connector')
    name = kwargs.pop('name')
    begin = kwargs.pop('begin')
    end = kwargs.pop('end')
    port_quantity = int(end) - int(begin) + 1

    module = create_switch_module_use_case(
        ticket=ticket,
        switch=switch,
        port_quantity=port_quantity,
        vendor=vendor,
        model=model,
        capacity=capacity,
        connector_type=connector,
        name_format=name)

    create_module_ports_use_case(
        ticket=ticket,
        switch=switch,
        module=module,
        begin=begin,
        end=end)

    # TODO: Include call to create ports related with module

    # return (port_range, module)
    # TODO: include port_range associate with module
    return module


def delete_switch_module_use_case(**kwargs):
    """ Delete a SwitchModule instance

    Args:
        pk: kwarg -> SwitchModule PK

    """

    pk = kwargs.pop('pk')

    module = SwitchModule.objects.filter(pk=pk)
    if module:
        Port.objects.filter(switch_module=module.first()).delete()
        module.delete()
    else:
        raise ValidationError(_("Invalid switch module primary key"))
