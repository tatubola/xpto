# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from ...models import IX, IPv6Address, MLPAv6
from ..login import DefaultLogin


class EditMLPAv6FormTestCase(TestCase):

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

        self.ix = mommy.make(IX, code='sp')
        self.ips_in_ix = mommy.make(IPv6Address, ix=self.ix, _quantity=10)
        self.ips_not_in_ix = mommy.make(IPv6Address, _quantity=10)

        self.mlpav6_services = [
            mommy.make(MLPAv6, mlpav6_address=self.ips_in_ix[0]),
            mommy.make(MLPAv6, mlpav6_address=self.ips_in_ix[1]),
            mommy.make(MLPAv6, mlpav6_address=self.ips_in_ix[2]), ]

        self.service = mommy.make(MLPAv6)

    def test_template(self):
        response = self.client.get(reverse("core:edit_mlpav6_form",
                                           args=[str(self.service.uuid),
                                                 self.ix.code]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('forms/edit_mlpav6_form.html')

    def test_correct_context(self):
        response = self.client.get(reverse("core:edit_mlpav6_form",
                                           args=[str(self.service.uuid),
                                                 self.ix.code]))

        self.assertEqual(response.context['service'], str(self.service.uuid))
        self.assertEqual(response.context['code'], self.ix.code)

        self.assertEqual(
            set(response.context['form'].fields['mlpav6_address'].queryset),
            set(self.ips_in_ix[3:10]))

    def test_edit_service(self):
        self.client.post(reverse('core:edit_mlpav6_form',
                                 args=[str(self.service.uuid),
                                       self.ix.code]),
                         {'mlpav6_address': self.ips_in_ix[8].address})

        new_service = MLPAv6.objects.get(pk=self.service.pk)
        self.assertEqual(new_service.mlpav6_address, self.ips_in_ix[8])
