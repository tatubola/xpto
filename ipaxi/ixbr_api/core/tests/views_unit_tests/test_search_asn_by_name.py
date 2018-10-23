# -*- coding: utf-8 -*-
from itertools import cycle
from unittest.mock import patch

from django.contrib.messages import get_messages

from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from ixbr_api.core.models import (Organization, ContactsMap, ASN)

from ..login import DefaultLogin


class SearchASNByNameTestCase(TestCase):
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

        self.name_search = 'mos'
        self.name_search_fail = 'b'

        self.names = ['Mosaico Telecom', 'Mosaico Tele']
        self.numbers = [20121, 69000]
        self.organizations = mommy.make(
            Organization,
            name=cycle(self.names),
            _quantity=2)
        self.asns = mommy.make(
            ASN,
            number=cycle(self.numbers),
            _quantity=2)
        mommy.make(
            ContactsMap,
            asn=cycle(self.asns),
            organization=cycle(self.organizations),
            _quantity=2)

    def test_search_asn_by_name_load_with_200_status_code(self):
        self.response = self.client.get(
            reverse('core:name_search'),
            {"name": self.name_search, "prev_path": "/core/"})
        self.assertEqual(self.response.status_code, 200)

    def test_search_asn_by_name_return_context(self):
        self.response = self.client.get(
            reverse('core:name_search'),
            {"name": self.name_search, "prev_path": "/core/"})

        self.organizations_dict = {
            self.organizations[0].name: [self.asns[0].number],
            self.organizations[1].name: [self.asns[1].number]

        }

        self.assertEqual(
            self.response.context[0]['name'], self.name_search)
        self.assertEqual(
            self.response.context[0]['organizations'], self.organizations_dict)
        self.assertEqual(
            self.response
            .context[0]['organizations'][self.organizations[0].name],
            self.organizations_dict[self.organizations[0].name])
        self.assertEqual(
            self.response
            .context[0]['organizations'][self.organizations[1].name],
            self.organizations_dict[self.organizations[1].name])

    def test_search_asn_by_name_fail(self):
        self.response = self.client.get(
            reverse('core:name_search'),
            {"name": self.name_search_fail, "prev_path": "/core/"})
        self.assertEqual(self.response.status_code, 302)

        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('b not found ', messages)
