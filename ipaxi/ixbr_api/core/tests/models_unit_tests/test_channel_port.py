from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import IX, ChannelPort, Port, Tag, User
from ..login import DefaultLogin


class Test_Channel_Port(TestCase):
    """Tests Channel Port model."""

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    def test_simple_history(
            self, mock_create_all_ips, mock_tag_channel_by_port,
            mock_full_clean):
        channel_port = mommy.make(ChannelPort, description='old description')

        new_user = User.objects.get_or_create(name='otheruser',
                                              email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user
        channel_port.description = 'new description'
        channel_port.save()
        mock.return_value = self.superuser

        self.assertEqual(channel_port.history.first().description,
                         'new description')
        self.assertEqual(channel_port.history.last().description,
                         'old description')
        self.assertEqual(channel_port.history.first().modified_by, new_user)
        self.assertEqual(channel_port.history.last().modified_by,
                         self.superuser)

    # Tests of methods of ChannelPort
    def test_verbose_name(self):
        self.assertEqual(str(ChannelPort._meta.verbose_name), 'ChannelPort')

    def test_verbose_name_plural(self):
        self.assertEqual(str(ChannelPort._meta.verbose_name_plural),
                         'ChannelPorts')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_meta__str__(self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        self.assertEqual(
            str(channel_port), "[{uuid}]".format(uuid=channel_port.uuid))

    # Tests of signals handlers
    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_create_tags_called_correctly(
            self, mock_full_clean, mock_create_tag):
        channel_port = mommy.make(ChannelPort,
                                  create_tags=False,
                                  tags_type='Indirect-Bundle-Ether')
        self.assertEqual(0, mock_create_tag.call_count)

        channel_port.create_tags = True
        channel_port.save()
        self.assertEqual(0, mock_create_tag.call_count)

        channel_port.tags_type = 'Direct-Bundle-Ether'
        channel_port.save()
        self.assertEqual(1, mock_create_tag.call_count)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_create_tags_successfully(self, mock_full_clean):
        channel_port = mommy.make(ChannelPort,
                                  create_tags=False,
                                  tags_type='Direct-Bundle-Ether')
        ix = mommy.make(IX, ipv4_prefix='10.0.0.0/22',
                        ipv6_prefix='2001:12f5::0/64', create_tags=False)
        mommy.make(Port, channel_port=channel_port, switch__pix__ix=ix)
        channel_port.create_tags = True
        channel_port.save()
        tags = Tag.objects.all()
        self.assertEqual(4096, tags.count())
        self.assertEqual(ix, tags[0].ix)
        self.assertEqual(channel_port, tags[0].tag_domain)
