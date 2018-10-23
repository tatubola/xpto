# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy


from ixbr_api.core.models import Port
from ...utils.constants import CAPACITIES_CONF

from ..login import DefaultLogin


class EditConfiguredCapacityPortFormTest(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.port = mommy.make(Port, configured_capacity=100, capacity=40000)

    def test_edit_configured_capacity_port_template(self):
        """Test that the EditConfiguredCapacityPortFormView returns a 200
        response, uses the correct template
        """
        response = self.client.get(
            reverse('core:edit_port_configured_capacity_form',
                    kwargs={'port': self.port.uuid}))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            'forms/edit_port_configured_capacity_form.html')

    def test_edit_configured_capacity_port_context(self):
        """Test that the EditConfiguredCapacityPortFormView has the correct
        context.
        """
        response = self.client.get(
            reverse('core:edit_port_configured_capacity_form',
                    kwargs={'port': self.port.uuid}))

        configured_capacity_choices = response.context['form'].\
            fields['configured_capacity'].choices
        selected_configured_capacity = response.context['form'].\
            fields['configured_capacity'].initial

        response.context['form'].fields['configured_capacity'].initial
        self.assertEqual(set(configured_capacity_choices),
                         set(CAPACITIES_CONF[0:4]))
        self.assertEqual(selected_configured_capacity,
                         self.port.configured_capacity)
        self.assertEqual(response.context['port'], str(self.port.uuid))

    def test_edit_configured_capacity_port_successfully(self):
        """Test that the EditConfiguredCapacityPortFormView edit the port
           configured capacity  successfully
        """
        last_ticket = 1
        configured_capacity = 1000

        self.client.post(
            reverse('core:edit_port_configured_capacity_form',
                    args=[self.port.uuid]),
            {'last_ticket': last_ticket,
             'configured_capacity': configured_capacity})
        self.port = Port.objects.get(pk=self.port.uuid)
        self.assertEqual(self.port.configured_capacity, configured_capacity)
        self.assertEqual(self.port.last_ticket, last_ticket)
