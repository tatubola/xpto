# -*- coding: utf-8 -*-
from itertools import cycle
import json
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ....models import (CustomerChannel, IPv4Address, IPv6Address,
                        IX, Port, Tag, MLPAv4, MLPAv6)
from ...login import DefaultLogin


class GetIPsAndTagsByIXTestCase(TestCase):

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

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.c = Client()

        self.ix = mommy.make(
            IX,
            tags_policy="ix_managed",
            create_tags=False,
            code="ria")
        self.customer_channel = mommy.make(CustomerChannel,)
        self.port = mommy.make(
            Port,
            switch__pix__ix=self.ix,
            channel_port=self.customer_channel.channel_port)
        self.ipv4 = mommy.make(
            IPv4Address,
            address=seq('187.16.193.'),
            ix=self.ix,
            _quantity=3)
        self.ipv6 = mommy.make(
            IPv6Address,
            ix=self.ix,
            address=seq("2001:12f8:0:16::"),
            _quantity=3)
        self.tags = mommy.make(Tag, _quantity=5, ix=self.ix, tag=seq(2))

        self.mlpav4 = mommy.make(
            MLPAv4,
            mlpav4_address=self.ipv4[0])

    def test_if_return_correct_IP_only_v4(self):
        resp = self.c.generic(
            'GET',
            "{}?option=only_v4&ix={}&channel={}".format(
                reverse("core:get_ips_and_tags_by_ix"),
                self.ix.code, self.customer_channel.uuid))

        context = json.loads(resp.content.decode('UTF-8'))
        self.assertFalse('ipv6' in context)
        self.assertEqual(context['ipv4'][0], self.ipv4[1].address)
        self.assertEqual(context['tag'][0], self.tags[0].tag)
        self.assertEqual(context['tag'][1], self.tags[1].tag)

    def test_if_return_correct_IP_only_v6(self):
        resp = self.c.generic(
            'GET',
            "{}?option=only_v6&ix={}&channel={}".format(
                reverse("core:get_ips_and_tags_by_ix"),
                self.ix.code, self.customer_channel.uuid))

        context = json.loads(resp.content.decode('UTF-8'))
        self.assertFalse('ipv4' in context)
        self.assertEqual(context['ipv6'][0], self.ipv6[0].address)
        self.assertEqual(context['tag'][0], self.tags[0].tag)
        self.assertEqual(context['tag'][1], self.tags[1].tag)

    def test_if_return_correct_IPs_v4_and_v6_with_v4_already_used(self):
        resp = self.c.generic(
            'GET',
            "{}?option=v4_and_v6&ix={}&channel={}".format(
                reverse("core:get_ips_and_tags_by_ix"),
                self.ix.code, self.customer_channel.uuid))

        context = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(context['ipv4'][0], self.ipv4[1].address)
        self.assertEqual(context['ipv6'][0], self.ipv6[1].address)
        self.assertEqual(context['tag'][0], self.tags[0].tag)
        self.assertEqual(context['tag'][1], self.tags[1].tag)
        self.assertEqual(
            context['cix_type'], self.customer_channel.cix_type)

    def test_if_return_correct_IPs_v4_and_v6_with_v6_already_used(self):
        self.mlpav6 = mommy.make(
            MLPAv6,
            mlpav6_address=cycle(self.ipv6),
            _quantity=2)
        resp = self.c.generic(
            'GET',
            "{}?option=v4_and_v6&ix={}&channel={}".format(
                reverse("core:get_ips_and_tags_by_ix"),
                self.ix.code, self.customer_channel.uuid))

        context = json.loads(resp.content.decode('UTF-8'))

        self.assertEqual(context['ipv4'][0], self.ipv4[2].address)
        self.assertEqual(context['ipv6'][0], self.ipv6[2].address)
        self.assertEqual(context['tag'][0], self.tags[0].tag)
        self.assertEqual(context['tag'][1], self.tags[1].tag)
        self.assertEqual(
            context['cix_type'], self.customer_channel.cix_type)

    def test_if_return_correct_tags(self):
        self.tags[0].status = "ALLOCATED"
        self.tags[0].save()
        resp = self.c.generic(
            'GET',
            "{}?option=v4_and_v6&ix={}&channel={}".format(
                reverse("core:get_ips_and_tags_by_ix"),
                self.ix.code, self.customer_channel.uuid))

        context = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(context['ipv4'][0], self.ipv4[1].address)
        self.assertEqual(context['ipv6'][0], self.ipv6[1].address)
        self.assertEqual(context['tag'][0], self.tags[1].tag)
        self.assertEqual(context['tag'][1], self.tags[2].tag)
        self.assertEqual(
            context['cix_type'], self.customer_channel.cix_type)
