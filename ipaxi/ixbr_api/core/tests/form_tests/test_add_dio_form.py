# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import PIX

from ..login import DefaultLogin


class AddDioViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.PIX.objects.get')
        self.mock_pix = p.start()
        self.addCleanup(p.stop)

        self.pix = PIX(uuid='935a7a78-4eb3-407c-bea9-591d6f6593cd')
        self.mock_pix.return_value = self.pix

        self.response = self.client.get(
            reverse('core:add_dio_form',
                    kwargs={'pix': self.pix.uuid}))

    def test_add_dio_template(self):
        """Test that the AddDIOToPIXFormView returns a 200
        response, uses the correct template, and has the
        correct context.
        """
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core/add_dio_form.html')

    def test_add_dio_context(self):
        """Test if the correct context is sent to the template"""
        pix = self.response.context['pix']
        self.assertEqual(pix, self.pix)

    @patch('ixbr_api.core.models.DIO.objects.create')
    @patch('ixbr_api.core.use_cases.create_dio_ports_use_case.'
           'create_dio_ports')
    def test_add_dio(self, mock_dio_port, mock_dio):
        """Test if the form saves the DIO and creates the DIO ports"""
        last_ticket = 1
        dio_name = "DIO test name"
        number_of_ports = 10
        ix_position = "{0}123456789{1}"
        datacenter_position = "{0}123456789{1}"

        self.mock_pix.return_value = self.pix

        self.response = self.client.post(
            reverse('core:add_dio_form',
                    args=[self.pix.uuid]),
            {'last_ticket': last_ticket,
             'dio_name': dio_name,
             'number_of_ports': number_of_ports,
             'ix_position': ix_position,
             'datacenter_position': datacenter_position})

        self.assertEqual(mock_dio_port.call_count, 1)
        self.assertEqual(mock_dio.call_count, 1)
