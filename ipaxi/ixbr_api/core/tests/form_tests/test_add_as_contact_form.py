# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ixbr_api.core.models import (ASN, IX, Organization, ContactsMap)

from ..login import DefaultLogin


class AddASContactFormViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        # patch method get_object_or_404 used in EditOrganizationFormView
        mock_full_clean = patch(
            'ixbr_api.core.models.'
            'HistoricalTimeStampedModel.full_clean')
        self.addCleanup(mock_full_clean.stop)
        self.mock_organization = mock_full_clean.start()

        mock_create_ips = patch(
            'ixbr_api.core.models.create_all_ips')
        self.addCleanup(mock_create_ips.stop)
        self.mock_create_ips = mock_create_ips.start()

        self.ix = mommy.make(IX, code='ria')
        self.asn = mommy.make(ASN, number=15000)
        self.organization = mommy.make(Organization, cnpj='22.476.230/0001-64')

        self.request = self.client.get(
            reverse('core:add_as_contact_form', args=[self.asn.number]))

        self.last_ticket = 12515
        # NOC Contact
        self.contact_name_noc = 'Wagner Luiz Neiva'
        self.contact_email_noc = 'wagner@onlineinternet.com.br'
        self.contact_phone_noc = '31973550055'
        # Administrative Contact
        self.contact_name_adm = 'Wagner Luiz Neiva'
        self.contact_email_adm = 'wagner@onlineinternet.com.br'
        self.contact_phone_adm = '31973550055'
        # Peer Contact
        self.contact_name_peer = 'NOC Matrix Do Brasil'
        self.contact_email_peer = 'peering@matrixdobrasil.com.br'
        self.contact_phone_peer = '3125173550'
        # Commercial Contact
        self.contact_name_com = 'Wagner Luiz Neiva'
        self.contact_email_com = 'wagner@onlineinternet.com.br'
        self.contact_phone_com = '31973550055'
        # Organization Contact
        self.contact_name_org = 'NOC Matrix Do Brasil'
        self.contact_email_org = 'noc@matrixdobrasil.com.br'
        self.contact_phone_org = '3125173550'

        # Organization info
        self.org_name = 'Online Telecomunicações, Info e internet Ltda'
        self.org_shortname = 'Online Telecomunicações'
        self.org_cnpj = '07.520.800/0001-82'
        self.org_url = 'http://www.onlineinternet.com.br/'
        self.org_addr = 'Rua Laudelina Carneiro'

    def test_as_add_contact_form_template(self):
        self.assertTemplateUsed('forms/add_as_contact_form.html')
        self.assertEqual(self.request.status_code, 200)

    def test_as_add_contact_form_success_with_selected_organization(self):
        self.response = self.client.post(
            reverse('core:add_as_contact_form', args=[self.asn.number]),
            {'ticket': self.last_ticket,
             'ix': self.ix.code,
             'organization': self.organization.uuid,
             'org_name': '',
             'org_shortname': '',
             'org_cnpj': '',
             'org_url': '',
             'org_addr': '',
             'last_ticket': self.last_ticket,
             'contact_name_noc': self.contact_name_noc,
             'contact_email_noc': self.contact_email_noc,
             'contact_phone_noc': self.contact_phone_noc,
             'contact_name_adm': self.contact_name_adm,
             'contact_email_adm': self.contact_email_adm,
             'contact_phone_adm': self.contact_phone_adm,
             'contact_name_peer': self.contact_name_peer,
             'contact_email_peer': self.contact_email_peer,
             'contact_phone_peer': self.contact_phone_peer,
             'contact_name_com': self.contact_name_com,
             'contact_email_com': self.contact_email_com,
             'contact_phone_com': self.contact_phone_com,
             'contact_name_org': self.contact_name_org,
             'contact_email_org': self.contact_email_org,
             'contact_phone_org': self.contact_phone_org,
             'asn': self.asn.number})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('AS Registered', messages)

        contact = ContactsMap.objects.get(asn=self.asn.number, ix=self.ix.code)
        self.assertEqual(contact.organization, self.organization)

    def test_as_add_contact_form_success_with_not_selected_organization(self):
        self.response = self.client.post(
            reverse('core:add_as_contact_form', args=[self.asn.number]),
            {'ticket': self.last_ticket,
             'ix': self.ix.code,
             'organization': '',
             'org_name': self.org_name,
             'org_shortname': self.org_shortname,
             'org_cnpj': self.org_cnpj,
             'org_url': self.org_url,
             'org_addr': self.org_addr,
             'last_ticket': self.last_ticket,
             'contact_name_noc': self.contact_name_noc,
             'contact_email_noc': self.contact_email_noc,
             'contact_phone_noc': self.contact_phone_noc,
             'contact_name_adm': self.contact_name_adm,
             'contact_email_adm': self.contact_email_adm,
             'contact_phone_adm': self.contact_phone_adm,
             'contact_name_peer': self.contact_name_peer,
             'contact_email_peer': self.contact_email_peer,
             'contact_phone_peer': self.contact_phone_peer,
             'contact_name_com': self.contact_name_com,
             'contact_email_com': self.contact_email_com,
             'contact_phone_com': self.contact_phone_com,
             'contact_name_org': self.contact_name_org,
             'contact_email_org': self.contact_email_org,
             'contact_phone_org': self.contact_phone_org,
             'asn': self.asn.number})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('AS Registered', messages)

        contact = ContactsMap.objects.get(asn=self.asn.number, ix=self.ix.code)
        self.assertEqual(contact.organization.name, self.org_name.upper())

    def test_as_add_contact_success_with_organization_that_already_exist(self):
        mommy.make(Organization, name=self.org_name)
        self.response = self.client.post(
            reverse('core:add_as_contact_form', args=[self.asn.number]),
            {'ticket': self.last_ticket,
             'ix': self.ix.code,
             'organization': '',
             'org_name': self.org_name,
             'org_shortname': self.org_shortname,
             'org_cnpj': self.org_cnpj,
             'org_url': self.org_url,
             'org_addr': self.org_addr,
             'last_ticket': self.last_ticket,
             'contact_name_noc': self.contact_name_noc,
             'contact_email_noc': self.contact_email_noc,
             'contact_phone_noc': self.contact_phone_noc,
             'contact_name_adm': self.contact_name_adm,
             'contact_email_adm': self.contact_email_adm,
             'contact_phone_adm': self.contact_phone_adm,
             'contact_name_peer': self.contact_name_peer,
             'contact_email_peer': self.contact_email_peer,
             'contact_phone_peer': self.contact_phone_peer,
             'contact_name_com': self.contact_name_com,
             'contact_email_com': self.contact_email_com,
             'contact_phone_com': self.contact_phone_com,
             'contact_name_org': self.contact_name_org,
             'contact_email_org': self.contact_email_org,
             'contact_phone_org': self.contact_phone_org,
             'asn': self.asn.number})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn('AS Registered', messages)
        contact = ContactsMap.objects.get(asn=self.asn.number, ix=self.ix.code)
        self.assertEqual(contact.organization.name, self.org_name.upper())

    def test_as_add_contact_form_failed_with_whitespace(self):
        mock_save_patcher = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.save')
        self.addCleanup(mock_save_patcher.stop)
        self.mock_save = mock_save_patcher.start()
        self.mock_save.reset_mock()

        self.response = self.client.post(
            reverse('core:add_as_contact_form', args=[self.asn.number]),
            {'ticket': self.last_ticket,
             'ix': self.ix.code,
             'organization': self.organization.uuid,
             'org_name': '',
             'org_shortname': '',
             'org_cnpj': '',
             'org_url': '',
             'org_addr': '',
             'last_ticket': self.last_ticket,
             'contact_name_noc': self.contact_name_noc,
             'contact_email_noc': self.contact_email_noc,
             'contact_phone_noc': self.contact_phone_noc,
             'contact_name_adm': self.contact_name_adm,
             'contact_email_adm': self.contact_email_adm,
             'contact_phone_adm': self.contact_phone_adm,
             'contact_name_peer': self.contact_name_peer,
             'contact_email_peer': self.contact_email_peer,
             'contact_phone_peer': self.contact_phone_peer,
             'contact_name_com': ' ',
             'contact_email_com': self.contact_email_com,
             'contact_phone_com': self.contact_phone_com,
             'contact_name_org': self.contact_name_org,
             'contact_email_org': self.contact_email_org,
             'contact_phone_org': self.contact_phone_org,
             'asn': self.asn.number})

        self.assertEqual(self.response.status_code, 302)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn("This field is required", messages[0])
