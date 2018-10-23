# -*- coding: utf-8 -*-
from itertools import cycle
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...forms import EditPortPhysicalInterfaceForm
from ...models import PhysicalInterface, Port
from ..login import DefaultLogin


class EditPortPhysicalInterfaceFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        port_types = ["SFP"] * 3 + ["SFP+"]

        self.physical_interfaces = mommy.make(
            PhysicalInterface,
            port_type=cycle(port_types),
            connector_type='UTP',
            _quantity=4)
        self.ports = mommy.make(
            Port,
            _quantity=3,
            connector_type='UTP',
            physical_interface=cycle(self.physical_interfaces))

    def test_form_return_200_status_code_on_get(self):
        request = self.client.get(reverse(
            "core:edit_port_physical_interface_form",
            args=[self.ports[0].uuid]))

        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/edit_port_physical_interface_form.html')

    def test_when_response_is_success_on_post(self):
            response = self.client.post(reverse(
                "core:edit_port_physical_interface_form",
                args=[self.ports[0].uuid]),
                {"physical_interface": self.physical_interfaces[-1].uuid})
            self.assertEqual(response.status_code, 302)

            port = Port.objects.get(uuid=self.ports[0].uuid)
            self.assertEqual(
                port.physical_interface, self.physical_interfaces[-1])

    def test_when_form_is_invalid(self):
        form = EditPortPhysicalInterfaceForm(
            data={
                "physical_interface": 'not a valid physical interface'
            }
        )
        self.assertFalse(form.is_valid())
