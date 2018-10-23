# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import IXAPIQuerySet

from ..makefaketestdata import MakeFakeTestData


class BasicsSetUp(TestCase):
    def setUp(self):
        MakeFakeTestData.__init__(self)


class HomeViewTestCase(BasicsSetUp):
    def test_basics(self):        # Instance a Request Factory
        self.response = self.client.get(
            reverse('core:home'))

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed('home.html')

    def test_context(self):
        self.response = self.client.get(
            reverse('core:home'))
        self.assertTrue(self.response.context['ix_list'][0].code, 'cpv')
        self.assertIsInstance(self.response.context['ix_list'], IXAPIQuerySet)
        self.assertTrue(
            self.response.context['ix_list'][0].fullname, 'Campina Grande')
        self.assertTrue(self.response.context['ix_list'][1].code, 'sp')
        self.assertTrue(self.response.context['user'], 'tupi@nic.br')


class ASSearchViewTestCase(BasicsSetUp):
    def test_AS_already_exists_on_the_system(self):
        self.response = self.client.get(
            reverse('core:as_search') +
            '?asn=' + str(self.chamacoco.number) +
            '&submit=Search')
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, '/core/as/' +
                         str(self.chamacoco.number) + '/')

    def test_AS_still_not_exists_on_the_system(self):
        self.response = self.client.get(
            reverse('core:as_search') +
            '?asn=2243&submit=Search')
        self.assertEqual(self.response.status_code, 302)
