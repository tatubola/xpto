# -*- coding: utf-8 -*-
import uuid
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...models import PIX, Switch
from ..login import DefaultLogin


class SearchUUIDTestCase(TestCase):
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

        pix = mommy.make(PIX)
        self.sw_uuid = uuid.UUID("7b2c3193-b7c0-4ee9-94e8-bf18270ce5ff")
        mommy.make(Switch, pix=pix, uuid=self.sw_uuid)
        self.search_uuid = "4ee9"
        self.search_uuid_fail = "abc123"

    def test_search_uuid_load_with_200_status_code(self):
        self.response = self.client.get(
            reverse('core:uuid_search'),
            {"uuid": self.search_uuid, "prev_path": "/core/"})
        self.assertEqual(self.response.status_code, 200)

    def test_search_uuid_template_used(self):
        self.response = self.client.get(
            reverse('core:uuid_search'),
            {"uuid": self.search_uuid, "prev_path": "/core/"})
        self.assertTemplateUsed('core/uuid_list.html')

    def test_search_uuid_fail(self):
        self.response = self.client.get(
            reverse('core:uuid_search'),
            {"uuid": self.search_uuid_fail, "prev_path": "/core/"})
        self.assertEqual(self.response.status_code, 302)

        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('abc123 not found', messages)
