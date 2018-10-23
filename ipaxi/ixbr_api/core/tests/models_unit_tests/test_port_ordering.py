from django.test import TestCase
from itertools import cycle
from model_mommy import mommy
from unittest.mock import patch

from ...models import (Port, PIX, Switch)
from ..login import DefaultLogin


class Test_Port_Ordering(TestCase):

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering_with_one_switch(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):

        switch = mommy.make(Switch, management_ip='192.0.0.1')
        ports_names = ['10', '2', '4', '3', '5', '6', '8', '9', '1', '7',
                       '11']
        mommy.make(Port, _quantity=len(ports_names),
                   switch=switch, name=cycle(ports_names))

        ordered_ports = Port.objects.order_by_port_name()
        self.assertEqual(list(ordered_ports.values_list('name', flat=True)),
                         ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                          '11'])

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering_with_different_format(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):

        switch = mommy.make(Switch, management_ip='192.0.0.1')
        ports_names = ['Ten0/0/1',
                       'Ten0/0/2',
                       'Ten0/0/3',
                       'Ten0/0/4',
                       'Ten0/0/5',
                       'Ten0/0/6',
                       'Ten0/0/7',
                       'Ten0/0/8',
                       'Ten0/0/9',
                       'Ten0/0/10',
                       'Ten0/1/1',
                       'Ten0/1/2',
                       'Ten0/1/3',
                       'Ten0/1/4',
                       'Ten0/1/5',
                       'Ten0/1/6',
                       'Ten0/1/7',
                       'Ten0/1/8',
                       'Ten0/1/9',
                       'Ten0/1/10']
        mommy.make(Port, _quantity=len(ports_names),
                   switch=switch, name=cycle(ports_names))

        ordered_ports = Port.objects.order_by_port_name()
        self.assertEqual(list(ordered_ports.values_list('name', flat=True)),
                         ports_names)

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering_with_two_switches(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):
        pix = mommy.make(PIX)
        switch1 = mommy.make(Switch, pix=pix, management_ip='192.0.0.1')
        switch2 = mommy.make(Switch, pix=pix, management_ip='192.0.0.2')
        ports_names = ['10', '2', '4', '3', '5', '6', '8', '9', '1', '7',
                       '11']
        mommy.make(Port, _quantity=len(ports_names),
                   switch=switch1, name=cycle(ports_names))
        mommy.make(Port, _quantity=len(ports_names),
                   switch=switch2, name=cycle(ports_names))

        ordered_ports = Port.objects.order_by_port_name()
        self.assertEqual(list(ordered_ports.values_list('name', flat=True)),
                         ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                          '11', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                          '10', '11'])
        for i in range(0, 11):
            self.assertEqual(ordered_ports[i].switch, switch1)
        for i in range(11, 11):
            self.assertEqual(ordered_ports[i].switch, switch2)

    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering_with_two_switches_and_different_patterns(
            self, mock_full_clean, mock_create_all_ips, mock_create_tags):
        pix = mommy.make(PIX)
        switch2 = mommy.make(Switch, pix=pix, management_ip='192.0.0.2')
        switch1 = mommy.make(Switch, pix=pix, management_ip='192.0.0.1')
        ports_names_switch_2 = ['10', '2', '4',
                                '3', '5', '6', '8', '9', '1', '7', '11']
        ports_names_switch_1 = ['Ten0/0/10', 'Ten0/0/2', 'Ten0/0/4',
                                'Ten0/0/3', 'Ten0/0/5', 'Ten0/0/6', 'Ten0/0/8',
                                'Ten0/0/9', 'Ten0/0/1', 'Ten0/0/7',
                                'Ten0/0/11']

        mommy.make(Port, _quantity=len(ports_names_switch_1),
                   switch=switch1, name=cycle(ports_names_switch_1))
        mommy.make(Port, _quantity=len(ports_names_switch_2),
                   switch=switch2, name=cycle(ports_names_switch_2))

        ordered_ports = Port.objects.order_by_port_name()
        self.assertEqual(list(ordered_ports.values_list('name', flat=True)),
                         ['Ten0/0/1', 'Ten0/0/2', 'Ten0/0/3',
                          'Ten0/0/4', 'Ten0/0/5', 'Ten0/0/6', 'Ten0/0/7',
                          'Ten0/0/8', 'Ten0/0/9', 'Ten0/0/10', 'Ten0/0/11',
                          '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                          '11'])
