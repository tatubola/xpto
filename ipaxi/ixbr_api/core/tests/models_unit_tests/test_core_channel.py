from itertools import cycle
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import CoreChannel, User
from ..login import DefaultLogin


class Test_Core_Channel(TestCase):
    """Tests CoreChannel model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips,
                            mock_create_tags):
        core_channel = mommy.make(CoreChannel, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        core_channel.description = 'new description'
        core_channel.save()
        mock.return_value = self.superuser

        self.assertEqual(core_channel.history.first().description,
                         'new description')
        self.assertEqual(
            core_channel.history.last().description, 'old description')
        self.assertEqual(
            core_channel.history.first().modified_by, new_user)
        self.assertEqual(
            core_channel.history.last().modified_by, self.superuser)

    # Tests of methods

    def test_meta_verbose_name(self):
        self.assertEqual(str(CoreChannel._meta.verbose_name), 'CoreChannel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(CoreChannel._meta.verbose_name_plural), 'CoreChannels')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        names = ['cc_4', 'cc_1', 'cc_0', 'cc_3', 'cc_2']
        mommy.make(
            CoreChannel, name=cycle(names), _quantity=len(names))

        core_channels = CoreChannel.objects.all()
        for core_channel, name in zip(core_channels, sorted(names)):
            self.assertEqual(core_channel.name, name)
