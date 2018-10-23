import ipaddress
import re
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

import ixbr_api.core.validators as validators

from ...models import IX, IPv4Address, IPv6Address, User


class Test_IX(TestCase):
    """Tests IX model."""

    def setUp(self):
        '''
        This method creates an user and logs into the system
        '''
        self.user = User.objects.get_or_create(
            name='testuser', email='testuser@nic.br')[0]
        self.client.force_login(self.user)

        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = self.user
        self.addCleanup(p.stop)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        ix = mommy.make(IX, code='sp', description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        ix.description = 'new description'
        ix.save()
        mock.return_value = self.user

        self.assertEqual(ix.history.first().description, 'new description')
        self.assertEqual(ix.history.last().description, 'old description')
        self.assertEqual(ix.history.first().modified_by, new_user)
        self.assertEqual(ix.history.last().modified_by, self.user)

    # Tests of fields validation
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.IX.clean')
    def test_code_with_more_than_4_chars(self,
                                         mock_clean,
                                         mock_create_all_ips):
        wrong_code = 'spspspspsp'

        with self.assertRaisesMessage(
            ValidationError,
                "Ensure this value has at most 4 characters (it has {n})."
                .format(n=len(wrong_code))):
            mommy.make(IX, code=wrong_code)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.IX.clean')
    def test_code_with_less_than_2_chars(self,
                                         mock_clean,
                                         mock_create_all_ips):
        wrong_code = 's'

        with self.assertRaisesMessage(
            ValidationError,
                "Ensure this value has at least 2 characters (it has {n})."
                .format(n=len(wrong_code))):
            mommy.make(IX, code=wrong_code)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.IX.clean')
    def test_code_with_uppercase_char(self, mock_clean, mock_create_all_ips):
        p = patch('ixbr_api.core.models.IX.clean')
        p.start()
        wrong_code = 'Sp'

        with self.assertRaisesMessage(
            ValidationError,
                validators.USUAL_IX_CODE
                .format(n=len(wrong_code))):
            mommy.make(IX, code=wrong_code)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.IX.clean')
    def test_wrong_shortname(self, mock_clean, mock_create_all_ips):
        p = patch('ixbr_api.core.models.IX.clean')
        p.start()
        wrong_shortname = 'aa.aa'

        with self.assertRaisesMessage(
            ValidationError,
                validators.USUAL_IX_SHORTNAME):
            mommy.make(IX, shortname=wrong_shortname)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.IX.clean')
    def test_ip_validator_raises_error(self, mock_clean, mock_create_all_ips):
        p = patch('ixbr_api.core.models.IX.clean')
        p.start()
        wrong_ipv4 = '187.16.216.256/21'
        wrong_ipv6 = '2001:12e21::/64'

        with self.assertRaisesMessage(
            ValidationError,
                validators.INVALID_IPV4_NETWORK):
            mommy.make(IX, ipv4_prefix=wrong_ipv4)

        with self.assertRaisesMessage(
            ValidationError,
                validators.INVALID_IPV4_NETWORK):
            mommy.make(IX, management_prefix=wrong_ipv4)

        with self.assertRaisesMessage(
            ValidationError,
                validators.INVALID_IPV6_NETWORK):
            mommy.make(IX, ipv6_prefix=wrong_ipv6)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.IX.clean')
    def test_ix_with_correct_fields(self, mock_clean, mock_create_all_ips):
        mommy.make(IX, code='sp', shortname='aaa.aaa',
                   fullname='São Paulo - SP',
                   ipv4_prefix='187.16.216.255/21',
                   ipv6_prefix='2001:12e2::/64',
                   management_prefix='192.168.0.15',
                   tags_policy='distributed')

    # Tests of methods of IX
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_create_all_ips):
        ix = mommy.make(IX, code='sp')
        self.assertEqual(str(ix), "[{code}]".format(code=ix.code))

    def test_ix_meta_verbose_name(self):
        self.assertEqual(str(IX._meta.verbose_name), 'IX')

    def test_ix_meta_verbose_name_plural(self):
        self.assertEqual(str(IX._meta.verbose_name_plural), 'IXs')

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ix_meta_order_by(self, mock_full_clean, mock_create_all_ips):
        ix1 = mommy.make(IX, code='b')
        ix3 = mommy.make(IX, code='d')
        ix2 = mommy.make(IX, code='c')
        ix0 = mommy.make(IX, code='a')
        ix4 = mommy.make(IX, code='e')

        ixs = list(IX.objects.all())
        self.assertEqual(ix0, ixs[0])
        self.assertEqual(ix1, ixs[1])
        self.assertEqual(ix2, ixs[2])
        self.assertEqual(ix3, ixs[3])
        self.assertEqual(ix4, ixs[4])

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_ip_network(self, mock_full_clean, mock_create_all_ips):
        ix = mommy.make(
            IX,
            ipv4_prefix='11.0.0.0/22',
            ipv6_prefix='2001:12e2::/64')

        self.assertEqual(ix.get_ipv4_network(),
                         ipaddress.ip_network(ix.ipv4_prefix))
        self.assertEqual(ix.get_ipv6_network(),
                         ipaddress.ip_network(ix.ipv6_prefix))

    # Tests of model validation
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ipv4_network_intersect_error(self,
                                          mock_full_clean,
                                          mock_create_all_ips):
        ix0 = mommy.make(
            IX,
            ipv4_prefix='11.0.0.0/24',
            ipv6_prefix='2001:12e2::/64')

        ix1 = mommy.make(
            IX,
            ipv4_prefix='11.0.0.0/22',
            ipv6_prefix='2002:12e2::/64')

        with self.assertRaisesMessage(
            ValidationError,
            '{ipv4} overlaps with {other_ipv4} from IX: {ix}'.
                format(ipv4=ix0.ipv4_prefix,
                       other_ipv4=ix1.ipv4_prefix,
                       ix=ix1)):
            ix0.validate_ip_network_intersect()

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ipv6_network_intersect_error(self,
                                          mock_full_clean,
                                          mock_create_all_ips):
        ix0 = mommy.make(
            IX,
            ipv4_prefix='12.0.0.0/24',
            ipv6_prefix='2001:12e2::/64')

        ix1 = mommy.make(
            IX,
            ipv4_prefix='11.0.0.0/22',
            ipv6_prefix='2001:12e2::/60')

        with self.assertRaisesMessage(
            ValidationError,
            '{ipv6} overlaps with {other_ipv6} from IX: {ix}'.
                format(ipv6=ix0.ipv6_prefix,
                       other_ipv6=ix1.ipv6_prefix,
                       ix=ix1)):
            ix0.validate_ip_network_intersect()

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_mgmt_network(self,
                                   mock_full_clean,
                                   mock_create_all_ips):
        ix0 = mommy.make(
            IX,
            ipv4_prefix='12.0.0.0/24',
            management_prefix='12.0.0.0/24',
            ipv6_prefix='2001:12e2::/64')

        with self.assertRaisesMessage(
            ValidationError,
            '{ip} is not a private network'.
                format(ip=ix0.management_prefix)):
            ix0.validate_mgmt_network()

    @patch('ixbr_api.core.models.create_all_ips')
    def test_valid_ix(self, mock_full_clean):
        mommy.make(IX, code='sp', shortname='aaa.aaa',
                   fullname='São Paulo - SP',
                   ipv4_prefix='187.16.216.0/24',
                   ipv6_prefix='2001:12e2::/64',
                   management_prefix='192.168.0.15',
                   tags_policy='distributed')

    # Tests of signals handlers
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_create_all_ips_successfully(self, mock_full_clean):
        mommy.make(
            IX,
            ipv4_prefix='11.0.0.0/22',
            ipv6_prefix='2001:12e2::/64',
            management_prefix='192.168.4.0/24')

        ipv4_address_list = IPv4Address.objects.values_list('address',
                                                            flat=True)
        ipv6_address_list = IPv6Address.objects.values_list('address',
                                                            flat=True)

        self.assertEqual(len(set(ipv4_address_list)), 1022)
        self.assertEqual(len(set(ipv6_address_list)), 1022)

        pattern_ipv4 = re.compile(
            r'11.0.[0123].(\d|\d\d|[01]\d\d|2[0-4]\d|25[0-5])$')
        pattern_ipv6 = re.compile(
            r'2001:12e2::([123]:)?(\d|\d\d|[01]\d\d|2[0-4]\d|25[0-5])$')

        for ipv4, ipv6 in zip(ipv4_address_list, ipv6_address_list):
            if pattern_ipv4.fullmatch(ipv4) is None:
                raise Exception("Error creating IPv4 network")
            if pattern_ipv6.fullmatch(ipv6) is None:
                raise Exception("Error creating IPv6 network")
