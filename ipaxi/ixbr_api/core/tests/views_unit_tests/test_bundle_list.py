# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import IXAPIQuerySet

from ..makefaketestdata import MakeFakeTestData


class BundleEthersViewTestCase(TestCase):
    def setUp(self):

        MakeFakeTestData.__init__(self)

        # Instance a Request Factory
        self.response = self.client.get(
            reverse('core:bundle_list', args=[self.sp.code]))

    def test_login(self):
        """ Check if is logged """
        self.assertTrue(self.login)

    def test_bundle_ethers_basics(self):
        """Test that the BundleEtherListView returns a 200
        response, uses the correct template, and has the
        correct context.
        """
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core/bundle-ethers.html')

    def test_bundle_ethers_return(self):
        ix_code = self.response.context['ix'].code
        self.assertEqual(ix_code, self.sp.code)
        bundle = self.response.context['bundle']
        self.assertIs(type(bundle), IXAPIQuerySet)
        self.assertEqual(
            bundle[0].name, self.downlink_channel_sp_kadiweu_1.name)
        self.assertEqual(
            bundle[1].name, self.downlink_channel_sp_kadiweu_2.name)
        self.assertEqual(
            bundle[2].name, self.downlink_channel_sp_kadiweu_3.name)
