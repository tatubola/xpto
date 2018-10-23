from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy
from rest_framework.reverse import reverse as api_reverse
from rest_framework import status

from ixbr_api.core.models import (ASN, Bilateral, IX)
from ixbr_api.core.tests.login import DefaultLogin


class Test_Bilateral_API(TestCase):
    """Tests Bilateral Endpoint."""

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

    def test_post(self):
        ix = mommy.make(IX, code='jpa')
        asn = mommy.make(ASN, number=1)
        url = api_reverse("api:bilateral-list", kwargs={
                          "code": ix.code, "asn": asn.number})

        data = {"last_ticket": 42, "modified_by": self.superuser,
                "description": "awesome description"}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_list(self):
        ix = mommy.make(IX, code='jpa')
        asn = mommy.make(ASN, number=1)
        url = api_reverse("api:bilateral-list", kwargs={
                          "code": ix.code, "asn": asn.number})

        mommy.make(Bilateral, label="a", peer_a__asn=asn, peer_a__tag__ix=ix)
        mommy.make(Bilateral, label="b", peer_b__asn=asn, peer_b__tag__ix=ix)

        response = self.client.get(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['label'], "a")
        self.assertEqual(response.data[1]['label'], "b")

    def test_search(self):
        ix = mommy.make(IX, code='jpa')
        asn1 = mommy.make(ASN, number=1)
        asn2 = mommy.make(ASN, number=2)
        url = api_reverse("api:bilateral-list", kwargs={
                          "code": ix.code, "asn": asn1.number})

        mommy.make(Bilateral, label="a", peer_a__asn=asn1,
                   peer_b__asn=asn1, peer_a__tag__ix=ix,
                   peer_a__tag__tag=1, peer_b__tag__tag=3)
        mommy.make(Bilateral, label="b", peer_a__asn=asn1,
                   peer_b__asn=asn2, peer_b__tag__ix=ix,
                   peer_a__tag__tag=2, peer_b__tag__tag=4)

        response = self.client.get(
            "{url}?search=2".format(url=url), [], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['label'], "b")
