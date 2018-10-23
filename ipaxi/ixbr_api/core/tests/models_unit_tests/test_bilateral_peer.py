from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import BilateralPeer, CustomerChannel, MACAddress, Tag
from ..makefaketestdata import MakeFakeTestData


class Test_Bilateral_Peer(TestCase):
    """Tests Bilateral_Peer model."""

    def setUp(self):
        MakeFakeTestData.__init__(self)

        self.bilateral_peer_yudja_2 = BilateralPeer.objects.create(
            asn=self.yudja,
            tag=self.tag_cpv_none_1,
            inner=1000,
            shortname='as{0}-bp'.format(self.yudja.number),
            customer_channel=self.customer_channel_yudja,
            last_ticket='1')

    def test__str__(self):
        self.assertEqual(
            str(self.bilateral_peer_yudja),
            "%s [%s AS%s %s:%s]" % (
                self.bilateral_peer_yudja.uuid,
                self.bilateral_peer_yudja.shortname,
                self.bilateral_peer_yudja.asn.number,
                self.bilateral_peer_yudja.tag,
                self.bilateral_peer_yudja.inner))

    def test_meta_verbose_name(self):
        self.assertEqual(
            str(BilateralPeer._meta.verbose_name), 'BilateralPeer')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(BilateralPeer._meta.verbose_name_plural), 'BilateralPeers')

    def test_unique_together(self):
        # unique_together = (('asn', 'tag', 'inner'),)
        # pix is the same?
        self.assertEqual(
            self.bilateral_peer_yudja.asn, self.bilateral_peer_yudja_2.asn)
        self.assertEqual(
            self.bilateral_peer_yudja.inner, self.bilateral_peer_yudja_2.inner)
        # if dio is the same, ix_position can't be the same
        self.bilateral_peer_yudja.tag = self.tag_cpv_none_1
        with self.assertRaisesMessage(
            ValidationError,
            'BilateralPeer with this Asn, '
                'Tag and Inner already exists.'):
            self.bilateral_peer_yudja.save()

    def test_meta_order_by(self):
        self.assertEqual(BilateralPeer.objects.all().ordered, True)
        self.assertEqual(str(BilateralPeer.objects.all()[
                         0]), str(self.bilateral_peer_yudja))
        self.assertEqual(str(BilateralPeer.objects.all()[
                         1]), str(self.bilateral_peer_yudja_2))
        self.assertEqual(str(BilateralPeer.objects.all()[
                         2]), str(self.bilateral_peer_kinikinau))
        self.assertEqual(str(BilateralPeer.objects.all()[
                         3]), str(self.bilateral_peer_chamacoco))
        self.assertEqual(str(BilateralPeer.objects.all()[
                         4]), str(self.bilateral_peer_terena))
        self.assertEqual(str(BilateralPeer.objects.all()[
                         5]), str(self.bilateral_peer_metuktire))
        self.assertEqual(str(BilateralPeer.objects.all()[
                         6]), str(self.bilateral_peer_kayapo))

    def test_simple_history(self):
        # is the last bilateral_peer_yudja in the historical table?
        self.assertEqual(self.bilateral_peer_yudja,
                         self.bilateral_peer_yudja.history.most_recent())
        self.bilateral_peer_yudja.description = 'my description'
        self.bilateral_peer_yudja.save()
        # is the last bilateral_yudja in the historical table?
        self.assertEqual(
            self.bilateral_peer_yudja.history.most_recent().description,
            'my description')
        # is the modified_by data field actually working?
        self.assertEqual(
            self.bilateral_peer_yudja.history.most_recent().modified_by,
            self.superuser)
        # is there three instances of bilateral_peer_yudja in the
        # historical table?
        # (Bilateral Peer Factory has a "POST GENERATION" function)
        self.assertEqual(self.bilateral_peer_yudja.history.count(), 2)

    def test_mac_by_service_limit(self):
        # test the limit of MAC Address allowed by bilateral_peer
        self.bilateral_peer_yudja.mac_addresses.add(self.mac_address_cpv_1)
        self.bilateral_peer_yudja.save()
        self.bilateral_peer_yudja.mac_addresses.add(self.mac_address_cpv_2)
        self.bilateral_peer_yudja.save()

        self.tag_cpv_none_2 = Tag.objects.create(
            tag='38',
            ix=self.cpv,
            status='AVAILABLE',
            last_ticket='2121')
        self.tag_cpv_none_3 = Tag.objects.create(
            tag='39',
            ix=self.cpv,
            status='AVAILABLE',
            last_ticket='2121')
        self.tag_cpv_none_4 = Tag.objects.create(
            tag='40',
            ix=self.cpv,
            status='AVAILABLE',
            last_ticket='2121')

        self.bilateral_peer_yudja_3 = BilateralPeer.objects.create(
            asn=self.yudja,
            tag=self.tag_cpv_none_2,
            inner=1000,
            shortname='as{0}-bp'.format(self.yudja.number),
            customer_channel=self.customer_channel_yudja,
            last_ticket='1')
        self.bilateral_peer_yudja_4 = BilateralPeer.objects.create(
            asn=self.yudja,
            tag=self.tag_cpv_none_3,
            inner=1001,
            shortname='as{0}-bp'.format(self.yudja.number),
            customer_channel=self.customer_channel_yudja,
            last_ticket='1')
        self.bilateral_peer_yudja_5 = BilateralPeer.objects.create(
            asn=self.yudja,
            tag=self.tag_cpv_none_4,
            inner=1001,
            shortname='as{0}-bp'.format(self.yudja.number),
            customer_channel=self.customer_channel_yudja,
            last_ticket='1')

        self.mac_addresses_test_1 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a1',
            last_ticket='3')
        self.mac_addresses_test_2 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a2',
            last_ticket='3')

        self.bilateral_peer_yudja.mac_addresses = set()
        self.bilateral_peer_yudja.mac_addresses.add(self.mac_address_cpv_2)
        self.bilateral_peer_yudja.save()
        self.bilateral_peer_yudja_3.mac_addresses.add(self.mac_address_cpv_1)
        self.bilateral_peer_yudja_3.save()
        self.bilateral_peer_yudja_4.mac_addresses.add(
            self.mac_addresses_test_1)
        self.bilateral_peer_yudja_4.save()
        self.bilateral_peer_yudja_5.mac_addresses.add(
            self.mac_addresses_test_2)
        self.bilateral_peer_yudja_5.save()
        self.bilateral_peer_yudja_2.mac_addresses.add(self.mac_address_cpv_3)
        with self.assertRaisesMessage(
            ValidationError,
                'Only 4 MACs by AS by Channel is allowed'):
            self.bilateral_peer_yudja_2.save()

    def test_mac_by_distinct_as(self):
        # test MAC in distinct AS in distinct IX
        self.mac_address_cpv_4 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:ab',
            last_ticket='222')
        self.new_tag_1 = Tag.objects.create(
            ix=self.cpv,
            tag='48',
            status='AVAILABLE',
            last_ticket='6634')
        self.new_tag_2 = Tag.objects.create(
            ix=self.sp,
            tag='47',
            status='AVAILABLE',
            last_ticket='223')
        self.bilateral_peer_terena.mac_addresses.add(self.mac_address_cpv_4)
        self.bilateral_peer_terena.save()
        self.bilateral_peer_kinikinau.mac_addresses.add(self.mac_address_cpv_4)
        try:
            self.bilateral_peer_kinikinau.save()
            self.assertTrue(0, 'Same MAC in distinct ASN')
        except ValidationError:
            pass
        self.mac_address_5 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:ac',
            last_ticket='3')
        self.bilateral_peer_h = BilateralPeer.objects.create(
            asn=self.kayapo,
            tag=self.new_tag_1,
            shortname='as{0}-bp'.format(self.kayapo.number),
            inner=1000,
            customer_channel=self.customer_channel_kayapo,
            last_ticket='1')
        self.bilateral_peer_h.mac_addresses.add(self.mac_address_5)
        self.bilateral_peer_i = BilateralPeer.objects.create(
            asn=self.terena,
            tag=self.new_tag_2,
            shortname='as{0}-bp'.format(self.terena.number),
            inner=1010,
            customer_channel=self.customer_channel_terena,
            last_ticket='1')
        self.bilateral_peer_i.mac_addresses.add(self.mac_address_5)
        try:
            self.bilateral_peer_h.save()
            self.bilateral_peer_i.save()
            pass
        except ValidationError:
            self.assertTrue(0, 'ASNs MAC blocked in distincts IX')

    def test_mac_by_as_by_customer_channel_limit(self):
        self.bilateral_peer_test = BilateralPeer.objects.create(
            asn=self.yudja,
            tag=self.tag_cpv_yudja,
            inner=1020,
            customer_channel=self.bilateral_peer_yudja.customer_channel,
            last_ticket='1',
            shortname='as{0}-bp'.format(self.yudja.number),)
        self.mac_new = MACAddress.objects.create(
            address='45:b3:b7:25:ee:b1', last_ticket='21')
        self.mac_niw = MACAddress.objects.create(
            address='45:b3:b7:25:ee:b2', last_ticket='21')
        try:
            self.bilateral_peer_test.mac_addresses.add(self.mac_new)
            self.bilateral_peer_test.mac_addresses.add(self.mac_niw)
            self.bilateral_peer_test.save()
            # self.assertTrue(0, 'broken MAC limit by asn by customer channel')
        except ValidationError:
            pass

    def test_post_delete_functions(self):

        self.assertGreaterEqual(self.yudja.contactsmap_set.all().count(), 1)

        self.customer = self.bilateral_peer_yudja.customer_channel
        self.bilateral_cpv_yudja_metuktire.delete()
        self.bilateral_peer_yudja.delete()

        for customer in CustomerChannel.objects.filter(asn=self.yudja):
            for monitor in customer.bilateralpeer_set.all():
                monitor.delete()
            customer.delete()
