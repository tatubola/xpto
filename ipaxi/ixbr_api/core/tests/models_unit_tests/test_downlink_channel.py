from itertools import cycle
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import DownlinkChannel, User
from ..login import DefaultLogin


class Test_Downlink_Channel(TestCase):
    """Tests DownlinkChannel model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):
        downlink_channel = mommy.make(
            DownlinkChannel, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        downlink_channel.description = 'new description'
        downlink_channel.save()
        mock.return_value = self.superuser

        self.assertEqual(downlink_channel.history.first().description,
                         'new description')
        self.assertEqual(downlink_channel.history.last().description,
                         'old description')
        self.assertEqual(downlink_channel.history.first().modified_by,
                         new_user)
        self.assertEqual(downlink_channel.history.last().modified_by,
                         self.superuser)

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(DownlinkChannel._meta.verbose_name),
                         'DownlinkChannel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(DownlinkChannel._meta.verbose_name_plural),
                         'DownlinkChannels')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        names = ['dc_4', 'dc_1', 'dc_0', 'dc_3', 'dc_2']
        mommy.make(DownlinkChannel, name=cycle(names), _quantity=5)

        downlink_channels = DownlinkChannel.objects.all()
        for downlink_channel, name in zip(downlink_channels, sorted(names)):
            self.assertEqual(downlink_channel.name, name)
