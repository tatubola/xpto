from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import (IX, PIX, CoreChannel, DownlinkChannel, Port, Switch,
                       UplinkChannel)
from ...use_cases.channels_use_cases import (create_core_channel_use_case,
                                             create_uplink_channel_use_case,
                                             create_uplink_core_channel_use_case)
from ...utils.constants import SWITCH_MODEL_CHANNEL_PREFIX
from ..login import DefaultLogin


class TestChannelsUseCases(TestCase):

    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.ix = mommy.make(IX)
        self.pix = mommy.make(
            PIX,
            ix=self.ix)

        self.switch_origin = mommy.make(
            Switch,
            is_pe=False,
            pix=self.pix,
            model__vendor='EXTREME')

        self.switch_dest = mommy.make(
            Switch,
            is_pe=False,
            pix=self.pix,
            model__vendor='EXTREME')

        self.port_origin_a = mommy.make(
            Port,
            switch=self.switch_origin,
            name='1')
        self.port_origin_b = mommy.make(
            Port,
            switch=self.switch_origin,
            name='2',)

        self.port_dest_a = mommy.make(
            Port,
            switch=self.switch_dest,
            name='1')
        self.port_dest_b = mommy.make(
            Port,
            switch=self.switch_dest,
            name='2')

        self.ticket = 0

    def test_create_uplink_channel_use_case(self):

        channel_orgin_name = self.port_origin_a.name
        channel_dest_name = self.port_dest_a.name

        uplink, downlink = create_uplink_channel_use_case(
            origin_ports=[self.port_origin_a,
                          self.port_origin_b],
            dest_ports=[self.port_dest_a,
                        self.port_dest_b],
            channel_origin_name=channel_orgin_name,
            channel_dest_name=channel_dest_name,
            create_tags=False,
            ticket=self.ticket)

        test_uplink = UplinkChannel.objects.filter(
            name='ul-{0}'.format(channel_orgin_name))[0]

        test_downlink = DownlinkChannel.objects.filter(
            name='dl-{0}'.format(channel_dest_name))[0]

        self.assertEqual(uplink, test_uplink.pk)
        self.assertEqual(downlink, test_downlink.pk)

    def test_create_core_channel_use_case(self):

        self.switch_origin.model.vendor = 'CISCO'
        self.switch_origin.is_pe = True
        self.switch_dest.model.vendor = 'CISCO'
        self.switch_dest.is_pe = True

        self.switch_dest.save()
        self.switch_origin.save()

        channel_orgin_name = SWITCH_MODEL_CHANNEL_PREFIX['CISCO'] + '1100'
        channel_dest_name = SWITCH_MODEL_CHANNEL_PREFIX['CISCO'] + '1101'

        core_origin, core_dest = create_core_channel_use_case(
            origin_ports=[self.port_origin_a,
                          self.port_origin_b],
            dest_ports=[self.port_dest_a,
                        self.port_dest_b],
            channel_origin_name=channel_orgin_name,
            channel_dest_name=channel_dest_name,
            create_tags=False,
            ticket=self.ticket)

        test_core_origin = CoreChannel.objects.filter(
            name='cc-{0}'.format(channel_orgin_name))[0]

        test_core_dest = CoreChannel.objects.filter(
            name='cc-{0}'.format(channel_dest_name))[0]

        self.assertEqual(core_origin, test_core_origin.pk)
        self.assertEqual(core_dest, test_core_dest.pk)
        self.assertEqual(test_core_origin.other_core_channel.pk, core_dest)
        self.assertEqual(test_core_dest.other_core_channel.pk, core_origin)

    def test_create_uplink_core_channel_use_case(self):

        channel_orgin_name = self.port_origin_a.name
        channel_dest_name = self.port_dest_a.name

        uplink, downlink = create_uplink_core_channel_use_case(
            origin_ports=[self.port_origin_a,
                          self.port_origin_b],
            dest_ports=[self.port_dest_a,
                        self.port_dest_b],
            channel_origin_name=channel_orgin_name,
            channel_dest_name=channel_dest_name,
            create_tags=False,
            ticket=self.ticket,
            channel_type='UPLINK')

        test_uplink = UplinkChannel.objects.filter(
            name='ul-{0}'.format(channel_orgin_name))[0]

        test_downlink = DownlinkChannel.objects.filter(
            name='dl-{0}'.format(channel_dest_name))[0]

        self.assertEqual(uplink, test_uplink.pk)
        self.assertEqual(downlink, test_downlink.pk)

        self.switch_origin.model.vendor = 'CISCO'
        self.switch_origin.is_pe = True
        self.switch_dest.model.vendor = 'CISCO'
        self.switch_dest.is_pe = True

        self.switch_dest.save()
        self.switch_origin.save()

        channel_orgin_name = SWITCH_MODEL_CHANNEL_PREFIX['CISCO'] + '1100'
        channel_dest_name = SWITCH_MODEL_CHANNEL_PREFIX['CISCO'] + '1101'

        core_origin, core_dest = create_uplink_core_channel_use_case(
            origin_ports=[self.port_origin_a,
                          self.port_origin_b],
            dest_ports=[self.port_dest_a,
                        self.port_dest_b],
            channel_origin_name=channel_orgin_name,
            channel_dest_name=channel_dest_name,
            create_tags=False,
            ticket=self.ticket,
            channel_type='CORE')

        test_core_origin = CoreChannel.objects.filter(
            name='cc-{0}'.format(channel_orgin_name))[0]

        test_core_dest = CoreChannel.objects.filter(
            name='cc-{0}'.format(channel_dest_name))[0]

        self.assertEqual(core_origin, test_core_origin.pk)
        self.assertEqual(core_dest, test_core_dest.pk)
        self.assertEqual(test_core_origin.other_core_channel.pk, core_dest)
        self.assertEqual(test_core_dest.other_core_channel.pk, core_origin)
        self.assertEqual(self.port_origin_a.status, 'INFRASTRUCTURE')
        self.assertEqual(self.port_origin_b.status, 'INFRASTRUCTURE')
        self.assertEqual(self.port_dest_a.status, 'INFRASTRUCTURE')
        self.assertEqual(self.port_dest_b.status, 'INFRASTRUCTURE')
