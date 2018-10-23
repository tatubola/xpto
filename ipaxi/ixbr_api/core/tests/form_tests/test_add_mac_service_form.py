# -*- coding: utf-8 -*-
from itertools import cycle
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...models import MLPAv4, MLPAv6, ASN, MACAddress, CustomerChannel
from ...forms import AddMACServiceForm
from ..login import DefaultLogin


class AddMACServiceFormTestCase(TestCase):

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
        asns = [20121, 26162]
        cixs_type = [0, 1]
        self.asns = mommy.make(
            ASN,
            number=cycle(asns),
            _quantity=len(asns))
        self.customers = mommy.make(
            CustomerChannel,
            asn=self.asns[0],
            cix_type=cycle(cixs_type),
            _quantity=len(cixs_type))
        self.mac = mommy.make(
            MACAddress,
            address='00:19:f9:aa:a2:59')
        self.service = mommy.make(
            MLPAv6,
            modified_by=self.superuser,
            customer_channel=self.customers[0],
            asn=self.asns[0])
        self.service_2 = mommy.make(
            MLPAv4,
            modified_by=self.superuser,
            asn=self.asns[1],
            customer_channel=self.customers[1])
        self.service_2.mac_addresses.add(self.mac.address)
        self.service_2.save()
        self.new_mac = '00:19:f9:aa:a2:57'
        self.mac_invalid_to_form = 'aabbcc3dddff'

    def test_template(self):
        request = self.client.get(reverse(
            "core:add_mac_service_form", args=[self.service.uuid]))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed('forms/create_mac_address_form.html')

    def test_add_mac_form_success(self):
        self.response = self.client.post(
            reverse('core:add_mac_service_form', args=[self.service.pk]),
            {'last_ticket': 1234,
             'address': self.new_mac,
             'description': 'Add Mac for service'})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('MAC registered', messages)

    def test_add_mac_form_failed_with_a_mac_already_registered(self):
        self.response = self.client.post(
            reverse('core:add_mac_service_form', args=[self.service.pk]),
            {'last_ticket': 1234,
             'address': self.mac.address,
             'description': 'Add Mac for service'})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('MAC is allocated in another asn', messages)

    def test_add_mac_form_when_form_is_invalid_to_form(self):
        form = AddMACServiceForm(
            data={
                'last_ticket': 1234,
                'address': 'aabbcc3dddff',
                'description': 'Add Mac for service'
            }
        )

        self.assertTrue(form.is_valid())

    def test_add_mac_form_when_form_not_have_a_vendor_associeted(self):
        self.response = self.client.post(
            reverse('core:add_mac_service_form', args=[self.service.pk]),
            {'last_ticket': 1234,
             'address': '012345678912',
             'description': 'Add Mac for service',
             'copy_mac': False})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('Vendor not Found', messages)
