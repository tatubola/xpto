from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from invoice_api.core.models import Participante


class ParticipanteTests(APITestCase):

    def setUp(self):
        self.objects_quantity = 12
        mommy.make(Participante, _quantity=self.objects_quantity)

    def test_get(self):
        url = reverse('api:participante-list',)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.objects_quantity)

    '''TODO: Arrumar lookup de uuid para asn
    def test_get_one_by_asn(self):
        participante = mommy.make(Participante, asn="20200")
        url = reverse(
            'api:participante-detail', kwargs={'asn': participante.asn})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asn'], participante.asn)'''
