from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _
from model_mommy import mommy

from ...models import IX, IPv4Address, MLPAv4, Monitorv4, User
from ..login import DefaultLogin


class Test_IPv4_Address(TestCase):
    """Tests IPv4Address model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        ipv4 = mommy.make(
            IPv4Address, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        ipv4.description = 'new description'
        ipv4.save()
        mock.return_value = self.superuser

        self.assertEqual(ipv4.history.first().description,
                         'new description')
        self.assertEqual(ipv4.history.last().description,
                         'old description')
        self.assertEqual(ipv4.history.first().modified_by,
                         new_user)
        self.assertEqual(ipv4.history.last().modified_by,
                         self.superuser)

    # Test of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_address(self, mock_full_clean, mock_signals):
        ipv4 = mommy.make(IPv4Address)
        ipv4.address = '10.0.0.0.1'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid IPv4 or IPv6 address.")):
            ipv4.clean_fields()

        ipv4.address = '10.256.0.1'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid IPv4 or IPv6 address.")):
            ipv4.clean_fields()

        ipv4.address = '10.0.0.1'
        # Clean fields is called to verify that fields are valid
        ipv4.clean_fields()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_url(self, mock_full_clean, mock_signals):
        ipv4 = mommy.make(IPv4Address, address='10.0.0.1')
        ipv4.reverse_dns = 'invalid url'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid URL.")):
            ipv4.clean_fields()

        ipv4.reverse_dns = 'www.nic.br'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid URL.")):
            ipv4.clean_fields()

        ipv4.reverse_dns = 'http://www.nic.br'
        ipv4.clean_fields()

        ipv4.reverse_dns = ''
        ipv4.clean_fields()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_blank_fields(self, mock_full_clean, mock_signals):
        ipv4 = mommy.make(IPv4Address)
        ipv4.ix = None
        with self.assertRaisesMessage(
                ValidationError,
                _("This field cannot be null.")):
            ipv4.clean_fields()

        ipv4.ix = mommy.make(IX)
        ipv4.address = ''
        with self.assertRaisesMessage(
                ValidationError,
                _("This field cannot be blank.")):
            ipv4.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(IPv4Address._meta.verbose_name),
                         'IPv4Address')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(IPv4Address._meta.verbose_name_plural),
                         'IPv4Addresses')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_signals):
        ipv4_address = mommy.make(IPv4Address, address='10.0.0.1', in_lg=True)
        self.assertEquals(str(ipv4_address), '[10.0.0.1L]')

        ipv4_address.in_lg = False
        ipv4_address.save()
        self.assertEquals(str(ipv4_address), '[10.0.0.1]')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_status_of_allocated_address(
            self, mock_full_clean, mock_signals):
        allocated_ipv4 = mommy.make(IPv4Address)
        mlpa_v4 = mommy.make(MLPAv4, mlpav4_address=allocated_ipv4)
        self.assertEquals(allocated_ipv4.get_status(), 'ALLOCATED')

        mlpa_v4.delete()
        mommy.make(Monitorv4, monitor_address=allocated_ipv4)
        self.assertEquals(allocated_ipv4.get_status(), 'ALLOCATED')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_status_of_free_address(
            self, mock_full_clean, mock_signals):
        allocated_ipv4 = mommy.make(IPv4Address)
        self.assertEquals(allocated_ipv4.get_status(), 'FREE')

        mlpa_v4 = mommy.make(MLPAv4, mlpav4_address=allocated_ipv4)
        mlpa_v4.delete()
        self.assertEquals(allocated_ipv4.get_status(), 'FREE')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        addresses = ['10.0.0.5', '10.0.0.1', '10.0.0.9']
        mommy.make(IPv4Address, address=cycle(addresses), _quantity=3)

        ipv4_addresses = IPv4Address.objects.all().values_list('address',
                                                               flat=True)
        self.assertEquals(ipv4_addresses[0], addresses[1])
        self.assertEquals(ipv4_addresses[1], addresses[0])
        self.assertEquals(ipv4_addresses[2], addresses[2])
