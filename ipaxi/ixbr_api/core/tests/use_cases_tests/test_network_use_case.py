from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import Client
from model_mommy import mommy

from ...use_cases.network_use_cases import (
    next_switch, bfs_switch, get_pe_channel_by_channel)
from ...models import (DownlinkChannel, UplinkChannel, Switch, Port, User)


class SwitchUseCasesTest(TestCase):

    def setUp(self):

        self.user = User.objects.get_or_create(
            name='testuser', email="testuser@nic.br", password="testuser")[0]
        patcher = patch('ixbr_api.core.models.get_current_user')
        self.addCleanup(patcher.stop)

        self.get_user_mock = patcher.start()
        self.get_user_mock.return_value = self.user

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_tag_by_channel_port')
        p.start()
        self.addCleanup(p.stop)

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.origin_switch = mommy.make(Switch)
        self.neighboor_a = mommy.make(Switch)
        self.neighboor_b = mommy.make(Switch)

        self.downlink_a = mommy.make(DownlinkChannel)
        self.uplink_a = mommy.make(UplinkChannel,
                                   downlink_channel=self.downlink_a)

        self.downlink_b = mommy.make(DownlinkChannel)
        self.uplink_b = mommy.make(UplinkChannel,
                                   downlink_channel=self.downlink_b)

        self.port_origin_a = mommy.make(Port,
                                        switch=self.origin_switch,
                                        channel_port=self.uplink_a.channel_port)

        self.port_origin_b = mommy.make(Port,
                                        switch=self.origin_switch,
                                        channel_port=self.uplink_b.channel_port)

        self.port_neighboor_a = mommy.make(Port,
                                           switch=self.neighboor_a,
                                           channel_port=self.downlink_a.channel_port)

        self.port_neighboor_b = mommy.make(Port,
                                           switch=self.neighboor_b,
                                           channel_port=self.downlink_b.channel_port)

        self.neighboor_middle = mommy.make(Switch)
        self.neighboor_end = mommy.make(Switch,
                                   is_pe=True)

        self.downlink_middle = mommy.make(DownlinkChannel)
        self.uplink_origin = mommy.make(UplinkChannel,
                                   downlink_channel=self.downlink_middle)

        self.downlink_end = mommy.make(DownlinkChannel)
        self.uplink_middle = mommy.make(UplinkChannel,
                                   downlink_channel=self.downlink_end)

        self.port_origin = mommy.make(Port,
                                 switch=self.origin_switch,
                                 channel_port=self.uplink_origin.channel_port)

        self.port_middle_down = mommy.make(Port,
                                      switch=self.neighboor_middle,
                                      channel_port=self.downlink_middle.channel_port)

        self.port_middle_up = mommy.make(Port,
                                    switch=self.neighboor_middle,
                                    channel_port=self.uplink_middle.channel_port)

        self.port_end_down = mommy.make(Port,
                                   switch=self.neighboor_end,
                                   channel_port=self.downlink_end.channel_port)

    def test_next_switch(self):

        tested_function = next_switch(switch=self.origin_switch)

        self.assertIn((self.neighboor_a, self.downlink_a), tested_function)
        self.assertIn((self.neighboor_b, self.downlink_b), tested_function)

    def test_bfs_switch(self):

        tested_function = bfs_switch(origin_vertex=self.origin_switch)

        self.assertEqual((self.neighboor_end, self.downlink_end), tested_function)

    def test_get_pe_channel_by_channel(self):

        tested_function = get_pe_channel_by_channel(
            channel=self.uplink_origin, ix=self.port_origin.switch.pix.ix)

        self.assertEqual(self.downlink_end, tested_function)
