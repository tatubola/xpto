# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase

from ...forms import CreateIXForm
from ...models import IX
from ..login import DefaultLogin

from django.core.exceptions import ValidationError


class CreateIXFormTestCase(TestCase):
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
        request = self.client.get(reverse('core:create_ix_form'))
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/create_.html')
        self.assertTrue(request.context['form'].fields['code'])
        self.assertTrue(request.context['form'].fields['shortname'])
        self.assertTrue(request.context['form'].fields['fullname'])
        self.assertTrue(request.context['form'].fields['ipv4_prefix'])
        self.assertTrue(request.context['form'].fields['ipv6_prefix'])
        self.assertTrue(request.context['form'].fields['management_prefix'])
        self.assertTrue(request.context['form'].fields['create_ips'])
        self.assertTrue(request.context['form'].fields['tags_policy'])
        self.assertTrue(request.context['form'].fields['last_ticket'])

    def test_create_ix_success_when_tags_policy_is_ix_managed(self):
        '''Test create an IX when tags policy is equal ix_managed.'''

        form = CreateIXForm(
            data={
                'code': 'sp',
                'last_ticket': '1234',
                'shortname': 'saopaulo.sp',
                'fullname': 'Sao Paulo - SPA',
                'ipv4_prefix': '187.16.195.0/24',
                'ipv6_prefix': '2001:12f8:0:18::/64',
                'management_prefix': '192.168.18.0/26',
                'create_ips': 'true',
                'tags_policy': 'ix_managed'
            }
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_ix_form'), form.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            True, IX.objects.get(code=form.data['code']).create_tags)
        self.assertEqual(
            True, IX.objects.get(code=form.data['code']).create_ips)
        self.assertTrue(IX.objects.get(code=form.data['code']))
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("IX created successfully", messages)

    def test_create_ix_success_when_tags_policy_is_distributed(self):
        '''Test create an IX when tags policy is equal distributed.'''

        form = CreateIXForm(
            data={
                'code': 'sp',
                'last_ticket': '1234',
                'shortname': 'saopaulo.sp',
                'fullname': 'Sao Paulo - SPA',
                'ipv4_prefix': '187.16.195.0/24',
                'ipv6_prefix': '2001:12f8:0:18::/64',
                'management_prefix': '192.168.18.0/26',
                'create_ips': 'false',
                'tags_policy': 'distributed'
            }
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_ix_form'), form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(IX.objects.get(code=form.data['code']))
        self.assertEqual(
            False, IX.objects.get(code=form.data['code']).create_tags)
        self.assertEqual(
            False, IX.objects.get(code=form.data['code']).create_ips)
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("IX created successfully", messages)

    def test_if_ix_form_fail(self):
        '''Test if IX form fail.'''

        form = CreateIXForm(
            data={
                'code': 'rj',
                'last_ticket': '1234',
                'shortname': 'riodejaneiro.rj',
                'fullname': 'Rio de Janeiro - RJA',
                'ipv4_prefix': '187.16.195.0/24',
                'ipv6_prefix': '2001:12f8:0:18::/64',
                'management_prefix': '',
                'create_ips': 'true',
                'tags_policy': 'ix_managed'
            }
        )
        self.assertFalse(form.is_valid())

    def test_invalid_management_ip(self):
        '''Test if management_ip is invalid.'''
        mock_save_patcher = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.save')
        self.addCleanup(mock_save_patcher.stop)
        self.mock_save = mock_save_patcher.start()
        self.mock_save.reset_mock()
        self.mock_save.side_effect = ValidationError(
            '192.168.190/26 does not appear to be an IPv4 or IPv6 network')
        form = CreateIXForm(
            data={
                'code': 'rj',
                'last_ticket': '1234',
                'shortname': 'riodejaneiro.rj',
                'fullname': 'Rio de Janeiro - RJA',
                'ipv4_prefix': '187.16.196.0/24',
                'ipv6_prefix': '2001:12f8:0:19::/64',
                'management_prefix': '192.168.190/26',
                'create_ips': 'true',
                'tags_policy': 'ix_managed'
            }
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_ix_form'), form.data)
        self.assertEqual(response.status_code, 200)
        messages = [
            m.message for m in get_messages(response.wsgi_request)]

        self.assertIn(
            '192.168.190/26 does not appear to be an IPv4 or IPv6 network',
            messages)
