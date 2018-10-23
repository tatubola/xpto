# -*- coding: utf-8 -*-
import json
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ....models import (ASN, IX, CustomerChannel, Port)
from ...login import DefaultLogin
from ....views.function_based_views import _build_channel_data


class GetCustomerChannelFormTestCase(TestCase):

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.create_all_ips')
        self.addCleanup(p.stop)
        p.start()

        p = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        self.addCleanup(p.stop)
        p.start()

        p = patch('ixbr_api.core.models.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

        # self.ix = mommy.make(
        #     IX,
        #     tags_policy="ix_managed",
        #     create_tags=False,
        #     code="ria")

        self.asn = mommy.make(ASN, number=62000)
        self.customer_channel = mommy.make(
            CustomerChannel,
            name='ct-1',
            asn=self.asn)

        # self.port = mommy.make(Port,)
        # self.switch = self.port.switch

    # def test_get_customer_channels_by_switch(self):
    #     request = self.client.generic(
    #         'GET',
    #         "{}?switch={}&asn={}".format(
    #             reverse("core:get_customer_channels_by_switch"),
    #             Switch.objects.first().pk,
    #             ASN.objects.first().pk))

    def test_build_channel_data(self):
        data = _build_channel_data(CustomerChannel.objects.filter(pk=self.customer_channel.pk))
        channels_list = data['channels_list']

        self.assertIn(self.customer_channel.name, channels_list[str(self.customer_channel.pk)])
        self.assertIn(str(self.customer_channel.asn_id), channels_list[str(self.customer_channel.pk)])
