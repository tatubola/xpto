# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...forms import EditContactsMapForm
from ...models import ContactsMap, IX, ASN
from ..login import DefaultLogin


class EditContactsMapFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.ix = mommy.make(IX, code='ria')
        self.asn = mommy.make(ASN, number=43222)
        self.contacts_map = mommy.make(ContactsMap, asn=self.asn, ix=self.ix)

    def test_edit_contacts_map_form_return_200_status_code_on_get(self):
        request = self.client.get(reverse(
            "core:edit_contacts_map_form",
            args=[self.contacts_map.uuid,
                  self.ix.code,
                  self.asn.number]))

        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/edit_contacts_map_form.html')

    def test_return_200_with_correct_parameters_on_post(self):
        self.assertNotEqual(
            self.contacts_map.noc_contact.uuid,
            self.contacts_map.adm_contact.uuid)

        response = self.client.post(reverse(
            "core:edit_contacts_map_form",
            args=[self.contacts_map.uuid,
                  self.ix.code,
                  self.asn.number]),
            {"last_ticket": 12313,
             "noc_contact": self.contacts_map.noc_contact.uuid,
             "adm_contact": self.contacts_map.noc_contact.uuid,
             "peer_contact": self.contacts_map.peer_contact.uuid,
             "com_contact": self.contacts_map.com_contact.uuid})

        self.assertEqual(response.status_code, 302)

        updated_contacts_map = ContactsMap.objects.get(
            uuid=self.contacts_map.uuid)

        self.assertEqual(
            updated_contacts_map.adm_contact.uuid,
            self.contacts_map.noc_contact.uuid)

    def test_when_form_is_invalid(self):
        form = EditContactsMapForm(
            data={
                "last_ticket": 23123,
                "noc_contact": self.contacts_map.noc_contact.uuid,
                "adm_contact": self.contacts_map.noc_contact.uuid,
                "peer_contact": 'not a uuid',
                "com_contact": self.contacts_map.com_contact.uuid
            }
        )

        self.assertFalse(form.is_valid())
