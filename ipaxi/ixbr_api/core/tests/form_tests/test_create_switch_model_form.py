# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase

from ...forms import CreateSwitchModelForm
from ...models import SwitchModel
from ..login import DefaultLogin

from django.core.exceptions import ValidationError
from ...validators import INVALID_SWITCH_MODEL


class CreateSwitchModelFormTestCase(TestCase):
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
        request = self.client.get(
            reverse('core:create_switch_model_form'))
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/create_.html')
        self.assertTrue(request.context['form'].fields['description'])
        self.assertTrue(request.context['form'].fields['model'])
        self.assertTrue(request.context['form'].fields['vendor'])
        self.assertTrue(request.context['form'].fields['last_ticket'])

        self.assertTrue(request.context['form'].fields['capacity'])
        self.assertTrue(request.context['form'].fields['connector_type'])
        self.assertTrue(request.context['form'].fields['name_format'])
        self.assertTrue(request.context['form'].fields['begin'])
        self.assertTrue(request.context['form'].fields['end'])

        self.assertTrue(request.context['form'].fields['extra_ports'])
        self.assertTrue(request.context['form'].fields['capacity_extra'])
        self.assertTrue(request.context['form'].fields['connector_type_extra'])
        self.assertTrue(request.context['form'].fields['begin_extra'])
        self.assertTrue(request.context['form'].fields['end_extra'])

    def test_if_correct_post_returns_302(self):
        '''Test if POST request with correct parameters returns a response
            with status code of 302.'''

        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48
            }
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(
                'core:create_switch_model_form'),
            form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SwitchModel.objects.get(model=form.data['model']))
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Switch Model created successfully", messages)

    def test_add_switch_without_ports(self):

        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 0,
                'end': 0
            }
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(
                'core:create_switch_model_form'),
            form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SwitchModel.objects.get(model=form.data['model']))
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Switch Model created successfully", messages)

    def test_if_switch_model_form_fail(self):

        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': ''
            }
        )
        self.assertFalse(form.is_valid())

    def test_switch_model_add_with_invalid_vendor_model(self):
        mock_save_patcher = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.save')
        self.addCleanup(mock_save_patcher.stop)
        self.mock_save = mock_save_patcher.start()
        self.mock_save.reset_mock()
        self.mock_save.side_effect = ValidationError(INVALID_SWITCH_MODEL)

        self.response = self.client.post(
            reverse('core:create_switch_model_form'),
            {
                'description': 'None',
                'last_ticket': '10',
                'model': 'wrong_model',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48
            }
        )
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn(INVALID_SWITCH_MODEL, messages[0])

    def test_switch_model_add_with_invalid_capacity(self):
        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 73,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48
            }
        )
        self.assertFalse(form.is_valid())
        self.response = self.client.post(
            reverse('core:create_switch_model_form'),
            form.data
        )
        self.assertEqual(self.response.status_code, 200)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn(
            'Select a valid choice. 73 is not one of the available choices.',
            messages[0]['capacity']
        )

    def test_switch_model_with_extra_ports_valid(self):
        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48,
                'extra_ports': True,
                'capacity_extra': 1000,
                'connector_type_extra': 'SFP',
                'begin_extra': 49,
                'end_extra': 52,
            }
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(
                'core:create_switch_model_form'),
            form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SwitchModel.objects.get(model=form.data['model']))
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Switch Model created successfully", messages)

    def test_switch_model_with_extra_ports_fail_blank_fields(self):
        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48,
                'extra_ports': True,
            }
        )
        self.assertTrue(form.is_valid())
        self.response = self.client.post(
            reverse('core:create_switch_model_form'),
            form.data
        )
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn(
            'Extra ports begin must be greater than end field',
            messages
        )

    def test_switch_model_with_extra_ports_fail_begin_extra_conflit(self):
        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48,
                'extra_ports': True,
                'capacity_extra': 1000,
                'connector_type_extra': 'SFP',
                'begin_extra': 48,
                'end_extra': 52,
            }
        )
        self.assertTrue(form.is_valid())
        self.response = self.client.post(
            reverse('core:create_switch_model_form'),
            form.data
        )
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn(
            'Extra ports begin must be greater than end field',
            messages[0]
        )

    def test_switch_model_with_extra_ports_fail_same_capacity_and_connector_type(self):
        form = CreateSwitchModelForm(
            data={
                'description': 'None',
                'last_ticket': '10',
                'model': 'X910-72t',
                'vendor': 'EXTREME',
                'capacity': 1000,
                'connector_type': 'UTP',
                'name_format': '{0}',
                'begin': 1,
                'end': 48,
                'extra_ports': True,
                'capacity_extra': 1000,
                'connector_type_extra': 'UTP',
                'begin_extra': 49,
                'end_extra': 52,
            }
        )
        self.assertTrue(form.is_valid())
        self.response = self.client.post(
            reverse('core:create_switch_model_form'),
            form.data
        )
        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn(
            'Extra ports capacity and connector_type are equal to common ports',
            messages[0]
        )
