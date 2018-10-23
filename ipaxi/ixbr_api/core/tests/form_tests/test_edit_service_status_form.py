# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import IX, MLPAv4, Tag
from ...forms import EditServiceStatusForm
from ..login import DefaultLogin


class EditServiceStatusFormTestCase(TestCase):
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

        self.ix = mommy.make(IX, code='ria')
        self.tag = mommy.make(Tag, ix=self.ix)
        self.mlpav4 = mommy.make(MLPAv4, tag=self.tag, status="ALLOCATED")

    def test_when_edit_service_tag_form_return_200_request_status_code(self):
        request = self.client.get(reverse(
            "core:edit_service_status_form", args=[self.mlpav4.uuid]))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/edit_service_status_form.html')

    def test_when_successfully_on_post(self):
        status = "QUARANTINE"
        response = self.client.post(reverse(
            "core:edit_service_status_form", args=[self.mlpav4.uuid]),
            {"status": status})
        self.assertEqual(response.status_code, 302)
        service = MLPAv4.objects.get(uuid=self.mlpav4.uuid)
        self.assertEqual(status, service.status)

    def test_when_edit_service_tag_form_is_invalid(self):
        form = EditServiceStatusForm(
            data={
                'status': 'not a valid status',
            }
        )
        self.assertFalse(form.is_valid())
