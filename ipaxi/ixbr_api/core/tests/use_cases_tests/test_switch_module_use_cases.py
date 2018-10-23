from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import Port, Switch, SwitchModule, SwitchPortRange
from ...use_cases.switch_module_use_cases import (associate_ports_switch_use_case,
                                                  create_switch_module_use_case,
                                                  create_switch_module_with_ports_use_case,
                                                  delete_switch_module_use_case)
from ..login import DefaultLogin


class SwitchModuleUseCaseTest(TestCase):

    def setUp(self):

        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    def test_associate_ports_switch_use_case(self):

        switch = mommy.make(
            Switch)

        module = mommy.make(
            SwitchModule)

        associate_ports_switch_use_case(switch=switch, module=module)

        for port in module.port_set.all():
            self.assertIn(port, Port.objects.filter(switch=switch))

    def test_create_switch_module_use_case(self):

        switch = mommy.make(
            Switch)

        port_range = mommy.make(
            SwitchPortRange,
)

        model = 'ABC'
        vendor = 'EXTREME'
        ticket = 0
        name_format='{}'
        port_qtd=10
        capacity=1000
        connector_type='SFP'

        module = create_switch_module_use_case(
            ticket=ticket,
            vendor=vendor,
            model=model,
            name_format=name_format,
            port_quantity=port_qtd,
            capacity=capacity,
            connector_type=connector_type
            )

        self.assertEqual(module.vendor, vendor)
        self.assertEqual(module.model, model)
        self.assertEqual(module.port_quantity, port_qtd)

    def test_create_switch_module_with_ports_use_case(self):

        switch = mommy.make(
            Switch)

        model = 'ABC'
        vendor = 'EXTREME'
        switch_model = switch.model
        ticket = 0
        name = '{}'
        begin = '1'
        end = '10'
        capacity = 1000
        connector = 'SFP'
        port_qtd = 10

        module = create_switch_module_with_ports_use_case(
            ticket=ticket,
            switch=switch,
            vendor=vendor,
            model=model,
            name=name,
            capacity=capacity,
            connector=connector,
            name_format=name,
            begin=begin,
            end=end)

        self.assertEqual(module.vendor, vendor)
        self.assertEqual(module.model, model)
        self.assertEqual(module.port_quantity, port_qtd)

        for port in module.port_set.all():
            self.assertIn(port, Port.objects.filter(switch=switch))

    def test_delete_switch_module_use_case(self):

        switch = mommy.make(
            Switch)

        model = 'ABC'
        vendor = 'EXTREME'
        ticket = 0
        name = '{}'
        begin = 1
        end = 10
        capacity = 1000
        connector = 'SFP'

        module = create_switch_module_with_ports_use_case(
            ticket=ticket,
            switch=switch,
            vendor=vendor,
            model=model,
            name=name,
            capacity=capacity,
            connector=connector,
            name_format=name,
            begin=begin,
            end=end)

        pk = module.pk

        self.assertNotEqual(SwitchModule.objects.filter(pk=pk).count(), 0)
        self.assertNotEqual(Port.objects.filter(
            switch_module__pk=pk).count(), 0)

        delete_switch_module_use_case(pk=pk)

        self.assertEqual(SwitchModule.objects.filter(pk=pk).count(), 0)
        self.assertEqual(Port.objects.filter(switch_module__pk=pk).count(), 0)
