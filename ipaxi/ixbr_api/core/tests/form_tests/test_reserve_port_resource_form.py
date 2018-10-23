# -*- coding: utf-8 -*-
from itertools import cycle
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy


from ...models import Switch, Port
from ..login import DefaultLogin


class ReservePortResourceFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.switch = mommy.make(
            Switch,
            management_ip='192.168.16.2',
            create_ports=False)

        ports_list = ['1', '2', '3']
        ports_status = ['AVAILABLE', 'AVAILABLE', 'CUSTOMER']

        self.ports = mommy.make(
            Port,
            switch=self.switch,
            name=cycle(ports_list),
            status=cycle(ports_status),
            channel_port=None,
            _quantity=len(ports_list))

    def test_template(self):
        request = self.client.get(reverse(
            "core:reserve_port_resource", args=[self.switch.uuid]))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/reserve_port_resource.html')

    def test_reverse_port_resource_form_success(self):
        self.response = self.client.post(
            reverse('core:reserve_port_resource', args=[self.switch.pk]),
            {'ports_to_reserve': [self.ports[0].uuid, self.ports[1].uuid]})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Port(s) Reserved', messages)

    @patch('ixbr_api.core.models.ReservableModel.reserve_this')
    def test_reverse_port_resource_form_fail(self, mock_save):
        mock_save.reset_mock()
        mock_save.side_effect = ValidationError(
            'Change Channel port if Status is not "Available".')
        self.response = self.client.post(
            reverse('core:reserve_port_resource', args=[self.switch.pk]),
            {'ports_to_reserve': [self.ports[2].uuid]})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn(
            'Change Channel port if Status is not "Available".', messages)
