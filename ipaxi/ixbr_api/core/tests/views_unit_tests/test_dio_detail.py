# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from ixbr_api.core.models import DIO, IX, PIX, DIOPort, Port

from ..login import DefaultLogin


class DioViewTestCase(TestCase):
    @patch('ixbr_api.core.models.DIO.objects.get')
    def setUp(self, mock_dio):
        DefaultLogin.__init__(self)

        self.ix = IX(code='cpv')
        self.pix = PIX(uuid='a798a305-9d99-4c39-a330-6891b2e81f22', ix=self.ix)
        self.dio = DIO(uuid='b05f6df4-4d39-4229-930a-a82feea213a5',
                       name='teste123456', pix=self.pix)
        self.port = Port(name='1')

        self.dio_port = DIOPort(dio=self.dio,
                                switch_port=self.port,
                                ix_position='rj12345678',
                                datacenter_position='cpv12345678')

        mock_dio.return_value = self.dio

        self.response = self.client.get(
            reverse('core:dio_detail',
                    kwargs={'dio': self.dio.uuid}))

    def test_dio_view_template(self):
        """Test that the DIOView returns a 200
        response and uses the correct template.
        """
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core:dio_detail.html')

    def test_dio_view_context(self):
        """Test if the correct context is sent to the template.
        """
        dio = self.response.context['dio']
        self.assertEqual(dio, self.dio)
