# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import cycle
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ixbr_api.core.models import (IX, MLPAv4, Tag,
                                  CustomerChannel,
                                  Port, IPv4Address, IPv6Address)
from ...forms import EditServiceTagForm
from ..login import DefaultLogin


class EditServiceTagFormViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        tags = [17, 18, 19]
        status_tags = ['PRODUCTION', 'AVAILABLE', 'PRODUCTION']

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

        self.tags = mommy.make(
            Tag,
            ix=self.ix,
            tag=cycle(tags),
            status=cycle(status_tags),
            _quantity=len(tags))

        self.mlpav4 = mommy.make(
            MLPAv4,
            mlpav4_address=self.ipv4[0],
            tag=self.tags[0])

    def test_when_edit_service_tag_form_return_200_request_status_code(self):
        request = self.client.get(reverse(
            "core:edit_service_tag_form",
            args=[self.mlpav4.uuid, self.ix.code]))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/edit_service_tag_form.html')

    def test_when_successfully_on_post(self):
        response = self.client.post(reverse(
            "core:edit_service_tag_form",
            args=[self.mlpav4.uuid, self.ix.code]),
            {"tag": self.tags[1].tag})
        self.assertEqual(response.status_code, 302)
        service = MLPAv4.objects.get(uuid=self.mlpav4.uuid)
        self.assertEqual(self.tags[1], service.tag)

    def test_when_tag_production(self):
        response = self.client.post(reverse(
            "core:edit_service_tag_form",
            args=[self.mlpav4.uuid, self.ix.code]),
            {"tag": self.tags[2].tag})
        self.assertEqual(response.status_code, 302)
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(["['Tag status is PRODUCTION']"], messages)

    def test_when_edit_service_tag_form_is_invalid(self):
        form = EditServiceTagForm(
            data={
                'tag': -1,
            }
        )
        self.assertTrue(form.is_valid())

    def test_when_tag_is_4096(self):
        form = EditServiceTagForm(
            data={
                'tag': 4096,
            }
        )
        self.assertTrue(form.is_valid())
