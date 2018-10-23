from collections import Counter
from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ...models import (ASN, DIO, IX, PIX, BilateralPeer,
                       ChannelPort, CustomerChannel, MLPAv4,
                       MLPAv6, Monitorv4, Port, Switch, User,)
from ...validators import USUAL_PIX_CODE
from ..login import DefaultLogin


class Test_PIX(TestCase):
    """Tests PIX model."""

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        pix = mommy.make(PIX, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        pix.description = 'new description'
        pix.save()
        mock.return_value = self.superuser

        self.assertEqual(pix.history.first().description,
                         'new description')
        self.assertEqual(pix.history.last().description, 'old description')
        self.assertEqual(pix.history.first().modified_by, new_user)
        self.assertEqual(pix.history.last().modified_by, self.superuser)

    # Tests of field validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_code_validation(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX, code='A')
        with self.assertRaisesMessage(
                ValidationError,
                'Ensure this value has at least 2 characters (it has 1).'):
            pix.clean_fields()

        pix.code = 'A' * 31
        with self.assertRaisesMessage(
                ValidationError,
                'Ensure this value has at most 30 characters (it has 31)'):
            pix.clean_fields()

        pix.code = '1A'
        with self.assertRaisesMessage(ValidationError, USUAL_PIX_CODE):
            pix.clean_fields()

        pix.code = 'ANID'
        # Clean fields is called to verify that fields are valid
        pix.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(PIX._meta.verbose_name), 'PIX')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(PIX._meta.verbose_name_plural), 'PIXs')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        ixs = mommy.make(IX, code=seq('sp'), _quantity=3)
        pix1 = mommy.make(PIX, ix=ixs[1], code='ANID1')
        pix4 = mommy.make(PIX, ix=ixs[2], code='ANID2')
        pix0 = mommy.make(PIX, ix=ixs[0], code='ANID0')
        pix3 = mommy.make(PIX, ix=ixs[2], code='ANID1')
        pix2 = mommy.make(PIX, ix=ixs[1], code='ANID2')

        saved_pixs = PIX.objects.all()
        self.assertEqual(saved_pixs[0], pix0)
        self.assertEqual(saved_pixs[1], pix1)
        self.assertEqual(saved_pixs[2], pix2)
        self.assertEqual(saved_pixs[3], pix3)
        self.assertEqual(saved_pixs[4], pix4)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX, ix__code='sp', code='ANID')

        self.assertEqual(str(pix), '[IX {ix}: PIX {pix}]'
                                   .format(ix=pix.ix.code, pix=pix.code))

    def __create_5_customer_channels_of_pix(self, pix, asn=None):
        channel_ports_in_pix = mommy.make(ChannelPort, _quantity=5)
        asn = asn or mommy.make(ASN)
        mommy.make(
            Port, channel_port=cycle(channel_ports_in_pix),
            switch__pix=pix, _quantity=5)
        customer_channels_in_pix = mommy.make(
            CustomerChannel, channel_port=cycle(channel_ports_in_pix),
            asn=asn, cix_type=1, _quantity=5)

        return customer_channels_in_pix

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_customer_channels(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        customer_channels_in_pix = self.__create_5_customer_channels_of_pix(
            pix)

        # Customer channels not related to pix
        other_pix = mommy.make(PIX)
        self.__create_5_customer_channels_of_pix(other_pix)

        self.assertEqual(
            Counter(pix.get_customer_channels()),
            Counter(customer_channels_in_pix))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_asns(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)

        asns = mommy.make(ASN, _quantity=5)
        customer_channels_in_pix = self.__create_5_customer_channels_of_pix(
            pix, asns[0])
        self.assertEqual(
            Counter([asns[0].number]), Counter(pix.get_asns()))

        mommy.make(
            MLPAv4, customer_channel=customer_channels_in_pix[1], asn=asns[1])
        self.assertEqual(
            Counter([asns[0].number, asns[1].number]),
            Counter(pix.get_asns()))

        mommy.make(
            MLPAv6, customer_channel=customer_channels_in_pix[2], asn=asns[2])
        self.assertEqual(
            Counter([asns[0].number, asns[1].number, asns[2].number]),
            Counter(pix.get_asns()))

        mommy.make(
            BilateralPeer, customer_channel=customer_channels_in_pix[3],
            asn=asns[3])
        self.assertEqual(
            Counter([asns[0].number, asns[1].number, asns[2].number,
                     asns[3].number]),
            Counter(pix.get_asns()))

        mommy.make(Monitorv4, customer_channel=customer_channels_in_pix[4],
                   asn=asns[4])
        self.assertEqual(
            Counter([asns[0].number, asns[1].number, asns[2].number,
                     asns[3].number, asns[4].number]),
            Counter(pix.get_asns()))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_has_dio(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        self.assertFalse(pix.has_dio())

        mommy.make(DIO, pix=pix)
        self.assertTrue(pix.has_dio())

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_stats_amount(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        customer_channels = self.__create_5_customer_channels_of_pix(pix)

        mommy.make(MLPAv4, customer_channel=customer_channels[0], _quantity=2)
        mommy.make(MLPAv6, customer_channel=customer_channels[1])
        mommy.make(BilateralPeer, customer_channel=customer_channels[2])
        mommy.make(Monitorv4, customer_channel=customer_channels[2])

        self.assertDictEqual(
            pix.get_stats_amount(),
            {'cix_amount': 5, 'mlpav6_amount': 1, 'monitorv4': 1,
             'mlpav4_amount': 2, 'asn_amount': 0, 'bilateral_amount': 1})

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_switch_infos(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        switch = mommy.make(Switch, pix=pix)

        status_port_1 = ['AVAILABLE', 'PRODUCTION', 'AVAILABLE', 'AVAILABLE']
        mommy.make(
            Port, status=cycle(status_port_1), switch=switch, _quantity=4)
        # mommy.make(Port, status='AVAILABLE', switch=switches[1], _quantity=2)
        amount_of_available_ports_by_switch = 3
        percents_available_ports_by_switch = 75

        switch_info = pix.get_switch_infos_by_pix()
        expected_info = \
            {'model': switch.model.model,
             'management_ip': switch.management_ip,
             'uuid': switch.uuid,
             'available_ports': amount_of_available_ports_by_switch,
             'percent_available_ports':
                percents_available_ports_by_switch}
        self.assertEqual(expected_info, switch_info['0'])

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_field(self, mock_full_clean, mock_signals):
        ix = mommy.make(IX)
        other_ix = mommy.make(IX)
        pix = mommy.make(PIX, ix=ix)

        pix.ix = other_ix
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: PIX.ix'):
            pix.clean()
