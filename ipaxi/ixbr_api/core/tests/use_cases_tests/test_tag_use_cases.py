from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import (IX, BilateralPeer, CustomerChannel, DownlinkChannel,
                       MLPAv4, Port, Switch, Tag, UplinkChannel, User)
from ...use_cases.tags_use_cases import (check_inner_tag_availability,
                                         get_available_inner_tag,
                                         get_free_tags,
                                         get_or_create_specific_tag_without_all_service,
                                         get_or_create_specific_tag_without_bilateral,
                                         get_tag_without_all_service,
                                         get_tag_without_bilateral,
                                         instantiate_tag)


class TagUseCasesTest(TestCase):

    def setUp(self):

        self.user = User.objects.get_or_create(
            name='testuser', email="testuser@nic.br", password="testuser")[0]
        patcher = patch('ixbr_api.core.models.get_current_user')
        self.addCleanup(patcher.stop)

        self.get_user_mock = patcher.start()
        self.get_user_mock.return_value = self.user

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

        self.ix = mommy.make(
            IX,
            tags_policy='distributed',
            create_tags=False)

        self.origin_switch = mommy.make(
            Switch,
            pix__ix=self.ix)
        self.neighboor_middle = mommy.make(
            Switch,
            pix__ix=self.ix)
        self.neighboor_end = mommy.make(
            Switch,
            pix__ix=self.ix,
            is_pe=True)

        self.blocking_switch = mommy.make(
            Switch,
            pix__ix=self.ix,
            is_pe=True)

        self.downlink_block = mommy.make(DownlinkChannel)

        self.downlink_middle = mommy.make(DownlinkChannel)
        self.uplink_origin = mommy.make(UplinkChannel,
                                        downlink_channel=self.downlink_middle)

        self.downlink_end = mommy.make(DownlinkChannel)
        self.uplink_middle = mommy.make(UplinkChannel,
                                        downlink_channel=self.downlink_end)

        self.port_origin = mommy.make(Port,
                                      switch=self.origin_switch,
                                      channel_port=self.uplink_origin.channel_port)

        self.port_middle_down = mommy.make(Port,
                                           switch=self.neighboor_middle,
                                           channel_port=self.downlink_middle.channel_port)

        self.port_middle_up = mommy.make(Port,
                                         switch=self.neighboor_middle,
                                         channel_port=self.uplink_middle.channel_port)

        self.port_end_down = mommy.make(Port,
                                        switch=self.neighboor_end,
                                        channel_port=self.downlink_end.channel_port)

    def test_direct_bundle_ether(self):
        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        reserved_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag_domain=self.downlink_end.channel_port,
            status='ALLOCATED')

        production_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag_domain=self.downlink_end.channel_port,
            status='PRODUCTION')

        free_tags = get_free_tags(
            ix=self.ix,
            channel=self.uplink_origin)

        self.assertIn(available_tag, free_tags)
        self.assertNotIn(reserved_tag, free_tags)
        self.assertNotIn(production_tag, free_tags)
        self.assertTrue(len(free_tags) >= 2)

    def test_ix_managed(self):
        self.ix.tags_policy = 'ix_managed'

        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            status='AVAILABLE')

        reserved_tag = mommy.make(
            Tag,
            ix=self.ix,
            status='ALLOCATED')

        production_tag = mommy.make(
            Tag,
            ix=self.ix,
            status='PRODUCTION')

        free_tags = get_free_tags(
            ix=self.ix,
            channel=self.uplink_origin)

        self.assertIn(available_tag, free_tags)
        self.assertNotIn(reserved_tag, free_tags)
        self.assertNotIn(production_tag, free_tags)

    def test_instantiate_tag(self):
        tag_tested = instantiate_tag(
            channel=self.downlink_end,
            ix=self.ix,
            tag_number=55)

        self.assertIn(tag_tested, Tag.objects.filter(ix=self.ix))

    def test_get_tag_without_bilateral(self):
        used_production_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        mommy.make(
            BilateralPeer,
            tag=used_production_tag)

        free_tags = get_tag_without_bilateral(
            ix=self.ix,
            channel=self.uplink_origin)

        self.assertNotIn(used_production_tag, free_tags)
        self.assertNotIn(used_tag, free_tags)
        self.assertIn(available_tag, free_tags)

    def test_get_tag_without_bilateral_when_there_is_reserved_tag(self):
        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        reserved_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=8,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')
        reserved_tag.reserve_this()

        free_tags = get_tag_without_bilateral(
            ix=self.ix,
            channel=self.uplink_origin)

        self.assertNotIn(reserved_tag, free_tags)
        self.assertIn(available_tag, free_tags)

    def test_get_tag_all_services(self):
        used_production_bilateral_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_production_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_bilateral_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        used_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=12,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        mommy.make(
            BilateralPeer,
            tag=used_production_bilateral_tag)

        mommy.make(
            MLPAv4,
            tag=used_production_mlpa_tag)

        free_tags = get_tag_without_all_service(
            ix=self.ix,
            channel=self.uplink_origin)

        self.assertNotIn(used_production_bilateral_tag, free_tags)
        self.assertNotIn(used_production_mlpa_tag, free_tags)
        self.assertNotIn(used_bilateral_tag, free_tags)
        self.assertNotIn(used_mlpa_tag, free_tags)
        self.assertIn(available_tag, free_tags)

    def test_get_tag_all_services_when_there_is_reserved_tag(self):
        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=12,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        reserved_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=8,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')
        reserved_tag.reserve_this()

        free_tags = get_tag_without_all_service(
            ix=self.ix,
            channel=self.uplink_origin)

        self.assertNotIn(reserved_tag, free_tags)
        self.assertIn(available_tag, free_tags)

    def test_get_or_create_tag_without_all_services(self):
        used_production_bilateral_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_production_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_bilateral_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        used_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=12,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        bilateral_peer = mommy.make(
            BilateralPeer,
            tag=used_production_bilateral_tag)
        mlpav4 = mommy.make(
            MLPAv4,
            tag=used_production_mlpa_tag)

        used_tag = get_or_create_specific_tag_without_all_service(
            ix=self.ix,
            channel=self.uplink_origin,
            tag_number=used_mlpa_tag.tag)

        free_tag = get_or_create_specific_tag_without_all_service(
            ix=self.ix,
            channel=self.uplink_origin,
            tag_number=available_tag.tag)

        created_tag = get_or_create_specific_tag_without_all_service(
            ix=self.ix,
            channel=self.uplink_origin,
            tag_number=67)

        self.assertEqual(free_tag, available_tag)
        self.assertEqual(created_tag.tag, 67)
        self.assertFalse(used_tag)

    def test_get_or_create_tag_without_bilateral(self):
        used_production_bilateral_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_production_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        used_bilateral_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=10,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        used_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=12,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        bilateral_peer = mommy.make(
            BilateralPeer,
            tag=used_production_bilateral_tag)
        mlpav4 = mommy.make(
            MLPAv4,
            tag=used_production_mlpa_tag)

        used_tag = get_or_create_specific_tag_without_bilateral(
            ix=self.ix,
            channel=self.uplink_origin,
            tag_number=used_production_bilateral_tag.tag)

        free_tag = get_or_create_specific_tag_without_bilateral(
            ix=self.ix,
            channel=self.uplink_origin,
            tag_number=used_mlpa_tag.tag)

        created_tag = get_or_create_specific_tag_without_bilateral(
            ix=self.ix,
            channel=self.uplink_origin,
            tag_number=67)

        self.assertEqual(free_tag, used_mlpa_tag)
        self.assertEqual(created_tag.tag, 67)
        self.assertFalse(used_tag)

    def test_check_inner_tag_availability(self):
        cix_channel = mommy.make(
            CustomerChannel,
            cix_type=3)

        used_production_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        mommy.make(
            MLPAv4,
            tag=used_production_mlpa_tag,
            customer_channel=cix_channel,
            inner=1010)

        unavailability = check_inner_tag_availability(
            tag=used_production_mlpa_tag,
            inner=1010)

        availability = check_inner_tag_availability(
            tag=used_production_mlpa_tag,
            inner=1020)

        self.assertFalse(unavailability)
        self.assertTrue(availability)

    def test_get_available_inner_tag(self):
        cix_channel = mommy.make(
            CustomerChannel,
            cix_type=3)

        used_production_mlpa_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=11,
            tag_domain=self.downlink_block.channel_port,
            status='PRODUCTION')

        mommy.make(
            MLPAv4,
            tag=used_production_mlpa_tag,
            customer_channel=cix_channel,
            inner=1)

        available_tag = get_available_inner_tag(
            tag=used_production_mlpa_tag)

        self.assertEqual(available_tag, 2)
