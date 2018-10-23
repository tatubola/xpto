from itertools import cycle
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq

from ixbr_api.core.models import (IX, PIX, DownlinkChannel, Port, Switch,
                                  SwitchModel, SwitchPortRange, Tag,)

from ...use_cases.channels_use_cases import create_uplink_channel_use_case
from ..login import DefaultLogin


class ReserveTagStatusFormTestCase(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch(
            'ixbr_api.core.models.create_all_ips')
        self.addCleanup(p.stop)
        p.start()

        p = patch(
            'ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.ix = mommy.make(IX, code='sp')

        self.tag = mommy.make(
            Tag,
            _quantity=4,
            ix=self.ix,
            tag=seq(4)
        )
        self.tag[0].reserve_this()
        self.tag[-1].reserve_this()

    def test_reserve_tag_recourse_form_when_status_code_200_and_context(self):
        request = self.client.get(
            reverse('core:reserve_tag_resource', args=[self.ix.code])
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.context['ix'], self.ix.code)
        self.assertTrue(request.context['form'].fields['tag_to_reserve'])

    def test_reserve_tag_recourse_form_without_bundle(self):
        self.assertEqual(self.tag[1].reserved, False)
        response = self.client.post(
            reverse('core:reserve_tag_resource', args=[self.ix.code]),
            {'tag_to_reserve': self.tag[1].pk}
        )
        tag_reserved = Tag.objects.get(uuid=self.tag[1].uuid)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(tag_reserved.reserved, True)

    def test_reserve_tag_recourse_form_with_bundle(self):
        pix = mommy.make(PIX)
        models = ['SLX9540', 'X470-48t', 'X470-48x']
        vendors = ['BROCADE', 'EXTREME', 'EXTREME']
        switch_model_set = mommy.make(
            SwitchModel,
            _quantity=len(models),
            vendor=cycle(vendors),
            model=cycle(models),
        )
        mommy.make(
            SwitchPortRange,
            _quantity=len(switch_model_set),
            switch_model=cycle(switch_model_set),
        )
        is_pe = [True, False, False]
        switch_set = mommy.make(
            Switch,
            model=cycle(switch_model_set),
            is_pe=cycle(is_pe),
            pix=pix,
            _quantity=len(switch_model_set),
            create_ports=False
        )
        port_set_brocade = mommy.make(
            Port,
            _quantity=2,
            status='AVAILABLE',
            switch=switch_set[0],
        )

        port_set_extreme_1 = mommy.make(
            Port,
            status='AVAILABLE',
            switch=switch_set[1],
            _quantity=2
        )
        origin, dest = create_uplink_channel_use_case(
            origin_ports=[port_set_extreme_1[0]],
            dest_ports=[port_set_brocade[0]],
            channel_origin_name='1',
            channel_dest_name='PC1',
            create_tags=False,
            ticket=1
        )
        channel_port = DownlinkChannel.objects.get(uuid=dest).channel_port
        tag_set = mommy.make(
            Tag,
            _quantity=4,
            tag=cycle(range(3, 7)),
            tag_domain=channel_port,
            ix=pix.ix,
        )
        tag_modified = Tag.objects.get(uuid=tag_set[0].uuid)
        self.assertEqual(tag_modified.reserved, False)

        response = self.client.post(
            '{}?bundle_pk={}'.format(
                reverse('core:reserve_tag_resource', args=[self.ix.code]),
                dest
            ),
            {'tag_to_reserve': tag_set[0].pk}
        )

        self.assertEqual(response.status_code, 302)

        tag_modified = Tag.objects.get(uuid=tag_set[0].uuid)
        self.assertEqual(tag_modified.reserved, True)
