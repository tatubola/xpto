# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import Contact, Phone

from ...forms import PhoneForm
from ..login import DefaultLogin


class AddPhoneFormViewTestCase(TestCase):
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

        self.contact = mommy.make(Contact)

        self.number = '+55 011 95485-5711'
        self.category = 'Mobile'
        self.last_ticket = 1212

    def test_when_page_status_code_return_200(self):
        self.request = self.client.get(
            reverse('core:add_phone_form', args=[self.contact.uuid]))
        self.assertEqual(200, self.request.status_code)
        self.assertTemplateUsed('forms/phone_edit_form.html')

    def test_when_form_is_valid_to_add_phone(self):

        self.response = self.client.post(
            reverse('core:add_phone_form', args=[self.contact.uuid]),
            {'phone': self.number,
             'category': self.category,
             'last_ticket': self.last_ticket})
        self.assertEqual(302, self.response.status_code)

        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Phone saved', messages)

        self.assertTrue(Phone.objects.get(number=self.number))

    def test_when_form_invalid_to_add_phone(self):
        form = PhoneForm(
            data={
                'phone': self.number,
                'category': 'Not a category',
                'last_ticket': 1231
            }
        )
        self.assertFalse(form.is_valid())
