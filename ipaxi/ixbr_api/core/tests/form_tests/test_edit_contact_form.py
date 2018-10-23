# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...forms import EditContactForm
from ...models import ContactsMap
from ..login import DefaultLogin


class EditContactFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.contacts_map = mommy.make(ContactsMap)

    def test_edit_contact_form_return_200_status_code_on_get(self):
        request = self.client.get(reverse(
            "core:edit_contact_form",
            args=[self.contacts_map.noc_contact.uuid,
                  self.contacts_map.uuid,
                  "noc"]))

        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/edit_contact_form.html')

    def test_return_200_with_correct_parameters_on_post(self):
        name = 'Paulo Tigre'
        email = 'tigre@nic.br'
        response = self.client.post(reverse(
            "core:edit_contact_form",
            args=[self.contacts_map.noc_contact.uuid,
                  self.contacts_map.uuid,
                  "noc"]),
            {'name': name,
             'email': email,
             'last_ticket': 212347})
        self.assertEqual(response.status_code, 200)

        noc = ContactsMap.objects.get(uuid=self.contacts_map.uuid).noc_contact
        self.assertEqual(noc.name, name)
        self.assertEqual(noc.email, email)

    def test_when_form_is_invalid(self):
        name = 'Paulo Tigre'
        email = 'tigre@nic.br'
        form = EditContactForm(
            data={
                'last_ticket': 'not a ticket',
                'name': name,
                'email': email,
            }
        )
        self.assertFalse(form.is_valid())
