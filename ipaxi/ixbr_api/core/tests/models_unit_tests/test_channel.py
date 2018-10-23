from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import (IX, Channel, ChannelPort, CoreChannel, CustomerChannel,
                       DownlinkChannel, Port, Switch, UplinkChannel, User)
from ...validators import validate_channel_name
from ..login import DefaultLogin


class Test_Channel(TestCase):
    """Tests Channel model."""

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
        self.assertEqual(core_channel.history.last().description,
                         'old description')
        self.assertEqual(core_channel.history.first().modified_by,
                         new_user)
        self.assertEqual(core_channel.history.last().modified_by,
                         self.superuser)

    # Tests of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_name_with_more_than_255_chars(
            self, mock_full_clean, mock_signals):
        core_channel = mommy.make(CoreChannel)
        core_channel.name = "1" * 256

        with self.assertRaisesMessage(
                ValidationError,
                "Ensure this value has at most 255 characters (it has 256)."):
            core_channel.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(Channel._meta.verbose_name), 'Channel')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(Channel._meta.verbose_name_plural), 'Channels')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_ports(self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        mommy.make(Port, _quantity=7, channel_port=channel_port)
        core_channel = mommy.make(CoreChannel, channel_port=channel_port)

        self.assertEqual(core_channel.get_ports().count(), 7)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_switches(self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        switches = mommy.make(Switch, _quantity=3)
        mommy.make(Port, _quantity=7, channel_port=channel_port,
                   switch=cycle(switches))
        core_channel = mommy.make(CoreChannel, channel_port=channel_port)

        self.assertEqual(len(core_channel.get_switches()), 3)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_master_port_of_individual_channel_is_its_port(
            self, mock_full_clean, mock_signals):
        core_channel = mommy.make(CoreChannel, is_lag=False, is_mclag=False)
        self.assertEqual(core_channel.get_master_port(),
                         core_channel.get_ports().first())

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_master_port_of_channel_with_lag_is_port_with_similar_name(
            self, mock_full_clean, mock_signals):

        channel_port = mommy.make(ChannelPort)
        ports = mommy.make(Port, _quantity=7, channel_port=channel_port)
        ports[0].name = "1"
        ports[0].save()
        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_port, is_lag=True)
        customer_channel.name = "ct-1"
        customer_channel.save()

        self.assertEqual(customer_channel.get_master_port(),
                         ports[0])

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_raise_error_in_wrong_channel_name_master_port(
            self, mock_full_clean, mock_signals):

        channel_port = mommy.make(ChannelPort)
        ports = mommy.make(Port, _quantity=7, channel_port=channel_port,
                           switch__model__vendor='EXTREME')
        ports[0].name = "2"
        ports[0].save()
        with self.assertRaisesMessage(
                ValidationError, "1 master port has nos association with him"):
            customer_channel = mommy.make(
                CustomerChannel, channel_port=channel_port, is_lag=True)
            customer_channel.name = "ct-1"
            customer_channel.check_channel_name_port()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_mclag_channel_connected_to_differents_ixs(
            self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        ix = mommy.make(IX)
        other_ix = mommy.make(IX)
        mommy.make(Port, _quantity=7, switch__pix__ix=ix,
                   channel_port=channel_port)
        wrong_port = mommy.make(
            Port, switch__pix__ix=other_ix, channel_port=channel_port)

        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_port, is_mclag=True)
        with self.assertRaisesMessage(
                ValidationError,
                "IX is not the same in Switches of ports on this Channel."):
            customer_channel.validate_ports_channel()

        wrong_port.switch.pix.ix = ix
        wrong_port.switch.pix.save()
        customer_channel.validate_ports_channel()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_channel_with_ports_in_different_switches(
            self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        switch = mommy.make(Switch)
        other_switch = mommy.make(Switch)
        mommy.make(Port, _quantity=7, switch=switch, channel_port=channel_port)
        wrong_port = mommy.make(
            Port, switch=other_switch, channel_port=channel_port)

        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_port, is_mclag=False)

        with self.assertRaisesMessage(
                ValidationError,
                "Switch is not the same in ports of this Channel."):
            customer_channel.validate_ports_channel()

        wrong_port.switch = switch
        wrong_port.save()
        customer_channel.validate_ports_channel()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_channel_with_invalid_name(
            self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        switch = mommy.make(Switch, model__vendor='EXTREME')
        mommy.make(Port, _quantity=7, switch=switch, channel_port=channel_port)
        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_port, is_mclag=False,
            name='wrong name')
        with self.assertRaisesMessage(
                ValidationError,
                "CustomerChannel name doesn't match with switch model."):
            validate_channel_name(customer_channel)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_channel_with_valid_name(
            self, mock_full_clean, mock_signals):
        channel_port = mommy.make(ChannelPort)
        switch = mommy.make(Switch, model__vendor='EXTREME')
        mommy.make(Port, _quantity=7, switch=switch, channel_port=channel_port)
        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_port, is_mclag=False,
            name='ct-5')
        validate_channel_name(customer_channel)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_channel_class(self, mock_full_clean, mock_signals):
        ''' Test if method get_channel_class returns the correct class of the
            channel object. '''
        customer_channel = mommy.make(CustomerChannel)
        self.assertEqual(CustomerChannel, customer_channel.get_channel_class())

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_channels_of_switch(self, mock_full_clean, mock_signals):
        ''' Test if method get_channels_of_switch returns all channels of
            specified switch. '''
        switch = mommy.make(Switch)
        ports_of_switch = mommy.make(Port, switch=switch, _quantity=4)
        channel_ports = mommy.make(ChannelPort, _quantity=4)
        for channel_port, port in zip(channel_ports, ports_of_switch):
            channel_port.port_set.add(port)
        customer_channel = mommy.make(
            CustomerChannel, channel_port=channel_ports[0])
        uplink_channel = mommy.make(
            UplinkChannel, channel_port=channel_ports[1])
        core_channel = mommy.make(
            CoreChannel, channel_port=channel_ports[2])
        downlink_channel = mommy.make(
            DownlinkChannel, channel_port=channel_ports[3])

        channels_of_switch = Channel.get_channels_of_switch(switch)
        self.assertIn(customer_channel, channels_of_switch)
        self.assertIn(uplink_channel, channels_of_switch)
        self.assertIn(core_channel, channels_of_switch)
        self.assertIn(downlink_channel, channels_of_switch)
