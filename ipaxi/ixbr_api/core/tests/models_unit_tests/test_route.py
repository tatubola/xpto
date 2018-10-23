from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import (ChannelPort, Port, Route, Switch,
                       SwitchModel, SwitchPortRange,)
from ..makefaketestdata import MakeFakeTestData


class Test_Route(TestCase):
    """Tests Route model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

        self.route_a = Route.objects.create(
            description='route 1', last_ticket='11')

    def test__str__(self):
        self.assertEqual(str(self.route_a), '[route 1]')

    def test_meta_verbose_name(self):
        self.assertEqual(str(Route._meta.verbose_name), 'Route')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(Route._meta.verbose_name_plural), 'Routes')

    def test_simple_history(self):
        # is the last route_a in the historical table?
        self.assertEqual(self.route_a, self.route_a.history.most_recent())
        self.route_a.description = 'my description'
        self.route_a.save()
        # is the last pixa in the historical table?
        self.assertEqual(
            self.route_a.history.most_recent().description, 'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.route_a.history.most_recent().modified_by, self.superuser)
        # is there two instances of pixa in the historical table?
        self.assertEqual(self.route_a.history.count(), 2)

    def test_route_with_ports_ok(self):
        self.port_cpv_kapotnhinore_1.route = self.route_a
        self.port_cpv_kapotnhinore_1.route.save()
        self.port_cpv_kapotnhinore_2.route = self.route_a
        self.port_cpv_kapotnhinore_2.route.save()
        self.port_cpv_kapotnhinore_3.route = self.route_a
        self.port_cpv_kapotnhinore_3.route.save()
        pass

    def test_route_with_ports_different_ix(self):
        self.channel_port_test_ix_1 = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.port_test_ix_1 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test_ix_1,
            physical_interface=None,
            name='TenGigE0/0/1/4',
            status='INFRASTRUCTURE',
            switch=self.extreme_pix_kapotnhinore,
            last_ticket='2121')

        self.channel_port_test_ix_2 = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.port_test_ix_2 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test_ix_2,
            physical_interface=None,
            name='TenGigE0/0/1/5',
            status='INFRASTRUCTURE',
            switch=self.cisco_sp_kadiweu,
            last_ticket='2121')

        self.port_test_ix_1.route = self.route_a
        self.port_test_ix_1.save()
        with self.assertRaisesMessage(ValidationError,
                                      "Route can't be in different IX."):
            self.port_test_ix_2.route = self.route_a
            self.port_test_ix_2.save()

    def test_route_with_ports_more_than_two_switch(self):
        self.channel_port_test_ix_1 = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.port_test_ix_1 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test_ix_1,
            physical_interface=None,
            name='TenGigE0/0/1/4',
            status='INFRASTRUCTURE',
            switch=self.cisco_sp_kadiweu,
            last_ticket='2121')

        self.port_test_ix_2 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test_ix_1,
            physical_interface=None,
            name='TenGigE0/0/1/5',
            status='INFRASTRUCTURE',
            switch=self.cisco_sp_araguaia,
            last_ticket='2121')

        self.port_test_ix_1.route = self.route_a
        self.port_test_ix_1.save()
        self.port_test_ix_2.route = self.route_a
        self.port_test_ix_2.save()

        self.cisco_sp_3 = SwitchModel.objects.create(
            model='ASR9432',
            vendor='CISCO',
            last_ticket='27686')
        self.cisco_sp_araguaia_port_3 = SwitchPortRange.objects.create(
            switch_model=self.cisco_sp_3,
            name_format='TenGigE0/0/3/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=27,
            last_ticket='21661')
        self.cisco_sp_araguaia_2 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_3,
            management_ip='192.168.5.252',
            last_ticket='453',
            translation=False,
            create_ports=False)

        with self.assertRaisesMessage(ValidationError,
                                      "Only permitted 2 Switches per Route."):
            self.port_test_ix_3 = Port.objects.create(
                capacity=1000,
                connector_type='SFP+',
                channel_port=self.channel_port_test_ix_1,
                physical_interface=None,
                name='TenGigE0/0/1/6',
                status='INFRASTRUCTURE',
                switch=self.cisco_sp_araguaia_2,
                last_ticket='2121')
            self.port_test_ix_3.route = self.route_a
            self.port_test_ix_3.save()

    def test_if_migrate_port_that_is_part_of_route_dont_raise_exception(self):
        self.route_a.port_set.add(self.port_sp_kadiweu_1)
        self.route_a.port_set.add(self.port_sp_araguaia_1)
        self.port_sp_araguaia_1.switch = self.cisco_sp_kadiweu
        self.port_sp_araguaia_1.save()
