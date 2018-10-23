# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import ASN, IX, ContactsMap

from ..login import DefaultLogin


class AddIXtoASNFormViewTestCase(TestCase):
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

        self.ix_ria = mommy.make(IX, code='ria')
        self.ix_jpa = mommy.make(IX, code='jpa')
        self.asn = mommy.make(ASN, number=62000)
        self.contactsmap = mommy.make(
            ContactsMap,
            asn=self.asn,
            ix=self.ix_ria)

        self.request = self.client.get(
            reverse('core:add_ix_to_asn_form', args=[self.asn.number]))

    def test_template_used(self):
        self.assertTemplateUsed('forms/add_ix_to_asn.html')
        self.assertEqual(self.request.status_code, 200)

    def test_add_ix_to_asn_form_success(self):
        self.response = self.client.post(
            reverse('core:add_ix_to_asn_form',
                    args=[self.asn.number]),
            {'ticket': 12123,
             'ix': self.ix_jpa.code})
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('IX saved', messages)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.save')
    def test_add_ix_to_asn_form_failed(self, mock_save):
        mock_save.reset_mock()
        mock_save.side_effect = ValidationError(
            'ASN {} in IX {} already exists'.format(
                self.asn.number, self.ix_ria.code))
        self.response = self.client.post(
            reverse('core:add_ix_to_asn_form',
                    args=[self.asn.number]),
            {'ticket': 12123,
             'ix': self.ix_ria.code})
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('ASN 62000 in IX ria already exists', messages)
