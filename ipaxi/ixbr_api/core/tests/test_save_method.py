from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from ixbr_api.core.models import ASN
from ixbr_api.core.validators import INVALID_ASN
from ixbr_api.users.models import User


class TestSaveMethod(TestCase):

    def setUp(self):
        """

        Returns:

        """
        # Create an AS with fields ok and another AS with wrong fields
        self.superuser = \
            User.objects.create_superuser(
                email='superuser@ix.br',
                password='V&ryS@f3Pwd',
                name='Super User')

        patcher = patch('ixbr_api.core.models.get_current_user')
        self.addCleanup(patcher.stop)

        self.get_user_mock = patcher.start()
        self.get_user_mock.return_value = self.superuser

        self.valid_asn_number = 12345
        self.invalid_asn_number = 4294967299

    def test_save_an_as_all_valid_fields(self):
        """ Validate if save method is working properly

        During this test an AS is created an saved. All fields are saved
        according to the validators. After a save is executed, tries to
        retrieve the data from the database.

        Returns:
        """

        # Test case the save process a new AS with all fields
        self.good_asn = ASN()
        self.good_asn.number = self.valid_asn_number
        self.good_asn.last_ticket = 0
        self.assertEqual(len(ASN.objects.all()), 0)
        self.good_asn.save()
        self.assertEqual(len(ASN.objects.all()), 1)

        self.retrieve_asn = ASN.objects.get(number=self.valid_asn_number)
        self.assertEqual(self.retrieve_asn.number, self.good_asn.number)
        self.retrieve_asn.delete()
        self.assertEqual(len(ASN.objects.all()), 0)

    def test_save_an_as_wrong_fields(self):
        """ Validate if save method do not save when object is not compliance

        During this test, an AS is created with fields no compliance to the
        validators. The save method should return an error when executed.

        Returns:

        """
        # Test case the save process a new AS with a wrong field
        self.bad_asn = ASN()
        self.bad_asn.number = self.invalid_asn_number
        self.bad_asn.last_ticket = 0
        with self.assertRaisesMessage(ValidationError, INVALID_ASN):
            self.bad_asn.save()

    def test_update_an_as_all_valid_fields(self):
        """ Validate if save method is working properly when updating

        During this test an AS is created and saved. All fields are saved
        according to the validators. After a save is executed, tries to
        update it with proper field values.

        Returns:

        """
        self.good_asn = ASN()
        self.good_asn.number = self.valid_asn_number
        self.good_asn.last_ticket = 0
        self.good_asn.save()

        self.asn_to_update = ASN.objects.get(number=self.valid_asn_number)
        self.asn_to_update.last_ticket = 1
        self.asn_to_update.save()

        self.asn_to_validate = ASN.objects.get(number=self.valid_asn_number)
        self.assertEqual(self.asn_to_validate.last_ticket, 1)

    def test_update_an_as_invalid_fields(self):
        """ Validate if save method is working properly when updating

        During this test an AS is created and saved. All fields are saved
        according to the validators. After a save is executed, tries to
        update it with proper field values.

        Returns:

        """
        err_msg = 'Trying to update non updatable field: ASN.number'
        self.good_asn = ASN()
        self.good_asn.number = self.valid_asn_number
        self.good_asn.last_ticket = 0
        self.good_asn.save()

        self.asn_to_update = ASN.objects.get(number=self.valid_asn_number)
        self.asn_to_update.number = 54321
        with self.assertRaisesMessage(ValidationError, err_msg):
            self.asn_to_update.save()
