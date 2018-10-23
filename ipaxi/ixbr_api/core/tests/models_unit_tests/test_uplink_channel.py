from itertools import cycle
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import UplinkChannel, User
from ..login import DefaultLogin


class Test_Uplink_Channel(TestCase):
    """Tests UplinkChannel model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):
        uplink_channel = mommy.make(
            UplinkChannel, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        uplink_channel.description = 'new description'
        uplink_channel.save()
        mock.return_value = self.superuser

        self.assertEqual(uplink_channel.history.first().description,
                         'new description')
        self.assertEqual(uplink_channel.history.last().description,
                         'old description')
        self.assertEqual(uplink_channel.history.first().modified_by,
                         new_user)
        self.assertEqual(uplink_channel.history.last().modified_by,
                         self.superuser)

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(UplinkChannel._meta.verbose_name),
                         'UplinkChannel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(UplinkChannel._meta.verbose_name_plural),
                         'UplinkChannels')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        mommy.make(UplinkChannel,
                   name=cycle(['uc_4', 'uc_1', 'uc_0', 'uc_3', 'uc_2']),
                   _quantity=5)

        uplink_channel = UplinkChannel.objects.all()
        self.assertEqual(uplink_channel[0].name, 'uc_0')
        self.assertEqual(uplink_channel[1].name, 'uc_1')
        self.assertEqual(uplink_channel[2].name, 'uc_2')
        self.assertEqual(uplink_channel[3].name, 'uc_3')
        self.assertEqual(uplink_channel[4].name, 'uc_4')
