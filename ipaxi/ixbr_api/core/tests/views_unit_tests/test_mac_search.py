# -*- coding: utf-8 -*-
from unittest.mock import patch
from itertools import cycle


from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy
from model_mommy.recipe import seq

from ixbr_api.core.models import (ASN, Bilateral, CustomerChannel,
                                  IX, MACAddress, MLPAv4, Port, Tag,)

from ..login import DefaultLogin


class MACSearchViewTestCase(TestCase):
    def setUp(self):
        # Log into application
        DefaultLogin.__init__(self)

        # patch method get_object_or_404 used in ASSearchView
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

        self.ix = mommy.make(IX, code='rj')
        self.asn = mommy.make(ASN, number=2222)
        self.mac = mommy.make(MACAddress, address='00:19:f9:aa:a2:52')
        self.tags = mommy.make(Tag, tag=seq(4), ix=self.ix, _quantity=3)
        self.customer_channel = mommy.make(CustomerChannel, asn=self.asn)
        self.port = mommy.make(
            Port,
            switch__model__vendor="BROCADE",
            switch__pix__ix=self.ix,
            channel_port=self.customer_channel.channel_port)
        self.service = mommy.make(
            MLPAv4,
            tag=self.tags[2],
            asn__number=self.asn.number,
            customer_channel=self.customer_channel)
        self.service.mac_addresses.add(self.mac.address)
        self.bilateral = mommy.make(
            Bilateral, peer_a__asn=self.asn,
            peer_a__tag=cycle(self.tags),
            peer_a__customer_channel=self.customer_channel,
            _quantity=2)
        self.bilateral[0].peer_a.mac_addresses.add(self.mac.address)
        self.bilateral[1].peer_a.mac_addresses.add(self.mac.address)

    def test_template_used(self):
        request = self.client.get(
            reverse('core:mac_search', args=[self.ix.code]),
            {'mac': self.mac.address})
        self.assertTemplateUsed('core/mac_search_result.html')
        self.assertEqual(request.status_code, 200)

    def test_tag_search_load_with_200_status_code(self):
        request = self.client.get(
            reverse('core:mac_search', args=[self.ix.code]),
            {'mac': self.mac.address})
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('core:tag_search_result.html')
        self.assertEqual(request.context[0]['mac'], self.mac)
        self.assertEqual(request.context[0]['ix'], self.ix)
        self.assertEqual(request.context[0]['services'][0], self.service)
        self.assertEqual(request.context[0]['bilateral']['owner'],
                         self.asn.number)
        self.assertEqual(request.context[0]['bilateral']['pix'],
                         self.port.switch.pix.code)
        self.assertEqual(request.context[0]['bilateral']['service_type'],
                         self.bilateral[0].peer_a.get_service_type())
        self.assertEqual(request.context[0]['bilateral']['switch_uuid'],
                         self.port.switch.uuid)
        self.assertEqual(request.context[0]['bilateral']['tags'],
                         [self.tags[0].tag, self.tags[1].tag])
        self.assertEqual(request.context[0]['bilateral']['port'],
                         self.port.__str__())
