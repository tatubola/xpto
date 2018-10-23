from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from model_mommy import mommy

import ixbr_api.core.validators as validators

from ...models import ASN, ContactsMap, User


class Test_ASN(TestCase):
    """Tests ASN model."""

    def setUp(self):
        '''
        This method creates an user and logs into the system
        '''
        self.user = User.objects.get_or_create(name='testuser',
                                               email='testuser@nic.br')[0]
        self.client.force_login(self.user)

        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = self.user
        self.addCleanup(p.stop)

    @patch('ixbr_api.core.models.create_all_ips')
    def test_simple_history(self, mock_create_all_ips):
        asn = mommy.make(ASN, number=5, description='old description')

        new_user = User.objects.get_or_create(name='otheruser',
                                              email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user
        asn.description = 'new description'
        asn.save()
        mock.return_value = self.user

        self.assertEqual(asn.history.first().description, 'new description')
        self.assertEqual(asn.history.last().description, 'old description')
        self.assertEqual(asn.history.first().modified_by, new_user)
        self.assertEqual(asn.history.last().modified_by, self.user)

    # Tests of exclusion
    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_delete_as_without_contact_map(self,
                                           mock_full_clean,
                                           mock_create_all_ips):
        asn = mommy.make(ASN)
        self.assertEqual(1, ASN.objects.count())
        asn.delete()
        self.assertEqual(0, ASN.objects.count())

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_delete_as_with_contact_map(self,
                                        mock_full_clean,
                                        mock_create_all_ips):
        asn = mommy.make(ASN)
        mommy.make(ContactsMap, asn=asn)
        with self.assertRaisesMessage(
            ProtectedError,
            "Cannot delete some "
                "instances of model 'ASN' because they "
                "are referenced through a protected foreign key"):
            asn.delete()

    # Test of fields validation
    def test_validate_as_number(self):
        with self.assertRaisesMessage(ValidationError,
                                      validators.INVALID_ASN):
            mommy.make(ASN, number=0)

        with self.assertRaisesMessage(ValidationError,
                                      validators.INVALID_ASN):
            mommy.make(ASN, number=64498)

        with self.assertRaisesMessage(ValidationError,
                                      validators.INVALID_ASN):
            mommy.make(ASN, number=65536)

        with self.assertRaisesMessage(ValidationError,
                                      validators.INVALID_ASN):
            mommy.make(ASN, number=4200000000)

    # Tests of methods of ASN
    @patch('ixbr_api.core.models.create_all_ips')
    def test__str__(self, mock_create_all_ips):
        asn = mommy.make(ASN, number=10)
        self.assertEqual(str(asn), '[AS{number}]'.format(number=asn.number))

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__asn_with_contact_map(self,
                                        mock_full_clean,
                                        mock_create_all_ips):
        asn = mommy.make(ASN, number=10)
        contacts_map = mommy.make(ContactsMap, asn=asn)

        self.assertEqual(str(asn), '[AS{number}: {organization}]'.format(
            number=asn.number, organization=contacts_map.organization))

    def test_meta_verbose_name(self):
        self.assertEqual(str(ASN._meta.verbose_name), 'ASN')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(ASN._meta.verbose_name_plural), 'ASNs')

    @patch('ixbr_api.core.models.create_all_ips')
    def test_meta_order_by(self, mock_create_all_ips):
        asn4 = mommy.make(ASN, number=30)
        asn1 = mommy.make(ASN, number=10)
        asn3 = mommy.make(ASN, number=20)
        asn0 = mommy.make(ASN, number=5)
        asn2 = mommy.make(ASN, number=15)

        asns = ASN.objects.all()
        self.assertTrue(asns.ordered)
        self.assertEqual(asns[0], asn0)
        self.assertEqual(asns[1], asn1)
        self.assertEqual(asns[2], asn2)
        self.assertEqual(asns[3], asn3)
        self.assertEqual(asns[4], asn4)

    # Tests of model validation
    def test_update_number(self):
        asn = mommy.make(ASN, number=5, description='old description')
        with self.assertRaisesMessage(ValidationError,
                                      'Trying to update non updatable field: '
                                      'ASN.number'):
            asn.number = 6
            asn.save()
