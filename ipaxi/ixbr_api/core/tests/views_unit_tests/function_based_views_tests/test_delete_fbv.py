# -*- coding: utf-8 -*-
import json
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from model_mommy import mommy

from ....models import ContactsMap, MLPAv4, Tag
from ...login import DefaultLogin


class DeleteFBVTestCase(TestCase):

    def setUp(self):
        DefaultLogin.__init__(self)

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

        self.client = Client()

        self.tag = mommy.make(Tag)
        contacts_map = mommy.make(ContactsMap)

        self.mlpav4 = mommy.make(
            MLPAv4,
            tag=self.tag,
            make_m2m=True)
        self.mlpav4.asn.contactsmap_set.add(contacts_map)

    def test_delete_service(self):
        resp = self.client.generic(
            'POST',
            "{}".format(reverse("core:service_delete", args=[self.mlpav4.pk]),))
        self.assertEqual(resp.status_code, 200)

    def test_fail_with_message_to_delete_service(self):
        resp = self.client.generic(
            'POST',
            "{}".format(reverse("core:service_delete", args=[self.tag.pk]),))
        content = json.loads(resp.content.decode())
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(content['message'][0], 'Invalid service primary key')

    def test_fail_without_message_to_delete_service(self):
        resp = self.client.generic(
            'GET',
            "{}".format(reverse("core:service_delete", args=[self.mlpav4.pk]),))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b'')
