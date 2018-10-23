from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import (ChannelPort, CustomerChannel, IPv4Address, MACAddress,
                       MLPAv4, Monitorv4, Port, Switch, Tag)
from ...validators import RESERVED_IP
from ..login import DefaultLogin
from ..makefaketestdata import MakeFakeTestData


class Test_Monitorv4(TestCase):
    """Tests monitorv4 model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

    def setUp_new(self):
        DefaultLogin.__init__(self)

    def test__str__(self):
        self.assertEqual(str(self.monitorv4_sp_1), "%s [%s AS%s %s:%s]" % (
            self.monitorv4_sp_1.uuid,
            self.monitorv4_sp_1.shortname,
            self.monitorv4_sp_1.asn.number,
            self.monitorv4_sp_1.tag,
            self.monitorv4_sp_1.inner))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(Monitorv4._meta.verbose_name), 'Monitorv4')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(Monitorv4._meta.verbose_name_plural), 'Monitorsv4')

    def test_unique_together(self):
        # unique_together = (('asn', 'tag', 'inner'),)
        self.assertEqual(self.monitorv4_sp_1.asn, self.monitorv4_sp_2.asn)
        self.assertEqual(self.monitorv4_sp_1.inner, self.monitorv4_sp_2.inner)
        self.monitorv4_sp_1.tag = self.tag_sp_monitor_v4_2
        with self.assertRaisesMessage(
            ValidationError,
                'Monitorv4 with this Asn, Tag and Inner already exists.'):
            self.monitorv4_sp_1.save()

    def test_meta_order_by(self):
        self.assertEqual(Monitorv4.objects.all().ordered, True)
        self.assertEqual(str(Monitorv4.objects.all()[
                         0]), str(self.monitorv4_sp_3))
        self.assertEqual(str(Monitorv4.objects.all()[
                         1]), str(self.monitorv4_sp_1))
        self.assertEqual(str(Monitorv4.objects.all()[
                         2]), str(self.monitorv4_sp_2))

    def test_simple_history(self):
        # is the last monitorv4_sp_1 in the historical table?
        self.assertEqual(self.monitorv4_sp_1,
                         self.monitorv4_sp_1.history.most_recent())
        self.monitorv4_sp_1.description = 'my description'
        self.monitorv4_sp_1.save()
        # is the last monitorv4_sp_1 in the historical table?
        self.assertEqual(
            self.monitorv4_sp_1.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.monitorv4_sp_1.history.most_recent().modified_by,
            self.superuser)
        # is there three instances of monitorv4_sp_1
        # in the historical table? (monitorv4)
        # Factory has a "POST GENERATION" function)
        self.assertEqual(self.monitorv4_sp_1.history.count(), 2)

    def test_mac_by_service_limit(self):
        # test the limit of MAC Address allowed by monitorv4
        self.ipv4_sp_monitor_v4_4 = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.9',
            last_ticket='45',
            in_lg=False)
        self.ipv4_sp_monitor_v4_5 = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.10',
            last_ticket='45',
            in_lg=False)
        self.ipv4_sp_monitor_v4_6 = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.11',
            last_ticket='45',
            in_lg=False)

        self.monitorv4_sp_4 = Monitorv4.objects.create(
            asn=self.nic,
            tag=self.tag_sp_monitor_v4_3,
            inner=1003,
            monitor_address=self.ipv4_sp_monitor_v4_4,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-4',
            last_ticket='5336')
        self.monitorv4_sp_5 = Monitorv4.objects.create(
            asn=self.nic,
            tag=self.tag_sp_monitor_v4_3,
            inner=1004,
            monitor_address=self.ipv4_sp_monitor_v4_5,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-4',
            last_ticket='5336')
        self.monitorv4_sp_6 = Monitorv4.objects.create(
            asn=self.nic,
            tag=self.tag_sp_monitor_v4_3,
            inner=1005,
            monitor_address=self.ipv4_sp_monitor_v4_6,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-4',
            last_ticket='5336')

        self.mac_addresses_test_1 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a1',
            last_ticket='3')
        self.mac_addresses_test_2 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a2',
            last_ticket='3')

        self.monitorv4_sp_4.mac_addresses.add(self.mac_address_cpv_1)
        self.monitorv4_sp_4.save()
        self.monitorv4_sp_4.mac_addresses.add(self.mac_address_cpv_2)
        self.monitorv4_sp_4.save()
        self.monitorv4_sp_4.mac_addresses.add(self.mac_address_cpv_3)
        with self.assertRaisesMessage(
            ValidationError,
                'Only 2 MAC/Service are allowed'):
            self.monitorv4_sp_4.save()

        self.monitorv4_sp_4.mac_addresses = set()
        self.monitorv4_sp_4.mac_addresses.add(self.mac_address_cpv_1)
        self.monitorv4_sp_4.save()
        self.monitorv4_sp_5.mac_addresses.add(self.mac_addresses_test_1)
        self.monitorv4_sp_5.save()
        self.monitorv4_sp_6.mac_addresses.add(self.mac_addresses_test_2)
        self.monitorv4_sp_6.save()
        self.monitorv4_sp_2.mac_addresses.add(self.mac_address_cpv_2)
        self.monitorv4_sp_2.save()
        self.monitorv4_sp_1.mac_addresses.add(self.mac_address_cpv_3)

        with self.assertRaisesMessage(
            ValidationError,
                'Only 4 MACs by AS by Channel is allowed'):
            self.monitorv4_sp_1.save()

    def test_mac_by_as_by_ix_by_service_limit(self):
        # test MAC in distinct AS in same IX
        self.monitorv4_sp_1.mac_addresses.add(self.mac_address_cpv_2)
        self.monitorv4_sp_1.save()
        self.monitorv4_sp_2.mac_addresses.add(self.mac_address_cpv_2)
        with self.assertRaisesMessage(
            ValidationError,
                'Only a MAC/Monitor/IX is allowed'):
            self.monitorv4_sp_2.save()

    def test_mac_by_distinct_as(self):
        # test MAC in distinct AS in distinct IX
        self.monitorv4_sp_1.mac_addresses.add(self.mac_address_cpv_2)
        self.monitorv4_sp_1.save()
        self.monitorv4_sp_3.mac_addresses.add(self.mac_address_cpv_2)
        with self.assertRaisesMessage(
            ValidationError,
                'Only a MAC/Monitor/IX is allowed'):
            self.monitorv4_sp_3.save()

        self.tag_sp_teste = Tag.objects.create(
            tag='333',
            ix=self.sp,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_sp_test = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.2.5',
            last_ticket='2121',
            in_lg=False)

        self.monitorv4_sp_test = MLPAv4.objects.create(
            tag=self.tag_sp_teste,
            asn=self.nic,
            inner=1002,
            mlpav4_address=self.ipv4_sp_test,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-teste',
            last_ticket='264')

        self.monitorv4_sp_test.mac_addresses.add(self.mac_address_cpv_2)
        try:
            self.monitorv4_sp_test.save()
            pass
        except ValidationError:
            self.assertTrue(0, 'ASNs MAC blocked in distincts IX')

    def test_mac_by_as_by_customer_channel_limit(self):
        self.tag_sp_teste = Tag.objects.create(
            tag='333',
            ix=self.sp,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_sp_test = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        self.monitorv4_sp_test = MLPAv4.objects.create(
            tag=self.tag_sp_teste,
            asn=self.nic,
            inner=1002,
            mlpav4_address=self.ipv4_sp_test,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-teste',
            last_ticket='264')

        self.mac_address_cpv_test_1 = MACAddress.objects.create(
            address='45:b3:b7:25:3a:ff',
            last_ticket='2')

        self.mac_address_cpv_test_2 = MACAddress.objects.create(
            address='45:b3:b7:25:a3:ff',
            last_ticket='3')
        try:
            self.monitorv4_sp_test.mac_addresses.add(
                self.mac_address_cpv_test_1)
            self.monitorv4_sp_test.mac_addresses.add(
                self.mac_address_cpv_test_2)
            self.monitorv4_sp_test.save()
            # self.assertTrue(0, 'broken MAC limit by asn by customer channel')
        except ValidationError:
            pass

    def test_cix_type_zero_fail(self):
        # raise ValidationError with service from another ASN in the same
        # customer_channel
        self.channel_port_test = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.cisco_test = Switch.objects.create(
            pix=self.kadiweu,
            model=self.cisco_sp_2,
            management_ip='192.168.5.252',
            last_ticket='453',
            create_ports=False)

        self.port_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_test,
            channel_port=self.channel_port_test,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.chamacoco,
            name='ct-BE1080',
            last_ticket='663',
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_test)

        self.port_sp_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test,
            physical_interface=None,
            name='TenGigE0/0/0/10',
            status='CUSTOMER',
            switch=self.cisco_sp_kadiweu,
            last_ticket='543')

        self.tag_sp_teste = Tag.objects.create(
            tag='333',
            ix=self.sp,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_sp_test = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        self.monitorv4_sp_test = MLPAv4.objects.create(
            tag=self.tag_sp_teste,
            asn=self.kinikinau,
            mlpav4_address=self.ipv4_sp_test,
            last_ticket='2121',
            customer_channel=self.customer_channel_terena,
            shortname='as-' + str(self.terena.number) + 'monitorv4')

        self.monitorv4_sp_test.customer_channel = self.customer_channel_test
        with self.assertRaisesMessage(
            ValidationError,
                "Respective Customer Channel is a individual "
                "port and doesn't accept participants."):
            self.monitorv4_sp_test.save()

    def test_cix_type_zero_ok(self):
        self.channel_port_test = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.cisco_test = Switch.objects.create(
            pix=self.kapotnhinore,
            model=self.cisco_sp_2,
            management_ip='192.168.4.252',
            last_ticket='453',
            create_ports=False)

        self.port_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_test,
            channel_port=self.channel_port_test,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.metuktire,
            name='ct-BE1080',
            last_ticket='663',
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_test)

        self.port_sp_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test,
            physical_interface=None,
            name='TenGigE0/0/0/10',
            status='CUSTOMER',
            switch=self.cisco_sp_kadiweu,
            last_ticket='543')

        self.tag_sp_teste = Tag.objects.create(
            tag='333',
            ix=self.sp,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_sp_test = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        self.monitorv4_sp_test = MLPAv4.objects.create(
            tag=self.tag_sp_teste,
            asn=self.nic,
            mlpav4_address=self.ipv4_sp_test,
            last_ticket='2121',
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4')

        self.monitorv4_sp_test.save()

    def test_asn_ix_customer_channel_fail(self):
        # Try to create a service with different IX in the ASN.
        self.tag_sp_teste = Tag.objects.create(
            tag='333',
            ix=self.sp,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_sp_test = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        with self.assertRaisesMessage(
            ValidationError,
                "This ASN doesn't belong to "
                "the same IX from customer channel."):
            self.monitorv4_sp_test = MLPAv4.objects.create(
                tag=self.tag_sp_teste,
                asn=self.metuktire,
                mlpav4_address=self.ipv4_sp_test,
                last_ticket='2121',
                customer_channel=self.customer_channel_nic,
                shortname='as-' + str(self.metuktire.number) + 'monitorv4')

        self.channel_port_test = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.cisco_test = Switch.objects.create(
            pix=self.kapotnhinore,
            model=self.cisco_sp_2,
            management_ip='192.168.4.252',
            last_ticket='453',
            create_ports=False)

        self.port_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_test,
            channel_port=self.channel_port_test,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.customer_channel_test = CustomerChannel.objects.create(
            asn=self.metuktire,
            name='ct-BE1080',
            last_ticket='663',
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_test)

        self.channel_port_test.port_set = set()

        with self.assertRaisesMessage(
            ValidationError,
                "Customer Channel associated MUST have in a least one port."):
            self.monitorv4_sp_test = MLPAv4.objects.create(
                tag=self.tag_sp_teste,
                asn=self.nic,
                mlpav4_address=self.ipv4_sp_test,
                last_ticket='2121',
                customer_channel=self.customer_channel_test,
                shortname='as-' + str(self.nic.number) + 'monitorv4')

    def test_post_delete_functions(self):
        self.assertGreaterEqual(len(self.nic.contactsmap_set.all()), 1)

        self.customer = self.monitorv4_sp_1.customer_channel
        self.assertTrue(self.monitorv4_sp_1)
        self.monitorv4_sp_1.delete()

    def test_create_monitor_with_reserved_ipv4_to_fail(self):
        self.setUp_new()
        ipv4 = mommy.make(IPv4Address, ix=self.cpv, address='10.0.2.10')
        ipv4.reserve_this()
        tag = mommy.make(
            Tag,
            tag='333',
            ix=self.cpv,
            status='AVAILABLE',
        )
        with self.assertRaisesMessage(ValidationError, RESERVED_IP.format(ipv4)):
            Monitorv4.objects.create(
                monitor_address=ipv4,
                customer_channel=self.customer_channel_metuktire,
                asn=self.metuktire,
                last_ticket='2121',
                tag=tag,
                shortname='mlpav4',
                status='QUARANTINE'
            )
