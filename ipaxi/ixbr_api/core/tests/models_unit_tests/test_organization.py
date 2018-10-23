from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import Organization, User
from ..login import DefaultLogin


class Test_Organization(TestCase):
    """Tests Organization model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean):
        organization = mommy.make(Organization, description='old description')

        new_user = User.objects.get_or_create(
            name='otheruser', email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user

        organization.description = 'new description'
        organization.save()
        mock.return_value = self.superuser

        self.assertEqual(organization.history.first().description,
                         'new description')
        self.assertEqual(
            organization.history.last().description, 'old description')
        self.assertEqual(
            organization.history.first().modified_by, new_user)
        self.assertEqual(
            organization.history.last().modified_by, self.superuser)

    # Tests of fields validation
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_cnpj(self, mock_full_clean):
        organization = mommy.make(Organization, cnpj='1162683600011')
        with self.assertRaisesMessage(
                ValidationError, 'Enter a valid CNPJ number.'):
            organization.clean_fields()

        organization = mommy.make(
            Organization, cnpj='11626836000112', url='http://nic.br')
        # Clean fields is called to verify that fields are valid
        organization.clean_fields()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_url(self, mock_full_clean):
        with self.assertRaisesMessage(ValidationError,
                                      "Enter a valid URL."):
            organization = mommy.make(Organization, url='invalid_url')
            organization.clean_fields()

        organization = mommy.make(Organization, url='http://www.nic.br')
        organization.clean_fields()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_invalid_blank_fields(self, mock_full_clean):
        organization = mommy.make(Organization, name='')
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            organization.clean_fields()

        organization = mommy.make(Organization, shortname='')
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            organization.clean_fields()

        organization = mommy.make(Organization, url='')
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            organization.clean_fields()

        organization = mommy.make(Organization, address='')
        with self.assertRaisesMessage(
                ValidationError, "This field cannot be blank."):
            organization.clean_fields()

    # Tests of methods
    def test_meta_verbose_name(self):
        self.assertEqual(str(Organization._meta.verbose_name), 'Organization')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(
            str(Organization._meta.verbose_name_plural), 'Organizations')

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean):
        mommy.make(Organization, shortname=cycle(['o2', 'o1', 'o3', 'o0']),
                   _quantity=4)

        organizations_shortname = Organization.objects.all().values_list(
            'shortname', flat=True)
        self.assertEqual(organizations_shortname[0], 'o0')
        self.assertEqual(organizations_shortname[1], 'o1')
        self.assertEqual(organizations_shortname[2], 'o2')
        self.assertEqual(organizations_shortname[3], 'o3')

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test__str__(self, mock_full_clean):
        organization = mommy.make(
            Organization, name='name', shortname='shortname')

        self.assertEqual(
            str(organization),
            '[{shortname}: {name}]'.format(shortname=organization.shortname,
                                           name=organization.name))

    # Tests of model validation
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_field(self, mock_full_clean):
        organization = mommy.make(Organization, cnpj='11626836000112')
        organization.cnpj = '11626836000113'
        with self.assertRaisesMessage(
                ValidationError, "Trying to update non updatable field: "
                                 "Organization.cnpj"):
            organization.clean()

    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_format_cnpj(self, mock_full_clean):
        organization = mommy.make(
            Organization, cnpj='11.626.836/0001-12', url='http://www.nic.br')
        organization.clean_fields()
        organization.clean()

        self.assertEquals(organization.cnpj, '11626836000112')
