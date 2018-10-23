from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import (MACAddress, MLPAv4, MLPAv6, User)
from ...validators import USUAL_MAC_ADDRESS
from ..login import DefaultLogin


class Test_MAC_Address(TestCase):
    """Tests MACAddress model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean):
        mac_address = mommy.make(
            MACAddress, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        mac_address.description = 'new description'
        mac_address.save()
        mock.return_value = self.superuser

        self.assertEqual(mac_address.history.first().description,
                         'new description')
        self.assertEqual(mac_address.history.last().description,
                         'old description')
        self.assertEqual(mac_address.history.first().modified_by,
                         new_user)
        self.assertEqual(mac_address.history.last().modified_by,
                         self.superuser)

    # Test of fields validation
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_mac_address_validation(self, mock_full_clean):
        mac_address = mommy.make(MACAddress)
        mac_address.address = '45:b3:b7:25:ee'
        with self.assertRaisesMessage(ValidationError, USUAL_MAC_ADDRESS):
            mac_address.clean_fields()

        mac_address.address = '45:b3:b7:25:ee:a8'
        # Clean fields is called to verify that fields are valid
        mac_address.clean_fields()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_blank_fields(self, mock_full_clean):
        mac_address = mommy.make(MACAddress)
        mac_address.address = ''
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            mac_address.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(MACAddress._meta.verbose_name), 'MACAddress')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(MACAddress._meta.verbose_name_plural),
                         'MACAddresses')

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean):
        mac_address = mommy.make(MACAddress, address='45:b3:b7:25:ee:a8')

        self.assertEquals(str(mac_address), '[45:b3:b7:25:ee:a8]')

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean):
        mommy.make(
            MACAddress, _quantity=3, address=cycle(['45:b3:b7:25:ee:a8',
                                                    '35:b3:b7:25:ee:a8',
                                                    '45:b3:b7:25:ee:aa']))
        mac_addresses = MACAddress.objects.all().values_list('address',
                                                             flat=True)
        self.assertEqual(mac_addresses[0], '35:b3:b7:25:ee:a8')
        self.assertEqual(mac_addresses[1], '45:b3:b7:25:ee:a8')
        self.assertEqual(mac_addresses[2], '45:b3:b7:25:ee:aa')

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    def test_mac_in_no_service(self, mock_channel_port_signal,
                               mock_full_clean, mock_create_all_ips):
        mac = mommy.make(MACAddress)
        mlpav4 = mommy.make(MLPAv4)
        mlpav6 = mommy.make(MLPAv6)
        x = 0
        self.assertEqual(mac.is_in_any_service(), False)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    @patch('ixbr_api.core.models.create_tag_by_channel_port')
    def test_mac_in_a_service(self, mock_channel_port_signal,
                              mock_full_clean, mock_create_all_ips):
        mac = mommy.make(MACAddress)
        mlpav4 = mommy.make(MLPAv4)
        mlpav6 = mommy.make(MLPAv6)
        mlpav6.mac_addresses.add(mac)

        self.assertEqual(mac.is_in_any_service(), True)

    # Tests of models validation
    def test_mac_converter(self):
        mac_address = mommy.make(MACAddress, address='1-2-3-4-5-6')
        self.assertEqual(mac_address.address, "01:02:03:04:05:06")
