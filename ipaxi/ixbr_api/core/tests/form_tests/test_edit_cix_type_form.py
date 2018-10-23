# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...forms import EditCixTypeForm
from ...models import CustomerChannel
from ..login import DefaultLogin


class EditCixTypeFormFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.channel = mommy.make(
            CustomerChannel, cix_type=2, channel_port__create_tags=False)

    def test_edit_contacts_map_form_return_200_status_code_on_get(self):
        request = self.client.get(reverse(
            "core:edit_cix_type_form",
            args=[self.channel.uuid]))

        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('form/edit_cix_type_form.html')

    def test_return_200_with_correct_parameters_on_post(self):
        response = self.client.post(reverse(
            "core:edit_cix_type_form",
            args=[self.channel.uuid]),
            {"cix_type": 3})

        self.assertEqual(response.status_code, 302)
        updated_channel = CustomerChannel.objects.get(
            uuid=self.channel.uuid)
        self.assertEqual(updated_channel.cix_type, 3)

    def test_if_try_to_update_a_lower_cix_type(self):
        response = self.client.post(reverse(
            "core:edit_cix_type_form",
            args=[self.channel.uuid]),
            {"cix_type": 1})
        self.channel.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.channel.cix_type, 1)

    def test_test_when_form_is_invalid(self):
        form = EditCixTypeForm(
            data={
                'cix_type': 'not a choice'
            }
        )
        self.assertFalse(form.is_valid())
