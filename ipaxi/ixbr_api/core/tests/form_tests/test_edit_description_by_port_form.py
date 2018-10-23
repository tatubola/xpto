# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import Port

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

        self.port = mommy.make(Port, name='1')

        self.request = self.client.get(
            reverse(
                'core:edit_description_by_port_form', args=[self.port.uuid]))

    def test_template_used(self):
        self.assertTemplateUsed('forms/edit_description_form.html')
        self.assertEqual(self.request.status_code, 200)

    def test_edit_description_by_port_form_success(self):
        self.response = self.client.post(
            reverse('core:edit_description_by_port_form',
                    args=[self.port.uuid]),
            {'description': 'Django is a high-level Python Web'
                            ' framework that encourages rapid testes sdfdsfn'})
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Description edited with success', messages)

    def test_edit_description_by_port_form_failed(self):
        self.response = self.client.post(
            reverse('core:edit_description_by_port_form',
                    args=[self.port.uuid]),
            {'description': 'Django is a high-level Python Web framework'
                            'that encourages rapid teste sdfdsfn fsdfsafas'})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('This form is invalid', messages)
