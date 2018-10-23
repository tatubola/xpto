from django.test import TestCase

from ....core.forms import (AddASContactForm, AddMACServiceForm,
                            EditMLPAv4Form, EditMLPAv6Form,)


class AddASContactFormTest(TestCase):
    def setUp(self):
        self.form = AddASContactForm()

    def test_form_has_field(self):
        expect_fields = ['asn', 'default_attr', 'contact_name_noc',
                         'contact_email_noc', 'contact_phone_noc',
                         'contact_name_adm', 'contact_email_adm',
                         'contact_phone_adm', 'contact_name_peer',
                         'contact_email_peer', 'contact_phone_peer',
                         'contact_name_com', 'contact_email_com',
                         'contact_phone_com', 'or_name',
                         'org_shortname', 'org_cnpj', 'org_url', 'org_addr',
                         'ix', 'ticket']
        self.assertEqual(expect_fields.sort(), list(self.form.fields).sort())


class EditMLPAv4FormTest(TestCase):
    def setUp(self):
        self.form = EditMLPAv4Form()

    def test_form_has_field(self):
        expect_fields = ['mlpav4_address']
        self.assertEqual(expect_fields.sort(), list(self.form.fields).sort())


class EditMLPAv6FormTest(TestCase):
    def setUp(self):
        self.form = EditMLPAv6Form()

    def test_form_has_field(self):
        expect_fields = ['mlpav6_address']
        self.assertEqual(expect_fields.sort(), list(self.form.fields).sort())


class AddMACServiceFormTest(TestCase):
    def setUp(self):
        self.form = AddMACServiceForm()

    def test_form_has_field(self):
        expect_fields = ['address', 'description', 'last_ticket']
        self.assertEqual(expect_fields.sort(), list(self.form.fields).sort())
