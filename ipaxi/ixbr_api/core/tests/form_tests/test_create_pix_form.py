# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy
from django.core.exceptions import ValidationError

from ...forms import CreatePixForm
from ...models import (IX, PIX)
from ..login import DefaultLogin


class CreatePixFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

    def test_template_used(self):
        '''Test if GET request returns a response with status code 200
        and if the response uses the correct template.'''
        ix = mommy.make(IX, code='ria')
        request = self.client.get(reverse('core:create_pix_form',
                                          args=[ix.code]))
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/create_pix_form.html')
        self.assertTrue(request.context['form'].fields['description'])
        self.assertTrue(request.context['form'].fields['code'])
        self.assertTrue(request.context['form'].fields['last_ticket'])

    def test_if_correct_post_returns_302(self):
        '''Test if POST request with correct parameters returns a response
            with status code of 302.'''
        ix = mommy.make(IX, code='ria')

        form = CreatePixForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'code': 'TIETE',
                'ix': ix}
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_pix_form',
                    args=[ix.code]),
            form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PIX.objects.get(code=form.data['code']))
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("PIX created successfully", messages)
