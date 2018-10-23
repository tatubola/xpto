# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import Tag

from ..login import DefaultLogin


class AddPortToSwitchFormViewTestCase(TestCase):
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

        self.tag = mommy.make(Tag, tag=1)

        self.request = self.client.get(
            reverse(
                'core:edit_tag_description_form', args=[self.tag.uuid]))

    def test_template_used(self):
        self.assertTemplateUsed('forms/edit_description_form.html')
        self.assertEqual(self.request.status_code, 200)

    def test_tag_edit_description_form_success(self):
        self.response = self.client.post(
            reverse('core:edit_tag_description_form',
                    args=[self.tag.uuid]),
            {'description': 'Inserting tag description'})
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Description edited with success', messages)

    def test_tag_edit_description_form_failed(self):
        self.response = self.client.post(
            reverse('core:edit_tag_description_form',
                    args=[self.tag.uuid]),
            {'description': 'Inserting tag description with more than 80 characters to cause an exception and return a message error'})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('This form is invalid', messages)
