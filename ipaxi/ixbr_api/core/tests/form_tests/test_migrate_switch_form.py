# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...forms import MigrateSwitchForm
from ...models import (PIX, Switch, SwitchModel)
from ..login import DefaultLogin


class MigrateSwitchFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_template_used(self, mock_full_clean, mock_signals):
        '''Test if GET request returns a response with status code 200
            and if the response uses the correct template.'''
        pix = mommy.make(PIX)
        request = self.client.get(
            reverse('core:migrate_switch_form',
                    kwargs={"pix": pix.uuid}))
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/migrate_switch_form.html')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_options_of_switches_are_correct(
            self, mock_full_clean, mock_signals):
        '''Test if only switches of correct PIX and with no uplink and core
            channel are returned in GET response.'''
        pix = mommy.make(PIX)
        switches = mommy.make(Switch, pix=pix, _quantity=3)

        # Switch that should not be displayed
        switch_from_another_pix = mommy.make(Switch)

        request = self.client.get(
            reverse('core:migrate_switch_form',
                    kwargs={"pix": pix.uuid}))

        option_string = "<option value=\"{uuid}\""
        for switch in switches:
            self.assertIn(option_string.format(uuid=switch.uuid),
                          str(request.content))

        self.assertNotIn(
            option_string.format(uuid=switch_from_another_pix.uuid),
            str(request.content))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_correct_post_returns_302(self, mock_full_clean, mock_signals):
        '''Test if POST request with correct parameters returns a response
            with status code of 302.'''
        pix = mommy.make(PIX)
        switch = mommy.make(Switch, pix=pix)
        model = mommy.make(SwitchModel)
        form = MigrateSwitchForm(
            data={
                'last_ticket': '10',
                'switch': switch.uuid,
                'new_model': model.uuid})
        request = self.client.post(
            reverse('core:migrate_switch_form',
                    kwargs={"pix": pix.uuid}),
            form.data)

        self.assertEqual(request.status_code, 302)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_post_with_incorrect_switch_returns_an_error(
            self, mock_full_clean, mock_signals):
        '''Test if POST request with incorrect switch returns an error. '''
        pix = mommy.make(PIX)
        mommy.make(Switch, pix=pix)
        switch_from_other_pix = mommy.make(Switch)
        model = mommy.make(SwitchModel)
        form = MigrateSwitchForm(
            data={
                'last_ticket': '10',
                'switch': switch_from_other_pix.uuid,
                'new_model': model.uuid})
        request = self.client.post(
            reverse('core:migrate_switch_form',
                    kwargs={"pix": pix.uuid}),
            form.data)

        messages = [m.message for m in get_messages(request.wsgi_request)]
        self.assertIn("Switches must be in the same pix", messages)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_post_with_correct_parameters_migrates_the_switch(
            self, mock_full_clean, mock_signals):
        '''Test if POST request with correct parameters migrates the switch.
        '''
        pix = mommy.make(
            PIX,
            ix__ipv4_prefix='10.0.0.0/22',
            ix__ipv6_prefix='2001:12f0::0/64')

        switch = mommy.make(Switch, pix=pix)
        model = mommy.make(SwitchModel)
        form = MigrateSwitchForm(
            data={
                'last_ticket': '10',
                'switch': switch.uuid,
                'new_model': model.uuid,
                'description': 'new description'})
        self.client.post(reverse('core:migrate_switch_form',
                         kwargs={"pix": pix.uuid}),
                         form.data)
        new_switch = Switch.objects.get(description='new description')
        self.assertEqual(Switch.objects.count(), 2)
        self.assertEqual(new_switch.model, model)
        self.assertEqual(new_switch.description, 'new description')
