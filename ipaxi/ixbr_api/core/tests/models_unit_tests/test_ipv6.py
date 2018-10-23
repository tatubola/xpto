from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _
from model_mommy import mommy

from ...models import IX, IPv6Address, MLPAv6, User
from ..login import DefaultLogin


class Test_IPv6_Address(TestCase):
    """Tests IPv6Address model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        ipv6 = mommy.make(
            IPv6Address, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        ipv6.description = 'new description'
        ipv6.save()
        mock.return_value = self.superuser

        self.assertEqual(ipv6.history.first().description,
                         'new description')
        self.assertEqual(ipv6.history.last().description,
                         'old description')
        self.assertEqual(ipv6.history.first().modified_by,
                         new_user)
        self.assertEqual(ipv6.history.last().modified_by,
                         self.superuser)

    # Test of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_address(self, mock_full_clean, mock_signals):
        ipv6 = mommy.make(IPv6Address)
        ipv6.address = 'invalid ipv6'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid IPv4 or IPv6 address.")):
            ipv6.clean_fields()

        ipv6.address = '2001:12fg::2:5'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid IPv4 or IPv6 address.")):
            ipv6.clean_fields()

        ipv6.address = '2001:12f0::2:5'
        # Clean fields is called to verify that fields are valid
        ipv6.clean_fields()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_url(self, mock_full_clean, mock_signals):
        ipv6 = mommy.make(IPv6Address, address='2001:12f0::2:5')
        ipv6.reverse_dns = 'invalid url'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid URL.")):
            ipv6.clean_fields()

        ipv6.reverse_dns = 'www.nic.br'
        with self.assertRaisesMessage(
                ValidationError,
                _("Enter a valid URL.")):
            ipv6.clean_fields()

        ipv6.reverse_dns = 'http://www.nic.br'
        ipv6.clean_fields()

        ipv6.reverse_dns = ''
        ipv6.clean_fields()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_blank_fields(self, mock_full_clean, mock_signals):
        ipv6 = mommy.make(IPv6Address)
        ipv6.ix = None
        with self.assertRaisesMessage(
                ValidationError,
                _("This field cannot be null.")):
            ipv6.clean_fields()

        ipv6.ix = mommy.make(IX)
        ipv6.address = ''
        with self.assertRaisesMessage(
                ValidationError,
                _("This field cannot be blank.")):
            ipv6.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(IPv6Address._meta.verbose_name),
                         'IPv6Address')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(IPv6Address._meta.verbose_name_plural),
                         'IPv6Addresses')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_signals):
        ipv6_address = mommy.make(
            IPv6Address, address='2001:12f0::2:5', in_lg=True)
        self.assertEquals(str(ipv6_address), '[2001:12f0::2:5L]')

        ipv6_address.in_lg = False
        ipv6_address.save()
        self.assertEquals(str(ipv6_address), '[2001:12f0::2:5]')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_status_of_allocated_address(
            self, mock_full_clean, mock_signals):
        allocated_ipv6 = mommy.make(IPv6Address)
        mlpa_v6 = mommy.make(MLPAv6, mlpav6_address=allocated_ipv6)
        self.assertEquals(allocated_ipv6.get_status(), 'ALLOCATED')

        mlpa_v6.delete()
        mommy.make(MLPAv6, mlpav6_address=allocated_ipv6)
        self.assertEquals(allocated_ipv6.get_status(), 'ALLOCATED')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_status_of_free_address(
            self, mock_full_clean, mock_signals):
        allocated_ipv6 = mommy.make(IPv6Address)
        self.assertEquals(allocated_ipv6.get_status(), 'FREE')

        mlpa_v6 = mommy.make(MLPAv6, mlpav6_address=allocated_ipv6)
        mlpa_v6.delete()
        self.assertEquals(allocated_ipv6.get_status(), 'FREE')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        addresses = ['2001:12f0::2:5', '2001:12f0::2:3', '2001:12f0::2:8']
        mommy.make(
            IPv6Address, address=cycle(addresses), _quantity=3)

        ipv6_addresses = IPv6Address.objects.all().values_list('address',
                                                               flat=True)
        self.assertEquals(ipv6_addresses[0], addresses[1])
        self.assertEquals(ipv6_addresses[1], addresses[0])
        self.assertEquals(ipv6_addresses[2], addresses[2])
