from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from ...models import ContactsMap, MLPAv4, Tag
from ...use_cases.service_use_case import delete_service_use_case
from ..login import DefaultLogin


class ServiceUseCaseTest(TestCase):

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

    def test_delete_service_use_case(self):
        tag = mommy.make(Tag, status='PRODUCTION')
        contacts_map = mommy.make(ContactsMap)
        service_mlpav4 = mommy.make(MLPAv4, tag=tag, make_m2m=True)
        service_mlpav4.asn.contactsmap_set.add(contacts_map)

        self.assertEqual(MLPAv4.objects.filter(pk=service_mlpav4.pk).count(), 1)

        delete_service_use_case(pk=service_mlpav4.pk)

        self.assertEqual(MLPAv4.objects.filter(pk=service_mlpav4.pk).count(), 0)

    def test_fail_delete_service_use_case(self):
        tag = mommy.make(Tag, status='PRODUCTION')
        contacts_map = mommy.make(ContactsMap)
        service_mlpav4 = mommy.make(MLPAv4, tag=tag, make_m2m=True)
        service_mlpav4.asn.contactsmap_set.add(contacts_map)

        self.assertEqual(MLPAv4.objects.filter(pk=service_mlpav4.pk).count(), 1)

        with self.assertRaisesMessage(ValidationError, "Invalid service primary key"):
            delete_service_use_case(pk=tag.pk)

        self.assertEqual(MLPAv4.objects.filter(pk=service_mlpav4.pk).count(), 1)
