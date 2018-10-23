# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import Organization

from ..login import DefaultLogin


class EditOrganizationFormViewTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.save')
        self.mock_save = p.start()
        self.addCleanup(p.stop)

        # Create an organization, although it is not saved.
        self.organization = Organization(
            uuid='0556a90b-5d58-4ba0-9102-5117ad26f066',
            name='Moreiras Bad Boy Inc.',
            shortname='Moreiras',
            url='https://moreiras.top',
            address='St. dos que é, SP 45452-854',
            last_ticket='45309')

        # patch method get_object_or_404 used in EditOrganizationFormView
        p = patch(
            'ixbr_api.core.views.form_views.get_object_or_404')
        mock_organization = p.start()
        self.addCleanup(p.stop)
        # Mock organization receive organization created
        mock_organization.return_value = self.organization

        # Get request in EditOrganizationFormView url
        self.response = self.client.get(
            reverse('core:edit_organization_form',
                    kwargs={'organization': self.organization.uuid}))

        # Variable to simulated a edition
        self.shortname = 'Test'
        self.name = 'Test Inc.'
        self.url = 'http://test.com.br'
        self.address = '666 Tests St., TE 71024-0351'
        self.last_ticket = '45687'

    def test_edit_organization_form_template(self):
        """Test that the AddDIOToPIXFormView returns a 200
        response, uses the correct template, and has the
        correct context.
        """
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core/edit_organization_form.html')

    def test_edit_organization_form_context(self):
        """Test if the correct context is sent to the template"""
        organization = self.response.context['organization']
        self.assertEqual(organization, self.organization.uuid)

    def test_edit_organization_form(self):
        '''Test a valid post request'''
        # TODO: Understand business rules to last ticket in edition cases
        # and fix it.
        self.mock_save.return_value = 'Object updated'

        self.response = self.client.post(
            reverse('core:edit_organization_form',
                    args=[self.organization.uuid]),
            {'shortname': self.shortname,
             'name': self.name,
             'url': self.url,
             'address': self.address, })

        self.assertEqual(self.organization.shortname, self.shortname)
        self.assertEqual(self.organization.name, self.name)
        self.assertEqual(self.organization.url, self.url)
        self.assertEqual(self.organization.address, self.address)
        self.assertEqual(self.mock_save.call_count, 1)
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn("Organization saved", messages)

    def test_edit_organization_form_failed(self):
        '''Test if force post an invalid field into form'''

        # TODO: Understand business rules to last ticket in edition cases
        # and fix it.
        self.mock_save.side_effect = ValidationError('Enter a valid URL')
        self.response = self.client.post(
            reverse('core:edit_organization_form',
                    args=[self.organization.uuid]),
            {'shortname': self.shortname,
             'name': self.name,
             'url': 'isso não é uma url',
             'address': self.address})
        messages = [
            m.message for m in get_messages(self.response.wsgi_request)]
        self.assertIn("Enter a valid URL", messages)
