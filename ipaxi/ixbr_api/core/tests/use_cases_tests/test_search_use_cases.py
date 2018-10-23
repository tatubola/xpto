from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import (CustomerChannel, MLPAv4, MLPAv6, BilateralPeer, Monitorv4, MACAddress)
from ...use_cases.search_use_cases import (search_customer_channel_by_mac_address)
from ...use_cases.mac_address_converter_to_system_pattern import (
    MACAddressConverterToSystemPattern,)
from ..login import DefaultLogin


class TestSearchUseCases(TestCase):

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

    def test_search_customer_channel_by_mac_address_mlpav4_service_case(self):
        address_string = '1B:D8:EE:AC:40:5F'
        mac = mommy.make(
            MACAddress,
            address=address_string)

        channel = mommy.make(CustomerChannel)

        mlpav4 = mommy.make(
            MLPAv4,
            customer_channel=channel,
            mac_addresses=[mac])

        search_result = search_customer_channel_by_mac_address(
            address=address_string)

        self.assertIn(channel, search_result)

    def test_search_customer_channel_by_mac_address_bilateralpeer_service_case(self):
        address_string = '1B:D8:EE:AC:40:5F'
        mac = mommy.make(
            MACAddress,
            address=address_string)

        channel = mommy.make(CustomerChannel)

        bilateral = mommy.make(
            BilateralPeer,
            customer_channel=channel,
            mac_addresses=[mac])

        search_result = search_customer_channel_by_mac_address(
            address=address_string)

        self.assertIn(channel, search_result)

    def test_search_customer_channel_by_mac_address_not_find_case(self):
        address_string = '1B:D8:EE:AC:40:5F'

        channel = mommy.make(CustomerChannel)

        search_result = search_customer_channel_by_mac_address(
            address=address_string)

        self.assertNotIn(channel, search_result)

    def test_search_customer_channel_by_mac_address_mac_converter_case(self):
        address_string = MACAddressConverterToSystemPattern(
            '1B:D8:EE:AC:40:5F').mac_address_converter()
        mac = mommy.make(
            MACAddress,
            address=address_string)

        channel = mommy.make(CustomerChannel)

        mlpav4 = mommy.make(
            MLPAv4,
            customer_channel=channel,
            mac_addresses=[mac])

        search_result = search_customer_channel_by_mac_address(
            address=address_string)

        self.assertIn(channel, search_result)