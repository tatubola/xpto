from itertools import cycle
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import BilateralPeer, ContactsMap, MLPAv4, MLPAv6

from ..login import DefaultLogin


class TestASIXDetailView(TestCase):
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

        self.contactsmap = mommy.make(
            ContactsMap, asn__number=2123, ix__code='rj')
        self.mlpav4 = mommy.make(
            MLPAv4,
            mlpav4_address__ix=self.contactsmap.ix,
            asn=self.contactsmap.asn,
            tag__tag=cycle([340, 342, 344, 345]),
            tag__ix=self.contactsmap.ix,
            _quantity=4)
        self.mlpav6 = mommy.make(
            MLPAv6,
            mlpav6_address__ix=self.contactsmap.ix,
            asn=self.contactsmap.asn,
            tag__tag=cycle([341, 343]),
            tag__ix=self.contactsmap.ix,
            _quantity=2)
        self.bilateral = mommy.make(
            BilateralPeer,
            asn=self.contactsmap.asn,
            tag__tag=346,
            tag__ix=self.contactsmap.ix)
        self.request = self.client.get(
            reverse("core:ix_as_detail", args=[
                self.contactsmap.ix.code,
                self.contactsmap.asn.number]))

    def test_as_ix_detail_basics(self):
        self.assertTemplateUsed('as/ix_as_detail.html')
        self.assertEqual(self.request.status_code, 200)

    def test_as_ix_detail_views_return(self):
            for item in ['asn',
                         'ix',
                         'channel_services',
                         'asn_pix_channels',
                         'organization_contacts',
                         'mlpav4_total',
                         'mlpav6_total',
                         'bilateral_total']:
                self.assertTrue(item in self.request.context.keys())

    def test_as_ix_detail_views_return_right_context(self):
        self.assertEqual(self.request.context['mlpav4_total'], 4)
        self.assertEqual(self.request.context['mlpav6_total'], 2)
        self.assertEqual(self.request.context['bilateral_total'], 1)
