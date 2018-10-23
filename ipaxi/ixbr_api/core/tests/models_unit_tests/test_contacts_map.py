from itertools import cycle
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import ASN, IX, Contact, ContactsMap, Organization, User
from ..login import DefaultLogin


class Test_Contact_Map(TestCase):
    """Tests PIX model."""

    def setUp(self):
        DefaultLogin.__init__(self)

    @patch('ixbr_api.core.models.create_all_ips')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_simple_history(self, mock_full_clean, mock_create_all_ips):
        contacts_map = mommy.make(ContactsMap, description='old description')

        new_user = User.objects.get_or_create(name='otheruser',
                                              email='otheruser@nic.br')[0]
        p = patch('ixbr_api.core.models.get_current_user')
        mock = p.start()
        mock.return_value = new_user
        contacts_map.description = 'new description'
        contacts_map.save()
        mock.return_value = self.superuser

        self.assertEqual(contacts_map.history.first().description,
                         'new description')
        self.assertEqual(contacts_map.history.last().description,
                         'old description')
        self.assertEqual(contacts_map.history.first().modified_by, new_user)
        self.assertEqual(contacts_map.history.last().modified_by,
                         self.superuser)

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_validate_url(self, mock_full_clean, mock_signals):
        with self.assertRaisesMessage(ValidationError,
                                      "Enter a valid URL."):
            contacts_map = mommy.make(ContactsMap, peering_url="invalid_url")
            contacts_map.clean_fields()

        contacts_map = mommy.make(ContactsMap, peering_url="http://www.nic.br")

        # Clean fields is called to verify that fields are valid
        contacts_map.clean_fields()

    # Test of field uniqueness
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_field_uniqueness(self, mock_full_clean, mock_signals):
        organization = mommy.make(Organization)
        asn = mommy.make(ASN)
        ix = mommy.make(IX)
        mommy.make(ContactsMap, organization=organization, asn=asn, ix=ix)
        contacts_map2 = mommy.prepare(ContactsMap, organization=organization,
                                      asn=asn, ix=ix)
        with self.assertRaisesMessage(ValidationError,
                                      "ContactsMap with this Organization, "
                                      "ASN and Ix already exists."):
            contacts_map2.validate_unique()

        other_asn = mommy.make(ASN)
        contacts_map2.asn = other_asn

        # Validate unique is called to verify that all uniqueness constraints
        # are satisfied
        contacts_map2.validate_unique()

    # Tests of methods of Tag
    def test_meta_verbose_name(self):
        self.assertEqual(str(ContactsMap._meta.verbose_name), 'ContactsMap')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(ContactsMap._meta.verbose_name_plural),
                         'ContactsMaps')

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_meta__str__(self, mock_full_clean, mock_signals):
        asn = mommy.make(ASN)
        ix = mommy.make(IX)
        peer_contact = mommy.make(Contact)
        contacts_map = mommy.make(ContactsMap, asn=asn, ix=ix,
                                  peer_contact=peer_contact)
        self.assertEqual(
            str(contacts_map),
            "[AS{asn}: {ix}: {peer_contact}]".
            format(asn=str(asn), ix=str(ix), peer_contact=str(peer_contact)))

    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_ordering(self, mock_full_clean, mock_signals):
        asns = mommy.make(ASN, number=cycle([0, 1, 2]), _quantity=3)
        ixs = mommy.make(IX, code=cycle(["aa", "bb", "cc"]), _quantity=3)

        contacts_map4 = mommy.make(ContactsMap, asn=asns[2], ix=ixs[2])
        contacts_map1 = mommy.make(ContactsMap, asn=asns[0], ix=ixs[1])
        contacts_map3 = mommy.make(ContactsMap, asn=asns[2], ix=ixs[0])
        contacts_map0 = mommy.make(ContactsMap, asn=asns[0], ix=ixs[0])
        contacts_map2 = mommy.make(ContactsMap, asn=asns[1], ix=ixs[0])

        contacts_maps = ContactsMap.objects.all()
        self.assertEqual(contacts_maps[0], contacts_map0)
        self.assertEqual(contacts_maps[1], contacts_map1)
        self.assertEqual(contacts_maps[2], contacts_map2)
        self.assertEqual(contacts_maps[3], contacts_map3)
        self.assertEqual(contacts_maps[4], contacts_map4)

    # Test of field validation
    @patch('django.dispatch.dispatcher.Signal.send')
    @patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
    def test_update_non_updatable_field(self, mock_full_clean, mock_signals):
        ix = mommy.make(IX)
        contacts_map = mommy.make(ContactsMap, ix=ix)
        other_ix = mommy.make(IX)
        contacts_map.ix = other_ix

        with self.assertRaisesMessage(
            ValidationError, "Trying to update non updatable field: "
                             "ContactsMap.ix"):
                contacts_map.clean()
