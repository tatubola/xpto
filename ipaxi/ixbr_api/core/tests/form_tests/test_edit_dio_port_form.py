# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import DIO, PIX, DIOPort, Port, Switch

from ..login import DefaultLogin


class EditDioPortFormViewTestCase(TestCase):
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

        self.pix = mommy.make(PIX, uuid="859cff08-f252-47cd-9473-999a541ddf96")
        self.switch_a = mommy.make(
            Switch,
            pix=self.pix,
            management_ip='186.221.58.10')
        self.switch_b = mommy.make(
            Switch,
            pix=self.pix,
            management_ip='186.221.58.11')
        self.port_a = mommy.make(
            Port, switch=self.switch_a, name='1', status='AVAILABLE')
        self.port_b = mommy.make(
            Port, switch=self.switch_a, name='2', status='AVAILABLE')
        self.port_c = mommy.make(
            Port, switch=self.switch_b, name='1', status='AVAILABLE')
        self.port_d = mommy.make(
            Port, switch=self.switch_b, name='2', status='RESERVED_INFRA')
        self.dio = mommy.make(DIO, pix=self.pix)

        self.dio_port_1 = mommy.make(
            DIOPort,
            dio=self.dio,
            switch_port=self.port_a,
            ix_position='rj12345678',
            datacenter_position='rj12345678',
            uuid='94e1536d-e136-42d5-86bd-8a1bc3535a98')

        self.dio_port_2 = mommy.make(
            DIOPort,
            dio=self.dio,
            switch_port=self.port_c,
            ix_position='rj87654321',
            datacenter_position='rj87654321',
            uuid='24e1536d-e136-42d5-86b3-8a1bc3535a97')

        self.request = self.client.get(
            reverse('core:edit_dio_port_form',
                    args=[
                        self.pix.uuid,
                        self.dio_port_1.uuid]))

        self.ix_position = 'ixposition/12'
        self.dc_position = 'datacenter/12'
        self.last_ticket = 1515

    def test_dio_port_edit_from_template(self):
        """Test that the DIOEditFormView returns a 200
        request, uses the correct template, and has the
        correct context.
        """
        self.assertEqual(200, self.request.status_code)
        self.assertTemplateUsed('forms/edit_dio_port_form.html')

    def test_dio_port_edit_from_context(self):
        """Test if the correct context is sent to the template"""
        dio_port_1 = self.request.context['dio_port']
        self.assertEqual(dio_port_1, self.dio_port_1.uuid)

        pix = self.request.context['pix']
        self.assertEqual(pix, self.pix.uuid)

    def test_dio_port_edit_success(self):
        """Test if success edition"""
        self.response = self.client.post(
            reverse('core:edit_dio_port_form',
                    args=[self.pix.uuid,
                          self.dio_port_1.uuid]),
            {'ix_position': self.ix_position,
             'dc_position': self.dc_position,
             'switch': self.switch_b.uuid,
             'ports': self.port_b.uuid,
             'last_ticket': self.last_ticket})
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('DIO Port saved', messages)

        dio_port_1 = DIOPort.objects.get(pk=self.dio_port_1.uuid)
        self.assertEqual(dio_port_1.ix_position, self.ix_position)
        self.assertEqual(dio_port_1.datacenter_position, self.dc_position)
        self.assertEqual(dio_port_1.switch_port_id, self.port_b.uuid)
        self.assertEqual(dio_port_1.last_ticket, self.last_ticket)

    def test_dio_port_edit_fail_ix_position(self):
        self.response = self.client.post(
            reverse('core:edit_dio_port_form',
                    args=[self.pix.uuid,
                          self.dio_port_2.uuid]),
            {'ix_position': 'rj12345678',
             'dc_position': self.dio_port_2.datacenter_position,
             'switch': self.switch_b.uuid,
             'ports': self.port_b.uuid,
             'last_ticket': self.last_ticket})
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('IX Position already exists', messages)

    def test_dio_port_edit_fail_datacenter_position(self):
        self.response = self.client.post(
            reverse('core:edit_dio_port_form',
                    args=[self.pix.uuid,
                          self.dio_port_2.uuid]),
            {'ix_position': self.dio_port_2.ix_position,
             'dc_position': 'rj12345678',
             'switch': self.switch_b.uuid,
             'ports': self.port_b.uuid,
             'last_ticket': self.last_ticket})
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Data center Position already exists', messages)

    def test_unique_switch_port(self):
        """ Test if a chosen port is removed after allocated to a DIO
        """
        response = self.client.get(
            reverse('core:edit_dio_port_form',
                    args=[self.pix.uuid,
                          self.dio_port_1.uuid]))

        available_ports = response.context['form'].fields['ports'].choices
        self.assertEqual(1, len(available_ports))

    def test_non_available_switch_port(self):
        response = self.client.get(
            reverse('core:edit_dio_port_form',
                    args=[self.pix.uuid,
                          self.dio_port_2.uuid]))

        available_ports = response.context['form'].fields['ports'].choices
        self.assertIn((str(self.port_d.uuid), self.port_d.name),
                      available_ports)
