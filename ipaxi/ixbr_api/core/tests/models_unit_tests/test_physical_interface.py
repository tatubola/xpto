
from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import PhysicalInterface, Port, User
from ..login import DefaultLogin


class Test_PhysicalInterface(TestCase):
    """Tests PhysicalInterface model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean):
        physical_interface = mommy.make(
            PhysicalInterface, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        physical_interface.description = 'new description'
        physical_interface.save()
        mock.return_value = self.superuser

        self.assertEqual(physical_interface.history.first().description,
                         'new description')
        self.assertEqual(physical_interface.history.last().description,
                         'old description')
        self.assertEqual(physical_interface.history.first().modified_by,
                         new_user)
        self.assertEqual(physical_interface.history.last().modified_by,
                         self.superuser)

    # Test of fields validation
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_blank_fields(self, mock_full_clean):
        physical_interface = mommy.make(PhysicalInterface)

        physical_interface.connector_type = ''
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            physical_interface.clean_fields()

        physical_interface.connector_type = 'SFP'
        physical_interface.port_type = ''
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            physical_interface.clean_fields()

        physical_interface.port_type = 'UTP'
        physical_interface.serial_number = ''
        # Clean fields is called to verify that fields are valid
        physical_interface.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(PhysicalInterface._meta.verbose_name),
                         'PhysicalInterface')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(PhysicalInterface._meta.verbose_name_plural),
                         'PhysicalInterfaces')

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean):
        physical_interface = mommy.make(PhysicalInterface,
                                        serial_number='pi3141')
        self.assertEqual(
            str(physical_interface),
            '[{serial}: {connector_type}: {port_type}]'
            .format(serial=physical_interface.serial_number,
                    connector_type=physical_interface.connector_type,
                    port_type=physical_interface.port_type))

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean):
        mommy.make(PhysicalInterface,
                   connector_type=cycle(['SFP', 'QSFP', 'CFP', 'SFP']),
                   port_type=cycle(['LR', 'LR4', 'LR', 'ZR']),
                   _quantity=4)

        physical_interfaces = PhysicalInterface.objects.all()
        self.assertEqual([physical_interfaces[0].connector_type,
                          physical_interfaces[0].port_type], ['CFP', 'LR'])
        self.assertEqual([physical_interfaces[1].connector_type,
                          physical_interfaces[1].port_type], ['QSFP', 'LR4'])
        self.assertEqual([physical_interfaces[2].connector_type,
                          physical_interfaces[2].port_type], ['SFP', 'LR'])
        self.assertEqual([physical_interfaces[3].connector_type,
                          physical_interfaces[3].port_type], ['SFP', 'ZR'])

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_get_free_physical_interfaces(self, mock_full_clean, mock_signals):
        physical_interfaces = mommy.make(PhysicalInterface, _quantity=5)
        mommy.make(Port, _quantity=3)
        mommy.make(Port, _quantity=2,
                   physical_interface=cycle(physical_interfaces))

        self.assertEqual(set(physical_interfaces[2:5]),
                         set(PhysicalInterface.get_free_physical_interfaces()))

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_blank_serial_number_of_UTP(self, mock_full_clean):
        physical_interface = mommy.make(
            PhysicalInterface, port_type='UTP', serial_number='')
        with self.assertRaisesMessage(
                ValidationError, 'UTP serial number cannot be blank'):
            physical_interface.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_not_blank_serial_number_of_UTP(self, mock_full_clean):
        physical_interface = mommy.make(
            PhysicalInterface, port_type='UTP',
            serial_number='XOdSwevnQlzkLRngKtqJ')

        # Clean is called to verify if object passes model validation
        physical_interface.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_update_serial_number_raises_exception(self, mock_full_clean):
        physical_interface = mommy.make(PhysicalInterface, serial_number='sn1')
        physical_interface.serial_number = 'sn2'
        with self.assertRaisesMessage(
                ValidationError, 'Trying to update non updatable field: '
                                 'PhysicalInterface.serial_number'):
            physical_interface.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_update_connector_type_raises_exception(self, mock_full_clean):
        physical_interface = mommy.make(PhysicalInterface,
                                        connector_type='SFP')
        physical_interface.connector_type = 'SFP+'
        with self.assertRaisesMessage(
                ValidationError, 'Trying to update non updatable field: '
                                 'PhysicalInterface.connector_type'):
            physical_interface.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_if_update_port_type_raises_exception(self, mock_full_clean):
        physical_interface = mommy.make(PhysicalInterface, port_type='UTP')
        physical_interface.port_type = 'ER'
        with self.assertRaisesMessage(
                ValidationError, 'Trying to update non updatable field: '
                                 'PhysicalInterface.port_type'):
            physical_interface.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_port_type_for_a_given_connector_type(
            self, mock_full_clean):
        physical_interface = mommy.make(
            PhysicalInterface, connector_type='SFP', port_type='ER')
        with self.assertRaisesMessage(
                ValidationError,
                'port_type not compatible with connector_type'):
            physical_interface.clean()

        physical_interface = mommy.make(
            PhysicalInterface, connector_type='CFP', port_type='10LR')
        with self.assertRaisesMessage(
                ValidationError,
                'port_type not compatible with connector_type'):
            physical_interface.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_valid_port_type_for_a_given_connector_type(self, mock_full_clean):
        physical_interface = mommy.make(
            PhysicalInterface, connector_type='CFP', port_type='LR4')
        physical_interface.clean()
