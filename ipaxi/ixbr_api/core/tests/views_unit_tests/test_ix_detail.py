# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from itertools import cycle
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ...models import (ASN, IX, BilateralPeer, ChannelPort,
                       ContactsMap, CustomerChannel, IPv4Address,
                       IPv6Address, MLPAv4, MLPAv6, Port, Switch, Tag,)
from ..login import DefaultLogin


class IXDetailViewTestCase(TestCase):
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

        p = patch('ixbr_api.core.use_cases.tags_use_cases.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.ix = mommy.make(
            IX,
            code="sp")

        self.switch = mommy.make(
            Switch,
            management_ip='192.168.0.30',
            pix__ix=self.ix,)

        self.asnumber = [57976, 28571, 1200, 4587]
        self.asns = mommy.make(
            ASN,
            number=cycle(self.asnumber),
            _quantity=len(self.asnumber))

        self.contactsmap = mommy.make(
            ContactsMap,
            asn=cycle(self.asns),
            ix=self.ix,
            _quantity=4)

        self.channels_port = mommy.make(
            ChannelPort,
            create_tags=False,
            _quantity=2)

        self.port_customers = mommy.make(
            Port,
            switch=self.switch,
            name=seq(12),
            channel_port=self.channels_port[0],
            _quantity=2)

        self.customer_channel = mommy.make(
            CustomerChannel,
            name='ct-13',
            asn=self.asns[0],
            cix_type=1,
            channel_port=self.channels_port[0],
            is_mclag=True)

        # Crete tag
        status = ['PRODUCTION'] * 3 + ['AVAILABLE']
        self.tags = mommy.make(
            Tag,
            ix=self.ix,
            tag_domain=self.channels_port[1],
            status=cycle(status),
            _quantity=4)

        # IPv4 and IPv6
        self.ipv6_address = mommy.make(
            IPv6Address,
            ix=self.ix)

        self.ipv4_address = mommy.make(
            IPv4Address,
            ix=self.ix,
            address=seq('10.0.0.'),
            _quantity=3)

        # Tag attributes
        self.mlpv6_one = mommy.make(
            MLPAv6,
            tag=self.tags[0],
            asn=self.asns[0],
            mlpav6_address=self.ipv6_address,
            customer_channel=self.customer_channel)

        self.bilateral = mommy.make(
            BilateralPeer,
            tag=self.tags[-1],
            asn=self.asns[1],
            customer_channel=self.customer_channel)

        self.mlpv4_one = mommy.make(
            MLPAv4,
            tag=cycle(self.tags),
            asn=cycle(self.asns),
            mlpav4_address=cycle(self.ipv4_address),
            customer_channel=self.customer_channel,
            _quantity=3)

        self.port_master = self.customer_channel.get_master_port()

        self.response = self.client.get(
            reverse('core:ix_detail', args=[self.ix.code]))

    def test_template_used(self):
        self.assertTemplateUsed('core/ix_detail.html')
        self.assertEqual(self.response.status_code, 200)

    def test_ix_view_return(self):
        ix = self.response.context['ix']
        self.assertEqual(ix.code, self.ix.code)
        self.assertEqual(ix.management_prefix, self.ix.management_prefix)
        self.assertEqual(ix.ipv4_prefix, self.ix.ipv4_prefix)
        self.assertEqual(ix.ipv6_prefix, self.ix.ipv6_prefix)
        amount_production_tags = self.response.context['total_production_tags']
        self.assertEqual(amount_production_tags, 3)
        amount_available_tags = self.response.context['total_available_tags']
        self.assertEqual(amount_available_tags, 1)
        self.assertEqual(len(self.response.context['pixs']), 1)
        self.assertIs(type(self.response.context['cixs']), dict)
        self.assertEqual(len(self.response.context['cixs']), 1)
        self.assertEqual(
            self.response.context['asn_total'], len(self.asnumber))
        self.assertEqual(self.response.context['mlpav4_total'], 3)
        self.assertEqual(self.response.context['mlpav6_total'], 1)
        self.assertEqual(self.response.context['bilateral_total'], 1)

    def test_ix_detail_pix__ix_detail(self):
        c = Client()
        resp = c.generic(
            'GET', '{0}?pix={1}'.format(reverse('core:ix_detail_pix', args=[
                self.ix.code]), str(self.switch.pix.uuid)))
        context = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(context['asn_amount'], len(self.asnumber))
        self.assertEqual(context['mlpav4_amount'], 3)
        self.assertEqual(context['mlpav6_amount'], 1)
        self.assertEqual(context['bilateral_amount'], 1)
        self.assertEqual(
            context['switch_set']['0']['model'],
            self.switch.model.model)
        self.assertEqual(
            context['switch_set']['0']['management_ip'],
            self.switch.management_ip)

    def test_ix_detail_cix__ix_detail(self):
        c = Client()
        resp = c.generic(
            'GET', '{0}?uuid={1}'.format(reverse('core:ix_detail_cix', args=[
                self.ix.code]), str(self.customer_channel.uuid)))
        context_cix = json.loads(resp.content.decode('UTF-8'))
        self.assertEqual(context_cix['mlpav4_amount'], 3)
        self.assertEqual(context_cix['mlpav6_amount'], 1)
        self.assertEqual(context_cix['bilateral_amount'], 1)
        self.assertEqual(
            context_cix['switch_set']['0']['management_ip'],
            self.switch.management_ip)
        self.assertEqual(
            context_cix['port_master'],
            '{0}: {1}'.format(
                self.port_master.switch.management_ip, self.port_master.name))
        self.assertEqual(
            context_cix['lag'],
            {self.switch.management_ip:
                [port.name for port in self.customer_channel.get_ports()]})
