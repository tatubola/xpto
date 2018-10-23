# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import ASN

from ...validators import INVALID_ASN
from ..login import DefaultLogin


class ASSearchViewTestCase(TestCase):
    def setUp(self):
        # Log into application
        DefaultLogin.__init__(self)

        # patch method get_object_or_404 used in ASSearchView
        mock_patcher = patch(
            'ixbr_api.core.views.form_views.get_object_or_404')
        self.addCleanup(mock_patcher.stop)
        self.mock_asn = mock_patcher.start()

        self.asn = ASN(
            number=62000,)

        self.mock_asn.return_value = self.asn

    def test_as_search_valid_success(self):
        self.request = self.client.get(
            '{}?asn={}&submit=Search'.format(
                reverse('core:as_search'), self.asn.number))
        self.assertEqual(self.request.status_code, 302)
        self.assertEqual(
            reverse('core:as_detail', args=[self.asn.number]),
            self.request.url)

    def test_as_search_not_registered_success(self):
        asn_not_registered = 4222
        self.request = self.client.get(
            '{}?asn={}&submit=Search'.format(
                reverse('core:as_search'), asn_not_registered))
        self.assertEqual(self.request.status_code, 302)
        self.assertEqual(
            reverse('core:as_detail', args=[asn_not_registered]),
            self.request.url)

    def test_as_search_invalid_number_asn_failed(self):
        invalid_asn_number = -5454
        self.request = self.client.get(
            '{}?asn={}&submit=Search&prev_path={}'.format(
                reverse('core:as_search'),
                invalid_asn_number,
                reverse('core:home')))
        self.assertEqual(self.request.status_code, 302)
        self.assertEqual(reverse('core:home'), self.request.url)
        messages = [
            m.message for m in get_messages(self.request.wsgi_request)]
        self.assertIn(INVALID_ASN, messages[0])

    def test_as_search_not_number_asn_failed(self):
        not_a_number = 'it_is_not_an_asn'
        self.request = self.client.get(
            '{}?asn={}&submit=Search&prev_path={}'.format(
                reverse('core:as_search'),
                not_a_number,
                '{}?asn={}&submit=Search&prev_path={}'.format(
                    reverse('core:as_search'),
                    not_a_number,
                    reverse('core:as_detail', args=[self.asn.number]))))
        self.assertEqual(self.request.status_code, 302)
        self.assertEqual(
            reverse('core:as_detail', args=[self.asn.number]),
            self.request.url)
        messages = [
            m.message for m in get_messages(self.request.wsgi_request)]
        self.assertIn("ASNs are only compound by numbers.", messages)
