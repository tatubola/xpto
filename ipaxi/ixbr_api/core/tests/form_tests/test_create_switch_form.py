# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...forms import CreateSwitchForm
from ...models import (PIX, Switch, SwitchModel, SwitchPortRange)
from ..login import DefaultLogin


class CreateSwitchFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.pix = mommy.make(PIX, ix__management_prefix="192.168.16.0/20")
        # IP prefix must not be generate with random string
        self.ix_object = self.pix.ix

    def test_template_used(self):
        '''Test if GET request returns a response with status code 200
        and if the response uses the correct template.'''
        request = self.client.get(
            reverse('core:create_switch_form',
                    args=[self.pix.uuid]))
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/create_switch_form.html')

        self.assertTrue(request.context['form'].fields['mgmt_ip'])
        self.assertTrue(request.context['form'].fields['last_ticket'])
        self.assertTrue(request.context['form'].fields['model'])
        self.assertTrue(request.context['form'].fields['translation'])

    def test_if_correct_post_returns_302(self):
        '''Test if POST request with correct parameters returns a response
            with status code of 302.'''

        p = patch('ixbr_api.core.models.Switch.objects.create')
        self.addCleanup(p.stop)
        p.start()

        switch_model = mommy.make(SwitchModel)
        model = mommy.make(SwitchPortRange, switch_model=switch_model)
        form = CreateSwitchForm(
            data={
                'mgmt_ip': '192.168.16.20',
                'last_ticket': '10',
                'model': model.switch_model.uuid,
                'is_pe': True,
                'translation': False,
                'create_ports': True}
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_switch_form',
                    args=[self.pix.uuid]),
            form.data)
        self.assertEqual(response.status_code, 302)
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Switch created successfully", messages)

    def test_if_post_with_incorrect_switch_switch_is_not_created(self):
        # IP prefix must not be generate with random string
        switch_model = mommy.make(SwitchModel)
        model = mommy.make(SwitchPortRange, switch_model=switch_model)
        nr_switches = Switch.objects.count()
        mgmt_ip = '1.1.1.1'
        form = CreateSwitchForm(
            data={
                'mgmt_ip': mgmt_ip,
                'last_ticket': '10',
                'model': model.switch_model.uuid,
                'is_pe': True,
                'translation': False,
                'create_ports': False}
        )
        err_message = "{} doesn't belong to network management IX: {}".format(
            mgmt_ip, self.ix_object.management_prefix)
        response = self.client.post(reverse(
            'core:create_switch_form', args=[self.pix.uuid]), form.data)

        self.assertEqual(Switch.objects.count(), nr_switches)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), err_message)

    def test_create_switch_without_ports(self):
        '''Test create a switch without ports.'''
        # IP prefix must not be generate with random string
        switch_model = mommy.make(SwitchModel)
        model = mommy.make(SwitchPortRange, switch_model=switch_model)
        form = CreateSwitchForm(
            data={
                'mgmt_ip': '192.168.16.20',
                'last_ticket': '10',
                'model': model.switch_model.uuid,
                'is_pe': True,
                'translation': False,
                'create_ports': False}
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_switch_form',
                    args=[self.pix.uuid]),
            form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Switch.objects.get(management_ip=form.data['mgmt_ip']))
        self.assertEqual(0, len(Switch.objects.get(
            management_ip=form.data['mgmt_ip']).port_set.all()))
        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Switch created successfully", messages)
