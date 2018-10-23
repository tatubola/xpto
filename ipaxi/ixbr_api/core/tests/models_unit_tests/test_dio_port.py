from itertools import cycle
from random import shuffle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import DIO, PIX, DIOPort, Port, User
from ..login import DefaultLogin


class Test_DIO_Port(TestCase):
    """Tests DIOPort model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        dio_port = mommy.make(DIOPort, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        dio_port.description = 'new description'
        dio_port.save()
        mock.return_value = self.superuser

        self.assertEqual(dio_port.history.first().description,
                         'new description')
        self.assertEqual(dio_port.history.last().description,
                         'old description')
        self.assertEqual(dio_port.history.first().modified_by, new_user)
        self.assertEqual(dio_port.history.last().modified_by, self.superuser)

    # Tests of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ix_position_validation(self, mock_full_clean,
                                    mock_create_all_ips):
        dio_port = mommy.make(DIOPort)
        with self.assertRaisesMessage(
                ValidationError,
                "Ensure this value has at most 255 characters (it has 256)."):
            dio_port.ix_position = "1" * 256
            dio_port.clean_fields()

    # Tests of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_dc_position_validation(self, mock_full_clean,
                                    mock_create_all_ips):
        dio_port = mommy.make(DIOPort)

        with self.assertRaisesMessage(
                ValidationError,
                "This field cannot be blank."):
            dio_port.datacenter_position = ""
            dio_port.clean_fields()

        with self.assertRaisesMessage(
                ValidationError,
                "Ensure this value has at most 255 characters (it has 256)."):
            dio_port.datacenter_position = "1" * 256
            dio_port.clean_fields()

    # Tests of methods
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO, name="dio example 01")
        dio_port = mommy.make(
            DIOPort, dio=dio, datacenter_position="datacenter position 1")

        self.assertEqual(
            str(dio_port),
            "[DIO {dio}: POS {datacenter_position}]"
            .format(dio=dio_port.dio.name,
                    datacenter_position=dio_port.datacenter_position))

    def test_meta_verbose_name(self):
        self.assertEqual(str(DIOPort._meta.verbose_name), 'DIOPort')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(DIOPort._meta.verbose_name_plural), 'DIOPorts')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        pixes = mommy.make(PIX, ix__code=cycle(['aa', 'bb', 'cc']),
                           _quantity=3)
        dios = mommy.make(DIO, pix=cycle(pixes), _quantity=3)

        dio_port2 = mommy.make(DIOPort, dio=dios[2])
        dio_port0 = mommy.make(DIOPort, dio=dios[0])
        dio_port1 = mommy.make(DIOPort, dio=dios[1])

        saved_dio_ports = DIOPort.objects.all()
        self.assertEqual(saved_dio_ports[0], dio_port0)
        self.assertEqual(saved_dio_ports[1], dio_port1)
        self.assertEqual(saved_dio_ports[2], dio_port2)

    # Test of field uniqueness
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_field_uniqueness(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO)
        port = mommy.make(Port)
        dio_port = mommy.make(
            DIOPort, ix_position='ix position 0', dio=dio,
            datacenter_position='datacenter position 0', switch_port=port)
        dio_port2 = mommy.prepare(
            DIOPort, ix_position='ix position 0', dio=dio,
            datacenter_position='datacenter position 0', switch_port=port)

        with self.assertRaisesMessage(
                ValidationError,
                "DIOPort with this Dio, Ix position, Datacenter position and "
                "Switch port already exists."):
            dio_port2.validate_unique()

        dio_port.datacenter_position = 'another datacenter position'

        # Validate unique is called to verify that all uniqueness constraints
        # are satisfied
        dio_port.validate_unique()

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_field(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO)
        dio_port = mommy.make(DIOPort, dio=dio)
        other_dio = mommy.make(DIO)

        dio_port.dio = other_dio
        with self.assertRaisesMessage(
                ValidationError,
                "Trying to update non updatable field: DIOPort.dio"):
            dio_port.clean()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_order_by_datacenter_position(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO)
        datacenter_position_set = [
            'datacenter/{}/{}'.format(i, i + 1) for i in range(1, 10)
        ]

        shuffle(datacenter_position_set)

        mommy.make(
            DIOPort,
            dio=dio,
            datacenter_position=cycle(datacenter_position_set),
            _quantity=len(datacenter_position_set)
        )
        ordered_dioport_set = DIO.objects.get(pk=dio.uuid). \
            dioport_set.order_by_datacenter_position()

        datacenter_position_set = sorted(datacenter_position_set)
        for index, dioport in enumerate(ordered_dioport_set):
            self.assertEqual(
                dioport.datacenter_position,
                datacenter_position_set[index]
            )
