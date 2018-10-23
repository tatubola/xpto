from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import (PIX, ChannelPort, CoreChannel, CustomerChannel, Switch,
                       SwitchModel, SwitchPortRange, create_all_ports,)
from ...use_cases.migrate_switch import migrate_switch
from ..login import DefaultLogin


class Test_Migrate_Switch(TestCase):
    """Tests Migrate Switch use case."""

    def __create_customer_channel(self, name, port):
        channel_port = mommy.make(ChannelPort)
        channel_port.port_set.add(port)
        port.status = 'CUSTOMER'
        port.save()
        mommy.make(CustomerChannel, name=name, channel_port=channel_port)

    def __create_core_channel(self, name, port):
        channel_port = mommy.make(ChannelPort)
        channel_port.port_set.add(port)
        port.status = 'INFRASTRUCTURE'
        port.save()
        mommy.make(CoreChannel, name=name, channel_port=channel_port)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def setUp(self, mock_full_clean, mock_signals):
        DefaultLogin.__init__(self)
        self.juniper = mommy.make(SwitchModel, vendor='JUNIPER')
        self.cisco = mommy.make(SwitchModel, vendor='CISCO')
        self.extreme = mommy.make(SwitchModel, vendor='EXTREME')
        self.brocade = mommy.make(SwitchModel, vendor='BROCADE')

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_migrating_switches_from_different_pixes_raises_exception(
            self, mock_full_clean, mock_signals):
        """ Tries to migrate a switch to a switch from a different pix and
            test if a exception is rased
        """

        old_switch = mommy.make(
            Switch, model=self.juniper, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.cisco)

        with self.assertRaises(ValueError):
            migrate_switch(old_switch, new_switch)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_switch_with_insufficient_number_of_ports_raises_exception(
            self, mock_full_clean, mock_signals):
        """ Tries to migrate to a switch with insufficient ports and test if
            a exception is rased
        """
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.juniper)
        mommy.make(
            SwitchPortRange, begin=1, end=3, name_format='{0}',
            switch_model=self.cisco)

        pix = mommy.make(PIX)

        old_switch = mommy.make(
            Switch, model=self.juniper, pix=pix, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.cisco, pix=pix)

        create_all_ports(old_switch)
        create_all_ports(new_switch)

        for i in range(4):
            self.__create_customer_channel(
                'ct-ae{0}'.format(i), old_switch.port_set.all()[i])

        # new_switch has only 3 ports, therefore it is not allowed to have
        # 4 channels.
        with self.assertRaises(ValidationError):
            migrate_switch(old_switch, new_switch)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_migrate_switch_update_names_and_switches_of_channels(
            self, mock_full_clean, mock_signals):
        """ Migrates a switch to a new switch and test if the names and
            switches of connected channels are updated.
        """

        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.juniper)
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.cisco)

        pix = mommy.make(PIX)

        old_switch = mommy.make(
            Switch, model=self.juniper, pix=pix, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.cisco, pix=pix)

        create_all_ports(old_switch)
        create_all_ports(new_switch)

        self.__create_customer_channel('ct-ae10', old_switch.port_set.all()[0])
        self.__create_customer_channel('ct-ae30', old_switch.port_set.all()[1])

        migrate_switch(old_switch, new_switch)

        customer_channels = CustomerChannel.objects.all()
        self.assertEqual(
            customer_channels[0].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(
            customer_channels[1].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(customer_channels[0].name, 'ct-BE10')
        self.assertEqual(customer_channels[1].name, 'ct-BE30')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_switches_with_different_ports_names(
            self, mock_full_clean, mock_signals):
        """ Migrates a switch to a new switch and test if the names and
            switches of connected channels are updated.
            The new switch have ports with a different name pattern.
        """
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='port{0}',
            switch_model=self.juniper)
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.brocade)

        pix = mommy.make(PIX)

        old_switch = mommy.make(
            Switch, model=self.juniper, pix=pix, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.brocade, pix=pix)

        create_all_ports(old_switch)
        create_all_ports(new_switch)

        self.__create_customer_channel('ct-ae10', old_switch.port_set.all()[0])
        self.__create_customer_channel('ct-ae30', old_switch.port_set.all()[1])

        migrate_switch(old_switch, new_switch)

        customer_channels = CustomerChannel.objects.all()
        self.assertEqual(
            customer_channels[0].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(
            customer_channels[1].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(customer_channels[0].name, 'ct-PC10')
        self.assertEqual(customer_channels[1].name, 'ct-PC30')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_migrate_to_switch_with_more_ports(
            self, mock_full_clean, mock_signals):
        """ Migrates a switch to a new switch and test if the names and
            switches of connected channels are updated.
            The new switch have more ports than the old switch.
        """
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.juniper)
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.extreme)
        mommy.make(
            SwitchPortRange, begin=49, end=72, name_format='{0}',
            switch_model=self.extreme)

        pix = mommy.make(PIX)

        old_switch = mommy.make(
            Switch, model=self.juniper, pix=pix, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.extreme, pix=pix)

        create_all_ports(old_switch)
        create_all_ports(new_switch)

        self.__create_customer_channel('ct-ae10', old_switch.port_set.all()[0])
        self.__create_customer_channel('ct-ae30', old_switch.port_set.all()[1])

        migrate_switch(old_switch, new_switch)

        customer_channels = CustomerChannel.objects.all()
        self.assertEqual(
            customer_channels[0].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(
            customer_channels[1].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(customer_channels[0].name, 'ct-10')
        self.assertEqual(customer_channels[1].name, 'ct-30')
        self.assertEqual(new_switch.port_set.count(), 72)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_migrate_to_switch_with_less_ports(
            self, mock_full_clean, mock_signals):
        """ Migrates a switch to a new switch and test if the names and
            switches of connected channels are updated.
            The new switch have less ports than the old switch.
        """
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.cisco)
        mommy.make(
            SwitchPortRange, begin=49, end=72, name_format='{0}',
            switch_model=self.cisco)
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.extreme)

        pix = mommy.make(PIX)

        old_switch = mommy.make(
            Switch, model=self.cisco, pix=pix, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.extreme, pix=pix)

        create_all_ports(old_switch)
        create_all_ports(new_switch)

        self.__create_customer_channel('ct-BE10', old_switch.port_set.all()[0])
        self.__create_customer_channel('ct-BE30', old_switch.port_set.all()[1])

        migrate_switch(old_switch, new_switch)

        customer_channels = CustomerChannel.objects.all()
        self.assertEqual(
            customer_channels[0].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(
            customer_channels[1].channel_port.port_set.first().switch,
            new_switch)
        self.assertEqual(customer_channels[0].name, 'ct-10')
        self.assertEqual(customer_channels[1].name, 'ct-30')
        self.assertEqual(new_switch.port_set.count(), 48)
        self.assertEqual(old_switch.port_set.count(), 72)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_migrate_switch_with_multiple_unavailable_ports(
            self, mock_full_clean, mock_signals):
        """ Migrates a switch to a new switch and test if the names and
            switches of connected channels are updated.
            The old switch have 6 customer channels and 1 core channel
            connected.
        """

        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='port{0}',
            switch_model=self.juniper)
        mommy.make(
            SwitchPortRange, begin=49, end=72, name_format='port{0}',
            switch_model=self.juniper)
        mommy.make(
            SwitchPortRange, begin=1, end=48, name_format='{0}',
            switch_model=self.extreme)

        pix = mommy.make(PIX)

        old_switch = mommy.make(
            Switch, model=self.juniper, pix=pix, management_ip='192.168.0.254')
        new_switch = mommy.make(Switch, model=self.extreme, pix=pix)

        create_all_ports(old_switch)
        create_all_ports(new_switch)

        for i in range(6):
            self.__create_customer_channel(
                'ct-ae{i}'.format(i=i),
                old_switch.port_set.all()[i])
        self.__create_core_channel(
            'cc-ae0', old_switch.port_set.last())
        migrate_switch(old_switch, new_switch)

        customer_channels = CustomerChannel.objects.all()
        for i in range(6):
            self.assertEqual(customer_channels[i].name, 'ct-{i}'.format(i=i))
        self.assertEqual(CoreChannel.objects.first().name, 'cc-0')
        self.assertEqual(new_switch.port_set.count(), 48)
        self.assertEqual(old_switch.port_set.count(), 72)
