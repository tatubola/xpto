# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from ..makefaketestdata import MakeFakeTestData


class IPsViewTestCase(TestCase):
    def setUp(self):

        MakeFakeTestData.__init__(self)

        # Instance a Request Factory
        self.response = self.client.get(reverse(
            'core:ip_list', args=[self.sp.code]))

        self.c = Client()

    def test_login(self):
        """ Check if is logged """
        # The participant make login into the application
        self.assertTrue(self.login)

    def test_ips_basics(self):
        """Test that the solo view returns a 200 response, uses
        the correct template, and has the correct context
        """
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core/ip_list.html')

    def test_ips_return(self):
        ix_code = self.response.context['ix'].code
        self.assertEqual(ix_code, self.sp.code)

        ips_name = self.response.context['ips']
        self.assertIs(type(ips_name), dict)

        self.assertEqual(ips_name[1]['v4'], self.ipv4_sp_kinikinau)
        self.assertEqual(ips_name[1]['v6'], self.ipv6_sp_kinikinau)

        self.assertEqual(ips_name[2]['v4'], self.ipv4_sp_monitor_v4_1)
        self.assertEqual(ips_name[2]['v6'], self.ipv6_sp_monitor_v4_1)

        self.assertEqual(ips_name[3]['v4'], self.ipv4_sp_monitor_v4_2)
        self.assertEqual(ips_name[3]['v6'], self.ipv6_sp_monitor_v4_2)

        self.assertEqual(ips_name[4]['v4'], self.ipv4_sp_monitor_v4_3)
        self.assertEqual(ips_name[4]['v6'], self.ipv6_sp_monitor_v4_3)

        self.assertEqual(ips_name[5]['v4'], self.ipv4_sp_chamacoco)
        self.assertEqual(ips_name[5]['v6'], self.ipv6_sp_chamacoco)

        self.assertEqual(ips_name[6]['v4'], self.ipv4_sp_none)
        self.assertEqual(ips_name[6]['v6'], self.ipv6_sp_none)

        self.assertEqual(ips_name[7]['v4'], self.ipv4_sp_terena)
        self.assertEqual(ips_name[7]['v6'], self.ipv6_sp_terena)

    def test_get_ip_informations_by_click__ip_views(self):
        # To a valid request
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_ip_informations_by_click__ip_views',
                args=[
                    self.sp.code]) +
            '?ipv4=' +
            self.ipv4_sp_chamacoco.address +
            '&ipv6=' +
            self.ipv6_sp_chamacoco.address +
            '&ip_opened=2')
        context = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context['asn_ipv4'], self.chamacoco.number)
        self.assertEqual(context['asn_ipv6'], self.chamacoco.number)
        self.assertEqual(context['ip_opened'], 2)
        self.assertEqual(context['ipv4_name'], 'Chamacoco')
        self.assertEqual(context['ipv6_name'], 'Chamacoco')

        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_ip_informations_by_click__ip_views',
                args=[
                    self.sp.code]) +
            '?ipv4=' +
            self.ipv4_sp_terena.address +
            '&ipv6=' +
            self.ipv6_sp_terena.address +
            '&ip_opened=3')
        context = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context['asn_ipv4'], self.terena.number)
        self.assertEqual(context['asn_ipv6'], '')
        self.assertEqual(context['ip_opened'], 3)
        self.assertEqual(context['ipv4_name'], 'Terena')
        self.assertEqual(context['ipv6_name'], '')

    def test_get_match_ips_by_asn_search__ip_views(self):
        resp = self.c.generic(
            'GET', reverse('core:get_match_ips_by_asn_search__ip_views', args=[
                self.sp.code]) + '?asn=' + str(self.kinikinau.number))
        context_ip = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_ip['ipv4'], [self.ipv4_sp_kinikinau.address])
        self.assertEqual(context_ip['ipv6'], [])

        resp = self.c.generic(
            'GET', reverse('core:get_match_ips_by_asn_search__ip_views', args=[
                self.sp.code]) + '?asn=12')
        context_ip = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_ip['ipv4'], [])
        self.assertEqual(context_ip['ipv6'], [])

    def tearDown(self):
        super().tearDown()
