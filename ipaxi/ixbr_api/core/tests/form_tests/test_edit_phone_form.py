# -*- coding: utf-8 -*-
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import Phone

from ...forms import PhoneForm
from ..login import DefaultLogin


class EditPhoneFormViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        self.old_number = '11 55093500'

        self.phone = mommy.make(
            Phone,
            number=self.old_number,
            category='Business', )

        self.request = self.client.get(
            reverse('core:edit_phone_form', args=[self.phone.uuid]))

        self.new_number = '11 945842548'
        self.category = 'Mobile'
        self.last_ticket = '15452'

    def test_template_used(self):
        self.assertEqual(200, self.request.status_code)
        self.assertTemplateUsed('forms/edit_phone_form.html')

    def test_phone_edit_form_success_return_200(self):
        self.response = self.client.post(
            reverse('core:edit_phone_form',
                    args=[self.phone.uuid]),
            {'phone': self.new_number,
             'category': self.category,
             'last_ticket': self.last_ticket})

        self.assertEqual(200, self.request.status_code)

        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Phone saved', messages)

        self.assertTrue(Phone.objects.get(number=self.new_number))
        self.assertFalse(Phone.objects.filter(number=self.old_number).exists())

    def test_when_form_is_invalid(self):
        form = PhoneForm(
            data={
                'category': 'not valid',
                'last_ticket': 12313,
                'number': self.new_number
            }
        )
        self.assertFalse(form.is_valid())
