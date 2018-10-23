from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import (ChannelPort, CustomerChannel, IPv4Address, MACAddress,
                       MLPAv4, Port, Switch, Tag)
from ...validators import RESERVED_IP
from ..login import DefaultLogin
from ..makefaketestdata import MakeFakeTestData


class Test_MLPAv4(TestCase):
    """Tests MLPAv4 model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

    def setUp_new(self):
        DefaultLogin.__init__(self)

    def test__str__(self):
        self.assertEqual(str(self.mlpv4_cpv_kayapo), "%s [%s AS%s %s:%s]" % (
            self.mlpv4_cpv_kayapo.uuid,
            self.mlpv4_cpv_kayapo.shortname,
            self.mlpv4_cpv_kayapo.asn.number,
            self.mlpv4_cpv_kayapo.tag,
            self.mlpv4_cpv_kayapo.inner))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(MLPAv4._meta.verbose_name), 'MLPAv4')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(MLPAv4._meta.verbose_name_plural), 'MLPAsv4')

    def test_unique_together(self):
        self.assertEqual(
            self.mlpv4_cpv_metuktire_1.asn,
            self.mlpv4_cpv_metuktire_2.asn)
        self.assertEqual(
            self.mlpv4_cpv_metuktire_1.inner,
            self.mlpv4_cpv_metuktire_2.inner)
        self.mlpv4_cpv_metuktire_1.tag = self.tag_cpv_metuktire_v4_2
        with self.assertRaisesMessage(
            ValidationError,
                'MLPAv4 with this Asn, Tag and Inner already exists.'):
            self.mlpv4_cpv_metuktire_1.save()

    def test_meta_order_by(self):
        self.assertEqual(MLPAv4.objects.all().ordered, True)
        self.assertEqual(str(MLPAv4.objects.all()[
                         0]), str(self.mlpv4_sp_kinikinau))
        self.assertEqual(str(MLPAv4.objects.all()[
                         1]), str(self.mlpv4_sp_chamacoco))
        self.assertEqual(str(MLPAv4.objects.all()[
                         2]), str(self.mlpv4_sp_terena))
        self.assertEqual(str(MLPAv4.objects.all()[
                         3]), str(self.mlpv4_cpv_metuktire_1))
        self.assertEqual(str(MLPAv4.objects.all()[
                         4]), str(self.mlpv4_cpv_metuktire_2))
        self.assertEqual(str(MLPAv4.objects.all()[
                         5]), str(self.mlpv4_cpv_kayapo))

    def test_simple_history(self):
        # is the last mlpv4_sp_kinikinau in the historical table?
        self.assertEqual(self.mlpv4_sp_kinikinau,
                         self.mlpv4_sp_kinikinau.history.most_recent())
        self.mlpv4_sp_kinikinau.description = 'my description'
        self.mlpv4_sp_kinikinau.save()
        # is the last mlpv4_sp_kinikinau in the historical table?
        self.assertEqual(
            self.mlpv4_sp_kinikinau.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.mlpv4_sp_kinikinau.history.most_recent().modified_by,
            self.superuser)
        # is there three instances of mlpv4_sp_kinikinau in the
        # historical table? (MLPAv4)
        # Factory has a "POST GENERATION" function)
        self.assertEqual(self.mlpv4_sp_kinikinau.history.count(), 2)

    def test_mac_by_service_limit(self):
        # test the limit of MAC Address allowed by MLPAv4
        self.ipv4_cpv_test_1 = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.5',
            last_ticket='2121',
            in_lg=False)
        self.ipv4_cpv_test_2 = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)
        self.ipv4_cpv_test_3 = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.7',
            last_ticket='2121',
            in_lg=False)

        self.mlpv4_cpv_test_1 = MLPAv4.objects.create(
            tag=self.tag_cpv_metuktire_v4_2,
            asn=self.metuktire,
            inner=1001,
            mlpav4_address=self.ipv4_cpv_test_1,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4',
            last_ticket='3123')
        self.mlpv4_cpv_test_2 = MLPAv4.objects.create(
            tag=self.tag_cpv_metuktire_v4_2,
            asn=self.metuktire,
            inner=1002,
            mlpav4_address=self.ipv4_cpv_test_2,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4',
            last_ticket='3123')
        self.mlpv4_cpv_test_3 = MLPAv4.objects.create(
            tag=self.tag_cpv_metuktire_v4_2,
            asn=self.metuktire,
            inner=1003,
            mlpav4_address=self.ipv4_cpv_test_3,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4',
            last_ticket='3123')

        self.mac_addresses_test_1 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a1',
            last_ticket='3')
        self.mac_addresses_test_2 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a2',
            last_ticket='3')

        self.mlpv4_cpv_test_1.mac_addresses.add(self.mac_address_cpv_1)
        self.mlpv4_cpv_test_1.save()
        self.mlpv4_cpv_test_1.mac_addresses.add(self.mac_address_cpv_2)
        self.mlpv4_cpv_test_1.save()
        self.mlpv4_cpv_test_1.mac_addresses.add(self.mac_address_cpv_3)
        with self.assertRaisesMessage(
            ValidationError,
                'Only 2 MAC/Service are allowed'):
            self.mlpv4_cpv_test_1.save()

        self.mlpv4_cpv_test_1.mac_addresses = set()
        self.mlpv4_cpv_test_1.mac_addresses.add(self.mac_address_cpv_1)
        self.mlpv4_cpv_test_1.save()
        self.mlpv4_cpv_test_2.mac_addresses.add(self.mac_addresses_test_1)
        self.mlpv4_cpv_test_2.save()
        self.mlpv4_cpv_test_3.mac_addresses.add(self.mac_addresses_test_2)
        self.mlpv4_cpv_test_3.save()
        self.mlpv4_cpv_metuktire_2.mac_addresses.add(self.mac_address_cpv_2)
        self.mlpv4_cpv_metuktire_2.save()
        self.mlpv4_cpv_metuktire_1.mac_addresses.add(self.mac_address_cpv_3)
        with self.assertRaisesMessage(
            ValidationError,
                'Only 4 MACs by AS by Channel is allowed'):
            self.mlpv4_cpv_metuktire_1.save()

    def test_mac_by_as_by_ix_by_service_limit(self):
        # test MAC in distinct AS in same IX
        self.mlpv4_cpv_metuktire_1.mac_addresses.add(self.mac_address_cpv_2)
        self.mlpv4_cpv_metuktire_1.save()
        self.mlpv4_cpv_metuktire_2.mac_addresses.add(self.mac_address_cpv_2)
        with self.assertRaisesMessage(
            ValidationError,
                'Only a MAC/MLPAv4/IX is allowed'):
                self.mlpv4_cpv_metuktire_2.save()

    def test_mac_by_distinct_as(self):
        # test MAC in distinct AS in distinct IX
        self.mlpv4_cpv_kayapo.mac_addresses.add(self.mac_address_cpv_2)
        self.mlpv4_cpv_kayapo.save()
        self.mlpv4_cpv_metuktire_2.mac_addresses.add(self.mac_address_cpv_2)
        with self.assertRaisesMessage(
            ValidationError,
                'Only a MAC/MLPAv4/IX is allowed'):
            self.mlpv4_cpv_metuktire_2.save()

        self.tag_sp_teste = Tag.objects.create(
            tag='333',
            ix=self.sp,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_cpv_test = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.5',
            last_ticket='2121',
            in_lg=False)

        self.mlpv4_sp_test = MLPAv4.objects.create(
            tag=self.tag_sp_teste,
            asn=self.chamacoco,
            inner=1002,
            mlpav4_address=self.ipv4_cpv_test,
            customer_channel=self.customer_channel_chamacoco,
            shortname='as-' + str(self.chamacoco.number) + 'mlpav4',
            last_ticket='264')
        try:
            self.mlpv4_sp_test.save()
            pass
        except ValidationError:
            self.assertTrue(0, 'ASNs MAC blocked in distincts IX')

    def test_mac_by_as_by_customer_channel_limit(self):
        self.tag_cpv_teste = Tag.objects.create(
            tag='333',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_cpv_test = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        self.mlpv4_sp_test = MLPAv4.objects.create(
            tag=self.tag_cpv_teste,
            asn=self.metuktire,
            inner=1020,
            mlpav4_address=self.ipv4_cpv_test,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4',
            last_ticket='264')

        self.mac_address_cpv_test_1 = MACAddress.objects.create(
            address='45:b3:b7:25:3a:ff',
            last_ticket='2')

        self.mac_address_cpv_test_2 = MACAddress.objects.create(
            address='45:b3:b7:25:a3:ff',
            last_ticket='3')

        try:
            self.mlpv4_sp_test.mac_addresses.add(self.mac_address_cpv_test_1)
            self.mlpv4_sp_test.mac_addresses.add(self.mac_address_cpv_test_2)
            self.mlpv4_sp_test.save()
            # self.assertTrue(0, 'broken MAC limit by asn by customer channel')
        except ValidationError:
            pass

    def test_cix_type_zero_fail(self):
        # raise ValidationError with service from another
        # ASN in the same customer_channel
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
            name='ct-BE1090',
            last_ticket='663',
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_test)

        self.port_cpv_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test,
            physical_interface=None,
            name='TenGigE0/0/1/4',
            status='CUSTOMER',
            switch=self.extreme_pix_kapotnhinore,
            last_ticket='543')

        self.tag_cpv_teste = Tag.objects.create(
            tag='333',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_cpv_test = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        self.mlpv4_cpv_test = MLPAv4.objects.create(
            tag=self.tag_cpv_teste,
            asn=self.kayapo,
            mlpav4_address=self.ipv4_cpv_test,
            last_ticket='2121',
            customer_channel=self.customer_channel_kayapo,
            shortname='as-' + str(self.kayapo.number) + 'mlpav4')

        self.mlpv4_cpv_test.customer_channel = self.customer_channel_test
        with self.assertRaisesMessage(
            ValidationError,
                "Respective Customer Channel is a individual "
                "port and doesn't accept participants."):
            self.mlpv4_cpv_test.save()

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
            name='ct-BE1090',
            last_ticket='663',
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_test)

        self.port_cpv_test = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_test,
            physical_interface=None,
            name='TenGigE0/0/1/4',
            status='CUSTOMER',
            switch=self.extreme_pix_kapotnhinore,
            last_ticket='543')

        self.tag_cpv_teste = Tag.objects.create(
            tag='333',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_cpv_test = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        self.mlpv4_cpv_test = MLPAv4.objects.create(
            tag=self.tag_cpv_teste,
            asn=self.metuktire,
            mlpav4_address=self.ipv4_cpv_test,
            last_ticket='2121',
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4')

        self.mlpv4_cpv_test.save()

    def test_asn_ix_customer_channel_fail(self):
        # Try to create a service with different IX in the ASN.
        self.tag_cpv_teste = Tag.objects.create(
            tag='333',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        self.ipv4_cpv_test = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.6',
            last_ticket='2121',
            in_lg=False)

        with self.assertRaisesMessage(
            ValidationError,
                "This ASN doesn't belong to "
                "the same IX from customer channel."):
            self.mlpv4_cpv_test = MLPAv4.objects.create(
                tag=self.tag_cpv_teste,
                asn=self.chamacoco,
                mlpav4_address=self.ipv4_cpv_test,
                last_ticket='2121',
                customer_channel=self.customer_channel_kayapo,
                shortname='as-' + str(self.chamacoco.number) + 'mlpav4')

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
            self.mlpv4_cpv_test = MLPAv4.objects.create(
                tag=self.tag_cpv_teste,
                asn=self.chamacoco,
                mlpav4_address=self.ipv4_cpv_test,
                last_ticket='2121',
                customer_channel=self.customer_channel_test,
                shortname='as-' + str(self.chamacoco.number) + 'mlpav4')

    def test_post_delete_functions(self):
        self.customer = self.mlpv4_sp_kinikinau.customer_channel
        self.bilateral_sp_terena_kinikinau.delete()
        self.bilateral_peer_kinikinau.delete()
        for customer in CustomerChannel.objects.filter(asn=self.kinikinau):
            self.assertGreaterEqual(customer.mlpav4_set.all().count(), 1)
            for mlpav4 in customer.mlpav4_set.all():
                mlpav4.delete()
            self.assertEqual(customer.mlpav4_set.count(), 0)

    def test_get_related_service(self):
        self.assertEqual(self.mlpv4_cpv_kayapo.get_related_service(),
                         self.mlpv6_cpv_kayapo)

    def test_create_mlpav4_with_reserved_ipv4_to_fail(self):
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
            MLPAv4.objects.create(
                mlpav4_address=ipv4,
                customer_channel=self.customer_channel_metuktire,
                asn=self.metuktire,
                last_ticket='2121',
                tag=tag,
                shortname='mlpav4',
                status='QUARANTINE'
            )
