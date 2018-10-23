# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import DIO, IX, PIX

from ..login import DefaultLogin


class DioListViewTestCase(TestCase):
    @patch('ixbr_api.core.models.DIO.objects.filter')
    @patch('ixbr_api.core.models.PIX.objects.get')
    def setUp(self, mock_pix, mock_dio):
        DefaultLogin.__init__(self)
        self.ix = IX(code='sp')
        self.pix = PIX(uuid='935a7a78-4eb3-407c-bea9-591d6f6593cd')

        mock_dio.return_value = [DIO(name="DIO test 1", pix=self.pix),
                                 DIO(name="DIO test 2", pix=self.pix),
                                 DIO(name="DIO test 3", pix=self.pix)]

        mock_pix.return_value = self.pix

        self.response = self.client.get(
            reverse('core:dio_list',
                    kwargs={'code': self.ix.code, 'pix': self.pix.uuid}))

    def test_dio_list_template(self):
        """Test that the DIOListView returns a 200
        response, uses the correct template, and has the
        correct context."""
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core/dio_list.html')

    def test_dio_list_context(self):
        """Test if the correct context is sent to the template"""
        pix = self.response.context['pix']
        self.assertEqual(pix, self.pix)
