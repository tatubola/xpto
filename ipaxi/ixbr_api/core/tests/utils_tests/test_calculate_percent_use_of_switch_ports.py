from itertools import cycle
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import PIX, Port, Switch
from ..login import DefaultLogin
from ...utils.calculate_percent_use_of_switch_ports import (
    calculate_percent_use_of_switch_ports)


class Test_calculate_percent_use_of_switch_ports(TestCase):
    """Tests PIX model."""

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_with_mix_status_port_status(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        switch = mommy.make(Switch, pix=pix)
        ports_status = [
            'AVAILABLE', 'INFRASTRUCTURE', 'PRODUCTION', 'PRODUCTION'
        ]
        mommy.make(
            Port,
            switch=switch,
            status=cycle(ports_status),
            _quantity=len(ports_status)
        )
        available_ports = switch.port_set.filter(status='AVAILABLE').count()
        ports = Port.objects.filter(switch=switch)
        result = calculate_percent_use_of_switch_ports(ports, available_ports)

        self.assertEqual(result, 25)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_with_not_available_port(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        switch = mommy.make(Switch, pix=pix)
        ports_status = [
            'PRODUCTION', 'PRODUCTION', 'PRODUCTION', 'INFRASTRUCTURE'
        ]
        mommy.make(
            Port,
            switch=switch,
            status=cycle(ports_status),
            _quantity=len(ports_status)
        )
        available_ports = switch.port_set.filter(status='AVAILABLE').count()
        ports = Port.objects.filter(switch=switch)
        result = calculate_percent_use_of_switch_ports(ports, available_ports)

        self.assertEqual(result, 100)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_with_no_port_associate(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        switch = mommy.make(Switch, pix=pix)
        ports_status = [
            'AVAILABLE', 'PRODUCTION', 'PRODUCTION', 'INFRASTRUCTURE'
        ]
        mommy.make(
            Port,
            status=cycle(ports_status),
            _quantity=len(ports_status)
        )
        available_ports = 25
        ports = Port.objects.filter(switch=switch)
        result = calculate_percent_use_of_switch_ports(ports, available_ports)

        self.assertEqual(result, 0)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_with_all_ports_available(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        switch = mommy.make(Switch, pix=pix)
        ports_status = [
            'AVAILABLE', 'AVAILABLE', 'AVAILABLE', 'AVAILABLE'
        ]
        mommy.make(
            Port,
            status=cycle(ports_status),
            _quantity=len(ports_status)
        )
        available_ports = 100
        ports = Port.objects.filter(switch=switch)
        result = calculate_percent_use_of_switch_ports(ports, available_ports)

        self.assertEqual(result, 0)
