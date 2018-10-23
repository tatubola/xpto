from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ...models import DIO, PIX, DIOPort, User
from ..login import DefaultLogin


class Test_DIO(TestCase):
    """Tests DIO model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        dio = mommy.make(DIO, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        dio.description = 'new description'
        dio.save()
        mock.return_value = self.superuser

        self.assertEqual(dio.history.first().description, 'new description')
        self.assertEqual(dio.history.last().description, 'old description')
        self.assertEqual(dio.history.first().modified_by, new_user)
        self.assertEqual(dio.history.last().modified_by, self.superuser)

    # Tests of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_name_validation(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO)
        with self.assertRaisesMessage(
                ValidationError,
                "Ensure this value has at least 10 characters (it has 9)."):
            dio.name = '123456789'
            dio.clean_fields()

        dio = mommy.make(DIO)
        with self.assertRaisesMessage(
                ValidationError,
                "Ensure this value has at most 255 characters (it has 256)."):
            dio.name = '1' * 256
            dio.clean_fields()

    # Tests of methods
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO, name='dio example 1', pix__code='sp')
        self.assertEqual(str(dio), "[PIX {pix_code}: DIO {dio_name}]"
                                   .format(pix_code=dio.pix.code,
                                           dio_name=dio.name))

    def test_meta_verbose_name(self):
        self.assertEqual(str(DIO._meta.verbose_name), 'DIO')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(DIO._meta.verbose_name_plural), 'DIOs')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        pixes = mommy.make(PIX, ix__code=cycle(['aa', 'bb', 'cc']),
                           _quantity=3)
        dio0 = mommy.make(DIO, pix=pixes[0], name='dio example 0')
        dio1 = mommy.make(DIO, pix=pixes[0], name='dio example 1')
        dio2 = mommy.make(DIO, pix=pixes[1], name='dio example 0')
        dio3 = mommy.make(DIO, pix=pixes[2], name='dio example 0')
        dio4 = mommy.make(DIO, pix=pixes[2], name='dio example 2')

        saved_dios = DIO.objects.all()
        self.assertEqual(saved_dios[0], dio0)
        self.assertEqual(saved_dios[1], dio1)
        self.assertEqual(saved_dios[2], dio2)
        self.assertEqual(saved_dios[3], dio3)
        self.assertEqual(saved_dios[4], dio4)

    # Test of field uniqueness
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_field_uniqueness(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        mommy.make(DIO, pix=pix, name='dio example 0')
        dio2 = mommy.prepare(DIO, pix=pix, name='dio example 0')

        with self.assertRaisesMessage(ValidationError,
                                      "DIO with this Pix and Name already "
                                      "exists."):
            dio2.validate_unique()

        other_pix = mommy.make(PIX)
        dio2.pix = other_pix
        dio2.validate_unique()

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_field(self, mock_full_clean, mock_signals):
        pix = mommy.make(PIX)
        other_pix = mommy.make(PIX)
        dio = mommy.make(DIO, pix=pix)
        dio.pix = other_pix

        with self.assertRaisesMessage(
                ValidationError,
                "Trying to update non updatable field: DIO.pix"):
            dio.clean()

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_unique_ix_position(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO)
        dioports = mommy.make(DIOPort, dio=dio, ix_position=seq('123456789'),
                              _quantity=10)

        self.assertFalse(
            dio.validate_unique_ix_position(dioports[0],
                                            dioports[1].ix_position))
        self.assertTrue(
            dio.validate_unique_ix_position(dioports[1],
                                            dioports[1].ix_position))

        self.assertTrue(
            dio.validate_unique_ix_position(dioports[0],
                                            "other ix position"))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_unique_dc_position(self, mock_full_clean, mock_signals):
        dio = mommy.make(DIO)
        dioports = mommy.make(DIOPort,
                              dio=dio,
                              datacenter_position=seq('123456789'),
                              _quantity=10)

        self.assertFalse(
            dio.validate_unique_dc_position(dioports[0],
                                            dioports[1].datacenter_position))
        self.assertTrue(
            dio.validate_unique_dc_position(dioports[1],
                                            dioports[1].datacenter_position))

        self.assertTrue(
            dio.validate_unique_dc_position(dioports[0],
                                            "other datacenter position"))
