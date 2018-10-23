from itertools import cycle
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import TranslationChannel, User
from ..login import DefaultLogin


class Test_Translation_Channel(TestCase):
    """Tests TranslationChannel model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):
        translation_channel = mommy.make(
            TranslationChannel, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        translation_channel.description = 'new description'
        translation_channel.save()
        mock.return_value = self.superuser

        self.assertEqual(translation_channel.history.first().description,
                         'new description')
        self.assertEqual(translation_channel.history.last().description,
                         'old description')
        self.assertEqual(translation_channel.history.first().modified_by,
                         new_user)
        self.assertEqual(translation_channel.history.last().modified_by,
                         self.superuser)

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(TranslationChannel._meta.verbose_name),
                         'TranslationChannel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(TranslationChannel._meta.verbose_name_plural),
                         'TranslationChannels')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        mommy.make(TranslationChannel,
                   name=cycle(['tc_4', 'tc_1', 'tc_0', 'tc_3', 'tc_2']),
                   _quantity=5)

        translation_channel = TranslationChannel.objects.all()
        self.assertEqual(translation_channel[0].name, 'tc_0')
        self.assertEqual(translation_channel[1].name, 'tc_1')
        self.assertEqual(translation_channel[2].name, 'tc_2')
        self.assertEqual(translation_channel[3].name, 'tc_3')
        self.assertEqual(translation_channel[4].name, 'tc_4')
