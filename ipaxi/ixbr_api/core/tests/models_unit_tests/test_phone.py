from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import Contact, Phone, User
from ..login import DefaultLogin


class Test_Phone(TestCase):
    """Tests Phone model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean):
        phone = mommy.make(
            Phone, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        phone.description = 'new description'
        phone.save()
        mock.return_value = self.superuser

        self.assertEqual(phone.history.first().description,
                         'new description')
        self.assertEqual(phone.history.last().description,
                         'old description')
        self.assertEqual(phone.history.first().modified_by,
                         new_user)
        self.assertEqual(phone.history.last().modified_by,
                         self.superuser)

    # Test of fields validation
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_blank_fields(self, mock_full_clean):
        phone = mommy.make(Phone)
        phone.category = ''
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            phone.clean_fields()

        phone.number = ''
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            phone.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(Phone._meta.verbose_name), 'Phone')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(Phone._meta.verbose_name_plural),
                         'Phones')

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean):
        contact = mommy.make(Contact)
        phone = mommy.make(
            Phone, contact=contact)

        self.assertEquals(
            str(phone),
            '[Contact: {contact} : Phone {number}]'
            .format(contact=contact.email, number=phone.number))

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean):
        contacts = mommy.make(
            Contact, email=cycle(['aaa@nic.br', 'bbb@nic.br', 'ccc@nic.br']),
            _quantity=3)

        phone0 = mommy.make(Phone, contact=contacts[0], number='0000-0000')
        phone1 = mommy.make(Phone, contact=contacts[1], number='1000-0000')
        phone2 = mommy.make(Phone, contact=contacts[2], number='0000-0000')
        phone3 = mommy.make(Phone, contact=contacts[2], number='1000-0000')

        saved_phones = Phone.objects.all()
        self.assertEqual(saved_phones[0], phone0)
        self.assertEqual(saved_phones[1], phone1)
        self.assertEqual(saved_phones[2], phone2)
        self.assertEqual(saved_phones[3], phone3)

    # Tests of model validation
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_field(self, mock_full_clean):
        contact = mommy.make(Contact)
        other_contact = mommy.make(Contact)
        phone = mommy.make(Phone, number='1234-5678', contact=contact)

        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: Phone.number'):
            phone.number = '0000-0000'
            phone.clean()

        phone.number = '1234-5678'

        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: Phone.contact'):
            phone.contact = other_contact
            phone.clean()
