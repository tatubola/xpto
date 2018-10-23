from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _
from model_mommy import mommy

from ...models import (ASN, IX, ChannelPort, ContactsMap,
                       CustomerChannel, Port, User,)
from ..login import DefaultLogin


class Test_Customer_Channel(TestCase):
    """Tests Customer Channel model."""

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips,
                            mock_create_tags):
        customer_channel = mommy.make(
            CustomerChannel, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        customer_channel.description = 'new description'
        customer_channel.save()
        mock.return_value = self.superuser

        self.assertEqual(customer_channel.history.first().description,
                         'new description')
        self.assertEqual(
            customer_channel.history.last().description, 'old description')
        self.assertEqual(
            customer_channel.history.first().modified_by, new_user)
        self.assertEqual(
            customer_channel.history.last().modified_by, self.superuser)

    # Tests of methods
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__of_customer_channel_with_lag(
            self, mock_full_clean, mock_signals):
        customer_channel = mommy.make(CustomerChannel, is_lag=True)

        self.assertEqual(
            '{uuid} [{name}L]'.format(uuid=customer_channel.uuid,
                                      name=customer_channel.name),
            str(customer_channel))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__of_customer_channel_without_lag(
            self, mock_full_clean, mock_signals):
        customer_channel = mommy.make(CustomerChannel, is_lag=False)

        self.assertEqual(
            '{uuid} [{name}]'.format(uuid=customer_channel.uuid,
                                     name=customer_channel.name),
            str(customer_channel))

    def test_meta_verbose_name(self):
        self.assertEqual(str(CustomerChannel._meta.verbose_name),
                         'CustomerChannel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(CustomerChannel._meta.verbose_name_plural), 'CustomerChannels')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        names = ['cc_4', 'cc_1', 'cc_0', 'cc_3', 'cc_2']
        mommy.make(CustomerChannel, name=cycle(names), _quantity=len(names))

        customer_channels = CustomerChannel.objects.all()
        for customer_channel, name in zip(customer_channels, sorted(names)):
            self.assertEqual(customer_channel.name, name)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_has_qinq(self, mock_full_clean, mock_signals):
        customer_channel_with_qinq = mommy.make(CustomerChannel, cix_type=3)
        customer_channel_without_qinq = mommy.make(CustomerChannel, cix_type=0)

        self.assertTrue(customer_channel_with_qinq.has_qinq())
        self.assertFalse(customer_channel_without_qinq.has_qinq())

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_asn_in_ix(self, mock_full_clean, mock_signals):
        asn = mommy.make(ASN)
        other_asn = mommy.make(ASN)
        ix = mommy.make(IX)
        mommy.make(ContactsMap, ix=ix, asn=asn)

        channel_port = mommy.make(ChannelPort)
        mommy.make(
            Port, switch__pix__ix=ix, channel_port=channel_port,
            _quantity=2)

        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_port, asn=other_asn)

        with self.assertRaisesMessage(
                ValidationError,
                _("Asn: {ASN} is not registered in the IX: {IX}")
                .format(ASN=other_asn, IX=ix)):
            customer_channel.validate_asn_in_ix()

        customer_channel.asn = asn
        customer_channel.save()
        customer_channel.validate_asn_in_ix()
