from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import (ChannelPort, CustomerChannel,
                       DownlinkChannel, Port, Switch, UplinkChannel,)
from ..makefaketestdata import MakeFakeTestData


class Test_Port(TestCase):
    """Tests Port model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

    def test__str__(self):
        self.assertEqual(
            str(self.port_cpv_kapotnhinore_1),
            '[%s: %s]' % (
                self.port_cpv_kapotnhinore_1.switch.management_ip,
                self.port_cpv_kapotnhinore_1.name))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(Port._meta.verbose_name), 'Port')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(Port._meta.verbose_name_plural), 'Ports')

    def test_unique_together(self):
        with self.assertRaisesMessage(
            ValidationError,
                'Port with this Switch and Name already exists.'):
            self.port_test = Port.objects.create(
                capacity=1000,
                connector_type='SFP',
                channel_port=self.channel_port_cpv_kapotnhinore_1,
                physical_interface=None,
                name='TenGigE0/0/1/1',
                status='INFRASTRUCTURE',
                switch=self.extreme_pix_kapotnhinore,
                last_ticket='2121')

    def test_meta_order_by(self):
        self.assertEqual(Port.objects.all().ordered, True)

        self.assertEqual(
            str(Port.objects.all()[0]), str(self.port_cpv_kapotnhinore_1))
        self.assertEqual(
            str(Port.objects.all()[1]), str(self.port_cpv_kapotnhinore_2))
        self.assertEqual(
            str(Port.objects.all()[2]), str(self.port_cpv_kapotnhinore_3))
        self.assertEqual(
            str(Port.objects.all()[3]), str(self.port_sp_araguaia_1))
        self.assertEqual(
            str(Port.objects.all()[4]), str(self.port_sp_araguaia_2))
        self.assertEqual(
            str(Port.objects.all()[5]), str(self.port_sp_kadiweu_1))
        self.assertEqual(
            str(Port.objects.all()[6]), str(self.port_sp_kadiweu_2))
        self.assertEqual(
            str(Port.objects.all()[7]), str(self.port_sp_kadiweu_3))
        self.assertEqual(
            str(Port.objects.all()[8]), str(self.port_sp_kadiweu_4))

    def test_simple_history(self):
        # is the last port_sp_araguaia_2 in the historical table?
        self.assertEqual(self.port_sp_araguaia_2,
                         self.port_sp_araguaia_2.history.most_recent())
        self.port_sp_araguaia_2.description = 'my description'
        self.port_sp_araguaia_2.save()
        # is the last port_sp_araguaia_2 in the historical table?
        self.assertEqual(
            self.port_sp_araguaia_2.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.port_sp_araguaia_2.history.most_recent().modified_by,
            self.superuser)
        # is there two instances of port_sp_araguaia_2 in the historical table?

        self.assertEqual(self.port_sp_araguaia_2.history.count(), 2)

    def test_validation(self):
        with self.assertRaisesMessage(
            ValidationError,
                'Change Status if associated a Channel port.'):
            self.port_test = Port.objects.create(
                capacity=1000,
                connector_type='SFP',
                channel_port=self.channel_port_sp_araguaia_2,
                physical_interface=None,
                name='1',
                status='AVAILABLE',
                switch=self.cisco_sp_araguaia,
                last_ticket='2121')

        with self.assertRaisesMessage(
            ValidationError,
                'Change Channel port if Status is not "Available".'):
            self.port_test = Port.objects.create(
                capacity=1000,
                connector_type='SFP',
                physical_interface=None,
                name='1',
                status='CUSTOMER',
                switch=self.cisco_sp_araguaia,
                last_ticket='2121')

    def test_capacity_connector_type(self):
        with self.assertRaisesMessage(
            ValidationError,
                'port_capacity not compatible with connector_type'):
            self.port_test = Port.objects.create(
                capacity=10000,
                connector_type='SFP',
                physical_interface=None,
                name='1',
                status='AVAILABLE',
                switch=self.cisco_sp_araguaia,
                last_ticket='2121')
            self.port_test.save()

    def test_connector_type_physical_interface(self):
        with self.assertRaisesMessage(
            ValidationError,
                'port_connector_type not compatible with'
                ' physical_interface connector_type'):
            self.port_test = Port.objects.create(
                capacity=1000,
                connector_type='SFP',
                physical_interface=self.interface_1,
                name='1',
                status='AVAILABLE',
                switch=self.cisco_sp_araguaia,
                last_ticket='2121')
            self.port_test.save()

    def test_invalid_customer_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.downlink_channel_sp_araguaia_1 = DownlinkChannel.objects.create(
            name='dl-BE1090',
            channel_port=self.channel_port_sp_araguaia_4,
            last_ticket='2121',
            is_lag=True,
            is_mclag=False,)

        self.uplink_channel_sp_araguaia_2 = UplinkChannel.objects.create(
            name='ul-BE1080',
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4,
            downlink_channel=self.downlink_channel_sp_araguaia_1,
            last_ticket='2121',
            is_lag=True)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        with self.assertRaisesMessage(
            ValidationError,
                'CUSTOMER only allowed if Channel port has a CustomerChannel'):
            self.port_sp_araguaia_3.channel_port = self.\
                channel_port_sp_araguaia_4
            self.port_sp_araguaia_3.status = 'CUSTOMER'
            self.port_sp_araguaia_3.save()

    def test_valid_customer_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.nic,
            name='ct-BE1590',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_3.channel_port = self.channel_port_sp_araguaia_4
        self.port_sp_araguaia_3.status = 'CUSTOMER'
        self.port_sp_araguaia_3.save()

    def test_invalid_infrastructure_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.nic,
            name='ct-BE1095',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        with self.assertRaisesMessage(
            ValidationError,
                'INFRASTRUCTURE not allowed if '
                'Channel port has a CustomerChannel'):
            self.port_sp_araguaia_3.channel_port = self.\
                channel_port_sp_araguaia_4
            self.port_sp_araguaia_3.status = 'INFRASTRUCTURE'
            self.port_sp_araguaia_3.save()

    def test_valid_infrastructure_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.downlink_channel_sp_araguaia_1 = DownlinkChannel.objects.create(
            name='dl-BE1090',
            channel_port=self.channel_port_sp_araguaia_4,
            last_ticket='2121',
            is_lag=True,
            is_mclag=False,)

        self.uplink_channel_sp_araguaia_2 = UplinkChannel.objects.create(
            name='ul-BE1080',
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4,
            downlink_channel=self.downlink_channel_sp_araguaia_1,
            last_ticket='2121',
            is_lag=True)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_3.channel_port = self.channel_port_sp_araguaia_4
        self.port_sp_araguaia_3.status = 'INFRASTRUCTURE'
        self.port_sp_araguaia_3.save()

    def test_invalid_reserved_customer_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.downlink_channel_sp_araguaia_1 = DownlinkChannel.objects.create(
            name='dl-BE1090',
            channel_port=self.channel_port_sp_araguaia_4,
            last_ticket='2121',
            is_lag=True,
            is_mclag=False,)

        self.uplink_channel_sp_araguaia_2 = UplinkChannel.objects.create(
            name='ul-BE1080',
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4,
            downlink_channel=self.downlink_channel_sp_araguaia_1,
            last_ticket='2121',
            is_lag=True)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_3.channel_port = self.channel_port_sp_araguaia_4
        self.port_sp_araguaia_3.status = 'RESERVED_CUSTOMER'

        with self.assertRaisesMessage(
            ValidationError,
                'RESERVED_CUSTOMER only allowed if'
                ' Channel port has a CustomerChannel'):
            self.port_sp_araguaia_3.save()

    def test_valid_reserved_customer_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.nic,
            name='ct-BE1050',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_3.channel_port = self.channel_port_sp_araguaia_4
        self.port_sp_araguaia_3.status = 'RESERVED_CUSTOMER'
        self.port_sp_araguaia_3.save()

    def test_invalid_reserved_infrastructure_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.nic,
            name='ct-BE1050',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_3.channel_port = self.channel_port_sp_araguaia_4
        self.port_sp_araguaia_3.status = 'RESERVED_INFRA'

        with self.assertRaisesMessage(
            ValidationError,
                'RESERVED_INFRA not allowed if Channel '
                'port has a CustomerChannel'):
            self.port_sp_araguaia_3.save()

    def test_valid_reserved_infrastructure_status(self):
        self.channel_port_sp_araguaia_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='124',
            create_tags=False)

        self.cisco_sp_araguaia_3 = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_4,
            name='TenGigE0/0/2/4',
            status='UNAVAILABLE',
            last_ticket='2175')

        self.downlink_channel_sp_araguaia_1 = DownlinkChannel.objects.create(
            name='dl-BE1090',
            channel_port=self.channel_port_sp_araguaia_4,
            last_ticket='2121',
            is_lag=True,
            is_mclag=False,)

        self.uplink_channel_sp_araguaia_2 = UplinkChannel.objects.create(
            name='ul-BE1050',
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_4,
            downlink_channel=self.downlink_channel_sp_araguaia_1,
            last_ticket='2121',
            is_lag=True)

        self.port_sp_araguaia_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            name='TenGigE0/0/2/8',
            status='AVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_3.channel_port = self.channel_port_sp_araguaia_4
        self.port_sp_araguaia_3.status = 'RESERVED_INFRA'
        self.port_sp_araguaia_3.save()

    def test_update_name(self):
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: Port.name'):
            self.port_sp_araguaia_1.name = 'new_name'
            self.port_sp_araguaia_1.save()

    def test_update_capacity(self):
        with self.assertRaisesMessage(
            ValidationError,
                'Trying to update non updatable field: Port.capacity'):
            self.port_sp_araguaia_1.connector_type = 'SFP+'
            self.port_sp_araguaia_1.capacity = 10000
            self.port_sp_araguaia_1.save()

    def test_update_configured_capacity_error_whith_value_bigger_than_capacity(self):
        with self.assertRaisesMessage(
            ValidationError,
                'Configured capacity must be the same or lower than capacity'):
            self.port_sp_araguaia_1.configured_capacity = 10000
            self.port_sp_araguaia_1.save()

    def test_update_configured_capacity_error_whith_not_valid_choice(self):
        with self.assertRaisesMessage(
            ValidationError,
                'Value 1234 is not a valid choice'):
            self.port_sp_araguaia_1.configured_capacity = 1234
            self.port_sp_araguaia_1.save()

    def test_update_configured_capacity_success(self):
        self.port_sp_araguaia_1.configured_capacity = 100
        self.port_sp_araguaia_1.save()
        pass
