from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import (BilateralPeer, MLPAv4, MLPAv6, Monitorv4, Service)
from ..login import DefaultLogin


class Test_Service(TestCase):
    """Tests Service model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    def test_get_service_by_uuid(
            self, mock_channel_port_signal, mock_full_clean,
            mock_create_all_ips):
        mlpav4 = mommy.make(MLPAv4)
        mlpav6 = mommy.make(MLPAv6)
        monitorv4 = mommy.make(Monitorv4)
        bilateral_peer = mommy.make(BilateralPeer)

        self.assertTrue(Service.get_objects_filter('pk',
                                                   bilateral_peer.pk).pop(),
                        bilateral_peer)
        self.assertTrue(Service.get_objects_filter('pk', mlpav4.pk).pop(),
                        mlpav4)
        self.assertTrue(Service.get_objects_filter('pk', mlpav6.pk).pop(),
                        mlpav6)
        self.assertTrue(Service.get_objects_filter('pk', monitorv4.pk).pop(),
                        monitorv4)
