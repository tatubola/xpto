from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _
from model_mommy import mommy

from ...models import Contact, User
from ..login import DefaultLogin


class Test_Contact(TestCase):
    """Tests Contacts model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        contact = mommy.make(Contact, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        contact.description = 'new description'
        contact.save()
        mock.return_value = self.superuser

        self.assertEqual(contact.history.first().description,
                         'new description')
        self.assertEqual(contact.history.last().description, 'old description')
        self.assertEqual(contact.history.first().modified_by, new_user)
        self.assertEqual(contact.history.last().modified_by, self.superuser)

    # Tests of fields validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_email_validation(self, mock_full_clean, mock_signals):
        wrong_email = 'user.nic.br'

        with self.assertRaisesMessage(
            ValidationError,
                _("Enter a valid email address.")
                .format(n=len(wrong_email))):
            contact = mommy.make(Contact, email=wrong_email)
            contact.clean_fields()

    # Tests of methods
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean, mock_signals):
        contact = mommy.make(Contact, email='nic@nic.br', name='NIC contact')
        self.assertEqual(str(contact), "[{email}: {name}]".
                                       format(email=contact.email,
                                              name=contact.name))

    def test_meta_verbose_name(self):
        self.assertEqual(str(Contact._meta.verbose_name), 'Contact')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(Contact._meta.verbose_name_plural), 'Contacts')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        contacts = mommy.make(
            Contact,
            email=cycle(['nic2@nic.br', 'nic0@nic.br', 'nic1@nic.br']),
            _quantity=3)

        saved_contacts = Contact.objects.all()
        self.assertEqual(saved_contacts[0], contacts[1])
        self.assertEqual(saved_contacts[1], contacts[2])
        self.assertEqual(saved_contacts[2], contacts[0])

    # Tests of model validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_fields(self, mock_full_clean, mock_signals):
        contacts = mommy.make(Contact, email='nic0@nic.br', name='NIC.br')

        contacts.email = 'new_email@nic.br'
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: Contact.email'):
            contacts.clean()

        contacts.email = 'nic0@nic.br'
        contacts.name = 'Another name'
        with self.assertRaisesMessage(
                ValidationError,
                'Trying to update non updatable field: Contact.name'):
            contacts.clean()
