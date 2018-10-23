# -*- coding: utf-8 -*-
from itertools import cycle
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ixbr_api.core.models import (ASN, IX, PIX, ChannelPort, ContactsMap,
                                  Port, Switch, SwitchModel,)

from ...forms import AddCustomerChannelForm
from ..login import DefaultLogin


class AddCustomerChannelFormViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.create_all_ips')
        self.addCleanup(p.stop)
        p.start()

        p = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        self.addCleanup(p.stop)
        p.start()

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.ix = mommy.make(
            IX,
            code='sp')

        self.pix = mommy.make(
            PIX,
            ix=self.ix)

        self.asn = mommy.make(
            ASN,
            number=20121)

        self.contactsmap = mommy.make(
            ContactsMap,
            asn=self.asn,
            ix=self.ix)

        self.models = ['[X460-48t]', '[X670-72x]']

        self.switch_models = mommy.make(
            SwitchModel,
            model=cycle(self.models),
            vendor='EXTREME',
            _quantity=len(self.models))

        self.switchs = mommy.make(
            Switch,
            pix=self.pix,
            model=cycle(self.switch_models),
            management_ip=seq('192.168.28.'),
            _quantity=2)

        self.channel_port_customer = mommy.make(
            ChannelPort,
            create_tags=False)

        self.ports = mommy.make(
            Port,
            switch=cycle(self.switchs),
            name=seq('1'),
            channel_port=self.channel_port_customer,
            _quantity=len(self.switchs))

        self.ticket = 1234
        self.channel_name = 'ct-1'
        self.cix_type = 0

    def test_customer_channel_add_form_when_status_code_200_and_context(self):
        """Test that the AddCustomerChannelFormView returns a 200
        request, uses the correct template, and has the
        correct context.
        """
        request = self.client.get(
            reverse('core:add_customer_channel_form',
                    args=[
                        self.asn.number,
                        self.pix.uuid]))

        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/add_customer_channel_form.html')

        self.assertEqual(int(request.context['asn']), self.asn.number)

        pix = request.context['pix']
        self.assertEqual(pix, str(self.pix.uuid))

        self.switch_list = ()
        for switch in self.switchs:
            self.switch_list += (
                (switch.pk, switch.management_ip),
            )

        switch = request.context['switch']

        self.assertEqual(self.switch_list, switch)

    def test_customer_channel_add_form_context_with_switch_huawei(self):
        """Test that the AddCustomerChannelFormView returns a 200 request,
        uses the correct template, and has the correct context and the first
        switch is a Huawei, must contains 'ct-Trunk' on suggestion channel name.
        """
        mommy.make(
            Switch,
            pix=self.pix,
            model__vendor='HUAWEI',
            management_ip=seq('192.168.1.'),)

        request = self.client.get(
            reverse('core:add_customer_channel_form',
                    args=[self.asn.number, self.pix.uuid]))

        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/add_customer_channel_form.html')

        # request._container[0] is where the form is rendered
        self.assertIn(b'Trunk', request._container[0])

    def test_customer_channel_add_form_success(self):
        """Test if success addition"""
        self.response = self.client.post(
            reverse('core:add_customer_channel_form',
                    args=[self.asn.number,
                          self.pix.uuid]),
            {'ticket': self.ticket,
             'pix': self.pix.uuid,
             'switch': self.switchs[0].uuid,
             'channel_name': self.channel_name,
             'cix_type': self.cix_type,
             'ports': [self.ports[1].uuid],
             'asn': self.asn.number})

        self.assertTemplateUsed('forms/modal_feedback_service.html')

        message = self.response.context['message']
        self.assertEqual(message, 'success')

    def test_add_customer_channel_form_fail(self):
        """Test if fail addition"""
        form = AddCustomerChannelForm(
            data={
                'ticket': self.ticket,
                'pix': self.pix.uuid,
                'switch': self.switchs[0].uuid,
                'channel_name': '',
                'cix_type': self.cix_type,
                'ports': [self.ports[1].uuid],
                'asn': self.asn.number
            }
        )
        self.assertFalse(form.is_valid())
