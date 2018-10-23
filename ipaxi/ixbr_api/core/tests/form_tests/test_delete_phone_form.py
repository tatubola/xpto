# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import Phone

from ..login import DefaultLogin


class DeletePhoneViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        self.number = '11 55093500'

        self.phone = mommy.make(
            Phone,
            number=self.number,
            category='Business')

    def test_when_delete_phone_is_successful(self):
        self.assertTrue(Phone.objects.filter(number=self.number).exists())
        self.response = self.client.get(
            reverse('core:delete_phone_form', args=[self.phone.uuid]))
        self.assertFalse(Phone.objects.filter(number=self.number).exists())
        self.assertIn(
            'Phone was deleted successfully',
            self.response.content.decode("utf-8"))
