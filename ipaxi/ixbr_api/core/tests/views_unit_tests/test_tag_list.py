# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from ..makefaketestdata import MakeFakeTestData


class TagListViewTestBasics(TestCase):
    def setUp(self):
        MakeFakeTestData.__init__(self)
        # Instance a Request Factory
        self.response_without_bundle = self.client.get(
            reverse('core:tag_list_without_bundle', args=[self.cpv.code]))
        self.response_with_bundle = self.client.get(
            reverse('core:tag_list_with_bundle', args=[
                self.sp.code, self.downlink_channel_sp_kadiweu_1.uuid]))

        self.c = Client()


class TestTagListViewWithoutBundle(TagListViewTestBasics):
    def test_login(self):
        """ Check if is logged """
        self.assertTrue(self.login)

    def test_tag_views_basics(self):
        """Test that the TAGsListView returns a 200 response, uses
        the correct template, and has the correct context
        """
        self.assertEqual(200, self.response_without_bundle.status_code)
        self.assertTemplateUsed('core/tag_list.html')

    def test_tag_views_return(self):
        ix_code = self.response_without_bundle.context['ix'].code
        self.assertEqual(ix_code, self.cpv.code)
        tags = self.response_without_bundle.context['tags']
        self.assertEqual(tags[0].tag, self.tag_cpv_metuktire_v4_1.tag)
        self.assertEqual(tags[0].status, 'PRODUCTION')
        self.assertEqual(tags[1].tag, self.tag_cpv_metuktire_v4_2.tag)
        self.assertEqual(tags[1].status, 'PRODUCTION')
        self.assertEqual(tags[2].tag, self.tag_cpv_yudja.tag)
        self.assertEqual(tags[2].status, 'PRODUCTION')
        self.assertEqual(tags[3].tag, self.tag_cpv_metuktire_v6_1.tag)
        self.assertEqual(tags[3].status, 'PRODUCTION')
        self.assertEqual(tags[4].tag, self.tag_cpv_metuktire_v6_2.tag)
        self.assertEqual(tags[4].status, 'PRODUCTION')
        self.assertEqual(tags[5].tag, self.tag_cpv_kayapo_v4.tag)
        self.assertEqual(tags[5].status, 'PRODUCTION')
        self.assertEqual(tags[6].tag, self.tag_cpv_none_1.tag)
        self.assertEqual(tags[6].status, 'AVAILABLE')
        self.assertEqual(tags[7].tag, self.tag_cpv_kayapo_v6.tag)
        self.assertEqual(tags[7].status, 'PRODUCTION')

        bundle = self.response_without_bundle.context['bundle']
        self.assertEqual(bundle, '')
        switch = self.response_without_bundle.context['switch']
        self.assertEqual(switch, '')
        available_amount = self.response_without_bundle.context[
            'available_amount']
        self.assertEqual(available_amount, 1)
        production_amount = self.response_without_bundle.context[
            'production_amount']
        self.assertEqual(production_amount, 7)

    def test_get_tag_informations_by_click__tag_views(self):
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_tag_informations_by_click__tag_views',
                args=[
                    self.cpv.code]) +
            '?tag=' +
            str(self.tag_cpv_yudja.uuid))
        context_click = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_click['asn'], self.yudja.number)
        self.assertEqual(
            context_click['organization'], self.yudja_organization.name)
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_tag_informations_by_click__tag_views',
                args=[
                    self.cpv.code]) +
            '?tag=' +
            str(self.tag_cpv_none_1.uuid))
        context_click = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_click, {})

    def test_get_match_tags_by_asn_search__tag_views(self):
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_match_tags_by_asn_search__tag_views',
                args=[
                    self.cpv.code]) +
            '?asn=' +
            str(self.kayapo.number))
        context_search = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(
            context_search['organization'], self.kayapo_organization.name)
        self.assertEqual(context_search['tag'][0], self.tag_cpv_kayapo_v4.tag)
        self.assertEqual(context_search['tag'][1], self.tag_cpv_kayapo_v6.tag)
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_match_tags_by_asn_search__tag_views',
                args=[
                    self.cpv.code]) +
            '?asn=466')
        context_search = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_search, {})


class TestTagListViewWithBundle(TagListViewTestBasics):
    def test_login(self):
        """ Check if is logged """
        self.assertTrue(self.login)

    def test_tag_views_basics(self):
        """Test that the TAGsListView returns a 200 response, uses
        the correct template, and has the correct context
        """
        self.assertEqual(200, self.response_with_bundle.status_code)
        self.assertTemplateUsed('core/tag_list.html')

    def test_tag_views_return(self):
        ix_code = self.response_with_bundle.context['ix'].code
        self.assertEqual(ix_code, self.sp.code)
        tags = self.response_with_bundle.context['tags']
        self.assertEqual(tags[0].tag, self.tag_sp_chamacoco.tag)
        self.assertEqual(tags[0].status, 'ALLOCATED')
        self.assertEqual(tags[1].tag, self.tag_sp_kinikinau.tag)
        self.assertEqual(tags[1].status, 'PRODUCTION')
        self.assertEqual(tags[2].tag, self.tag_sp_none_1.tag)
        self.assertEqual(tags[2].status, 'AVAILABLE')
        self.assertEqual(tags[3].tag, self.tag_sp_none_2.tag)
        self.assertEqual(tags[3].status, 'AVAILABLE')
        ''' It is out of this bundle, if want to test this, please
            change the bundle into response.
        self.assertEqual(tags[4].tag, self.tag_sp_terena.tag)
        self.assertEqual(tags[4].status, 'PRODUCTION')'''
        bundle = self.response_with_bundle.context['bundle'].name
        self.assertEqual(bundle, self.downlink_channel_sp_kadiweu_1.name)
        switch = self.response_with_bundle.context['switch']
        self.assertEqual(switch.model, self.cisco_sp_kadiweu.model.model)
        available_amount = self.response_with_bundle.context[
            'available_amount']
        self.assertEqual(available_amount, 2)
        production_amount = self.response_with_bundle.context[
            'production_amount']
        self.assertEqual(production_amount, 1)

    def test_get_tag_informations_by_click__tag_views(self):
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_tag_informations_by_click__tag_views',
                args=[
                    self.sp.code]) +
            '?tag=' +
            str(self.tag_sp_kinikinau.uuid))
        context_click = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_click['asn'], self.kinikinau.number)
        self.assertEqual(
            context_click['organization'],
            self.kinikinau_organization.name)
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_tag_informations_by_click__tag_views',
                args=[
                    self.sp.code]) +
            '?tag=' +
            str(self.tag_cpv_none_1.uuid))
        context_click = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_click, {})

    def test_get_match_tags_by_asn_search__tag_views(self):
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_match_tags_by_asn_search__tag_views',
                args=[
                    self.sp.code]) +
            '?asn=' +
            str(self.terena.number))
        context_search = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(
            context_search['organization'], self.terena_organization.name)
        self.assertEqual(context_search['tag'][0], self.tag_sp_terena.tag)
        resp = self.c.generic(
            'GET',
            reverse(
                'core:get_match_tags_by_asn_search__tag_views',
                args=[
                    self.sp.code]) +
            '?asn=466')
        context_search = ast.literal_eval(resp.content.decode('UTF-8'))
        self.assertEqual(context_search, {})
