# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import PhysicalInterface
from ...utils.constants import CONNECTOR_TYPES, PORT_TYPES

from ..login import DefaultLogin


class CreatePortPhysicalInterfaceFormTest(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

    def test_create_port_physical_interface_template(self):
        """Test that the CreatePortPhysicalInterfaceFormView returns a 200
        response, uses the correct template, and has the correct context.
        """
        self.response = self.client.get(reverse(
            'core:create_port_physical_interface_form'))
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed(
            'forms/create_port_physical_interface_form.html')

    @patch('ixbr_api.core.views.form_views.PhysicalInterface.objects.create')
    def test_create_port_physical_interface_successfully(
        self, mock_create_physical_interface
    ):
        connector_type = CONNECTOR_TYPES[0][0]
        last_ticket = 1
        port_type = PORT_TYPES[0][0]
        serial_number = "abc123"
        self.response = self.client.post(
            reverse('core:create_port_physical_interface_form'),
            {
                'connector_type': connector_type,
                'last_ticket': last_ticket,
                'serial_number': serial_number,
                'port_type': port_type,
            }
        )
        mock_create_physical_interface.assert_called_with(
            connector_type=connector_type,
            last_ticket=last_ticket,
            modified_by=self.superuser,
            port_type=port_type,
            serial_number=serial_number,
        )
        self.assertEqual(mock_create_physical_interface.call_count, 1)
