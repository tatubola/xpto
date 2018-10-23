# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import ContactsMap, IX, PIX, Port

from ..login import DefaultLogin


class AddPixToAsnFormTestCase(TestCase):
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

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.ix = mommy.make(IX, code='ria')
        self.contacts_map = mommy.make(
            ContactsMap,
            asn__number=23124,
            ix=self.ix)
        self.pix = mommy.make(PIX, ix=self.ix)
        self.port = mommy.make(Port, switch__pix=self.pix, switch__model__vendor="EXTREME", name=1)

    def test_when_return_status_code_200_on_get(self):
        request = self.client.get(reverse(
            'core:add_pix_to_asn_form',
            args=[self.ix.code, self.contacts_map.asn.number]))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/add_pix_to_asn_form.html')

    def test_when_successfully_post(self):
        response = self.client.post(reverse(
            'core:add_pix_to_asn_form',
            args=[self.contacts_map.ix.code,
                  self.contacts_map.asn.number]),
            {'ticket': 23121,
             'pix': self.pix.uuid,
             'switch': self.port.switch.uuid,
             'channel_name': 'ct-1',
             'cix_type': 0,
             'ports': self.port.uuid,
             'asn': self.contacts_map.asn.number})
        self.assertEqual(response.status_code, 200)

        pix = PIX.objects.get(uuid=self.pix.uuid)
        self.assertIn(self.contacts_map.asn.number, pix.get_asns())
