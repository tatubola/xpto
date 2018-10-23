# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import MLPAv4
from ..login import DefaultLogin
from ...forms import EditServicePrefixLimitForm


class EditServicePrefixLimitFormViewTestCase(TestCase):
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

        self.service = mommy.make(MLPAv4, prefix_limit=100)

    def test_edit_service_prefix_limit_form_success_return_200_on_get(self):
        request = self.client.get(
            reverse('core:edit_service_prefix_limit_form',
                    args=[self.service.uuid]))
        self.assertEqual(request.status_code, 200)
        self.assertTrue(MLPAv4.objects.filter(uuid=self.service.uuid).exists())
        self.assertTrue(
            MLPAv4.objects.get(uuid=self.service.uuid).prefix_limit, 100)
        self.assertTemplateUsed('edit_service_prefix_limit_form.html')

    def test_when_edit_service_prefix_limit_success_return_302_on_post(self):
        response = self.client.post(
            reverse('core:edit_service_prefix_limit_form',
                    args=[self.service.uuid]),
            {'prefix_limit': 99})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            MLPAv4.objects.get(uuid=self.service.uuid).prefix_limit, 99)

    def test_when_edit_service_prefix_limit_form_is_invalid(self):
        form = EditServicePrefixLimitForm(
            data={
                'prefix_limit': -1,
            }
        )
        self.assertFalse(form.is_valid())
