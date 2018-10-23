# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...models import (MACAddress, MLPAv4,  MLPAv6)
from ..login import DefaultLogin


class DeleteMacAddressFormTest(TestCase):
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

    def test_delete_mac_associated_only_with_mlpav4_service(self):
        mac1 = mommy.make(MACAddress, address='00:19:f9:21:02:51')
        mac2 = mommy.make(MACAddress, address='00:19:f9:21:02:50')
        service = mommy.make(MLPAv4, modified_by=self.superuser)
        service.mac_addresses.add(mac1)
        service.mac_addresses.add(mac2)

        response = self.client.get('{0}?mac={1}&service={2}'.format(
            reverse('core:delete_mac_address_form'),
            mac1.address, service.uuid))

        self.assertEqual(response.status_code, 200)
        self.assertIn("Your MAC was deleted successfully",
                      str(response.content))

        self.assertEqual(service.mac_addresses.count(), 1)
        self.assertEqual(service.mac_addresses.first(), mac2)

        self.assertEqual(MACAddress.objects.count(), 1)
        self.assertEqual(MACAddress.objects.first(), mac2)

    def test_delete_mac_associated_with_multiple_services(self):
        mac1 = mommy.make(MACAddress, address='00:19:f9:21:02:51')
        mac2 = mommy.make(MACAddress, address='00:19:f9:21:02:50')
        mlpav4 = mommy.make(MLPAv4, modified_by=self.superuser)
        mlpav6 = mommy.make(MLPAv6, modified_by=self.superuser)

        mlpav4.mac_addresses.add(mac1)
        mlpav4.mac_addresses.add(mac2)
        mlpav6.mac_addresses.add(mac1)

        response = self.client.get('{0}?mac={1}&service={2}'.format(
            reverse('core:delete_mac_address_form'),
            mac1.address, mlpav4.uuid))

        self.assertEqual(response.status_code, 200)
        self.assertIn("Your MAC was deleted successfully",
                      str(response.content))

        self.assertEqual(mlpav4.mac_addresses.count(), 1)
        self.assertEqual(mlpav4.mac_addresses.first(), mac2)
        self.assertEqual(mlpav6.mac_addresses.count(), 1)
        self.assertEqual(mlpav6.mac_addresses.first(), mac1)

        self.assertEqual(MACAddress.objects.count(), 2)

    def test_passing_wrong_uuid(self):
        mac = mommy.make(MACAddress, address='00:19:f9:21:02:51')
        mlpav4 = mommy.make(MLPAv4, modified_by=self.superuser)
        mlpav6 = mommy.make(MLPAv6, modified_by=self.superuser)

        mlpav4.mac_addresses.add(mac)
        mlpav6.mac_addresses.add(mac)

        response = self.client.get('{0}?mac={1}&service={2}'.format(
            reverse('core:delete_mac_address_form'),
            mac.address, mac.uuid, mac.uuid))

        self.assertEqual(response.status_code, 200)
        self.assertIn("error",
                      str(response.content))
