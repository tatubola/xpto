# -*- coding: utf-8 -*-
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase

from ...forms import CreateOrganizationForm
from ...models import Organization
from ..login import DefaultLogin

from django.core.exceptions import ValidationError


class CreateOrganizationFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

    def test_template_used(self):
        '''Test if GET request returns a response with status code 200
        and if the response uses the correct template.'''
        request = self.client.get(reverse('core:create_organization_form'))
        self.assertEqual(200, request.status_code)
        self.assertTemplateUsed('forms/create_organization_form.html')

    def test_create_valid_organization(self):
        '''Test create an organization with valid inputs.'''

        form = CreateOrganizationForm(
            data={
                'last_ticket': 1,
                'name': 'IX.br',
                'shortname': 'ix',
                'cnpj': '39.279.577/0001-10',
                'url': 'http://ix.br',
                'country_code': 'BRA',
                'state': 'SP',
                'city': 'São Paulo',
                'address': 'Rua do IX',
                'zip_code': '00000-000'
            }
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_organization_form'), form.data)
        self.assertEqual(response.status_code, 302)

        organization = Organization.objects.first()
        self.assertEqual(organization.name, 'IX.br')
        self.assertEqual(organization.cnpj, '39279577000110')

        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Organization created successfully", messages)

    def test_create_organization_with_invalid_cnpj(self):
        '''Test create an organization with invalid cnpj.'''

        form = CreateOrganizationForm(
            data={
                'last_ticket': 1,
                'name': 'IX.br',
                'shortname': 'ix',
                'cnpj': '39.279.577/0001',
                'url': 'http://ix.br',
                'country_code': 'BRA',
                'state': 'SP',
                'city': 'São Paulo',
                'address': 'Rua do IX',
                'zip_code': '00000-000'
            }
        )
        self.assertEqual(form.is_valid(), True)

        response = self.client.post(
            reverse('core:create_organization_form'), form.data)
        self.assertEqual(response.status_code, 302)

        messages = [
            m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Enter a valid CNPJ number.", messages)
