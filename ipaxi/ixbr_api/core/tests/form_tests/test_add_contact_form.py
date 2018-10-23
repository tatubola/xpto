# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import Contact, ContactsMap

from ...forms import AddContactForm
from ..login import DefaultLogin


class AddContactFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.contacts_map = mommy.make(ContactsMap)

        self.last_ticket = 2312
        self.name = 'Angelo Looser'
        self.email = 'angelo@nic.br'
        self.adm = True

    def test_to_return_status_code_200(self):
        request = self.client.get(
            reverse('core:add_contact_form', args=[self.contacts_map.uuid]))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/add_contact_form.html')

    def test_when_post_is_success(self):
        response = self.client.post(
            reverse('core:add_contact_form',
                    args=[self.contacts_map.uuid]),
            {'last_ticket': self.last_ticket,
             'name': self.name,
             'email': self.email,
             'adm': self.adm})
        self.assertEqual(response.status_code, 302)
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Contact saved', messages)

        new_contact_map = ContactsMap.objects.get(
            adm_contact=Contact.objects.get(name=self.name))
        self.assertEqual(new_contact_map.adm_contact.name, self.name)

    def test_when_form_is_invalid(self):
        form = AddContactForm(
            data={
                'last_ticket': 'not a ticket',
                'name': self.name,
                'email': self.email,
                'adm': self.adm
            }
        )
        self.assertFalse(form.is_valid())
