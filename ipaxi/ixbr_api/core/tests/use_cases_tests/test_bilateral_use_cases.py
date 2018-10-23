from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ...models import (ASN, IX, Bilateral, CustomerChannel, DownlinkChannel,
                       Port, Switch, Tag, UplinkChannel)
from ...use_cases.bilateral_use_case import (create_bilateral_a_b_qinq,
                                             create_bilateral_not_qinq,
                                             create_bilateral_peer_a_qinq,
                                             create_bilateral_peer_b_qinq,
                                             define_bilateral_case)
from ..login import DefaultLogin


class TestBilateralUseCases(TestCase):

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

        p = patch(
            'ixbr_api.core.models.Switch.full_clean')
        self.addCleanup(p.stop)
        p.start()

        self.ix = mommy.make(
            IX,
            tags_policy='distributed',
            create_tags=False)

        self.origin_switch = mommy.make(
            Switch,
            pix__ix=self.ix)
        self.neighboor_middle = mommy.make(
            Switch,
            pix__ix=self.ix)
        self.neighboor_end = mommy.make(
            Switch,
            pix__ix=self.ix,
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

        self.available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=12,
            tag_domain=self.downlink_end.channel_port,
            status='AVAILABLE')

        self.peer_a_asn = mommy.make(ASN)
        self.peer_b_asn = mommy.make(ASN)
        self.peer_c_asn = mommy.make(ASN)

    def test_define_bilateral_case(self):

        channel_peer_a = mommy.make(
            CustomerChannel,
            asn=self.peer_a_asn,
            cix_type=0)
        channel_peer_b = mommy.make(
            CustomerChannel,
            asn=self.peer_b_asn,
            cix_type=0)

        with self.assertRaisesMessage(ValueError, "Two channels must be given"):
            define_bilateral_case(channel_a=channel_peer_a)

        with self.assertRaisesMessage(ValueError, "Two channels must be given"):
            define_bilateral_case(channel_b=channel_peer_b)

        case = define_bilateral_case(
            channel_a=channel_peer_a,
            channel_b=channel_peer_b)

        self.assertEqual(case, 0)

        channel_peer_a.cix_type = 3

        case = define_bilateral_case(
            channel_a=channel_peer_a,
            channel_b=channel_peer_b)

        self.assertEqual(case, 1)

        channel_peer_a.cix_type = 0
        channel_peer_b.cix_type = 3

        case = define_bilateral_case(
            channel_a=channel_peer_a,
            channel_b=channel_peer_b)

        self.assertEqual(case, 2)

        channel_peer_a.cix_type = 3
        channel_peer_b.cix_type = 3

        case = define_bilateral_case(
            channel_a=channel_peer_a,
            channel_b=channel_peer_b)

        self.assertEqual(case, 3)

        channel_peer_a.cix_type = 1
        channel_peer_b.cix_type = 2

        case = define_bilateral_case(
            channel_a=channel_peer_a,
            channel_b=channel_peer_b)

        self.assertEqual(case, 0)

    def test_create_bilateral_not_qinq(self):

        channel_peer_a = mommy.make(
            CustomerChannel,
            asn=self.peer_a_asn,
            cix_type=0)
        channel_peer_b = mommy.make(
            CustomerChannel,
            asn=self.peer_b_asn,
            cix_type=0)
        port_peer_a = mommy.make(
            Port,
            switch=self.origin_switch,
            channel_port=channel_peer_a.channel_port)
        port_peer_b = mommy.make(
            Port,
            switch=self.neighboor_end,
            channel_port=channel_peer_b.channel_port)

        b_available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=12,
            tag_domain=channel_peer_b.channel_port,
            status='AVAILABLE')

        bilateral = create_bilateral_not_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=channel_peer_a,
            channel_b=channel_peer_b,
            ix=self.ix,
            tag_a=self.available_tag.tag,
            ticket=0,
            b_type="L2")
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))

    def test_create_bilateral_peer_b_qinq(self):

        channel_peer_a = mommy.make(
            CustomerChannel,
            asn=self.peer_a_asn,
            cix_type=0)
        channel_peer_c = mommy.make(
            CustomerChannel,
            asn=self.peer_c_asn,
            cix_type=3)
        port_peer_a = mommy.make(
            Port,
            switch=self.origin_switch,
            channel_port=channel_peer_a.channel_port)
        port_peer_c = mommy.make(
            Port,
            switch=self.neighboor_end,
            channel_port=channel_peer_c.channel_port)

        c_available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=44,
            tag_domain=channel_peer_c.channel_port,
            status='AVAILABLE')

        inner_b = self.available_tag.tag
        bilateral = create_bilateral_peer_b_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=channel_peer_a,
            channel_b=channel_peer_c,
            ix=self.ix,
            tag_a=self.available_tag.tag,
            tag_b=c_available_tag.tag,
            ticket=0,
            b_type="L2",
            inner_b=str(inner_b))
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))
        self.assertEqual(
            Bilateral.objects.filter(pk=bilateral.pk).first().peer_b.inner, inner_b)

    def test_create_bilateral_peer_a_qinq(self):

        channel_peer_b = mommy.make(
            CustomerChannel,
            asn=self.peer_a_asn,
            cix_type=0)
        channel_peer_c = mommy.make(
            CustomerChannel,
            asn=self.peer_c_asn,
            cix_type=3)
        port_peer_b = mommy.make(
            Port,
            switch=self.origin_switch,
            channel_port=channel_peer_b.channel_port)
        port_peer_c = mommy.make(
            Port,
            switch=self.neighboor_end,
            channel_port=channel_peer_c.channel_port)

        c_available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=44,
            tag_domain=channel_peer_c.channel_port,
            status='AVAILABLE')

        inner_a = self.available_tag.tag
        bilateral = create_bilateral_peer_a_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=channel_peer_c,
            channel_b=channel_peer_b,
            ix=self.ix,
            tag_b=self.available_tag.tag,
            tag_a=c_available_tag.tag,
            ticket=0,
            b_type="L2",
            inner_a=str(inner_a))
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))
        self.assertEqual(
            Bilateral.objects.filter(pk=bilateral.pk).first().peer_a.inner, inner_a)


class TestBilateralUseCases_test_create_bilateral_a_b_qinq(TestCase):
    def setUp(self):
        TestBilateralUseCases.setUp(self)
        peer_d_asn = mommy.make(ASN)

        self.channel_peer_d = mommy.make(
            CustomerChannel,
            asn=peer_d_asn,
            cix_type=3)
        self.channel_peer_c = mommy.make(
            CustomerChannel,
            asn=self.peer_c_asn,
            cix_type=3)
        port_peer_d = mommy.make(
            Port,
            switch=self.origin_switch,
            channel_port=self.channel_peer_d.channel_port)
        port_peer_c = mommy.make(
            Port,
            switch=self.neighboor_end,
            channel_port=self.channel_peer_c.channel_port)

        self.c_available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=44,
            tag_domain=self.channel_peer_c.channel_port,
            status='AVAILABLE')

        self.d_available_tag = mommy.make(
            Tag,
            ix=self.ix,
            tag=300,
            tag_domain=self.channel_peer_d.channel_port,
            status='AVAILABLE')

    def test_inner_a_and_b_filled(self):
        inner_a = 1010
        inner_b = 1010
        bilateral = create_bilateral_a_b_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=self.channel_peer_c,
            channel_b=self.channel_peer_d,
            ix=self.ix,
            tag_a=self.c_available_tag.tag,
            tag_b=self.d_available_tag.tag,
            ticket=0,
            b_type="L2",
            inner_a=inner_a,
            inner_b=inner_b)
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))
        self.assertEqual(
            Bilateral.objects.filter(
                pk=bilateral.pk).first().peer_a.inner, inner_a)

    def test_inner_a_filled_and_inner_b_is_none(self):
        inner_a = 1010
        inner_b = None
        bilateral = create_bilateral_a_b_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=self.channel_peer_c,
            channel_b=self.channel_peer_d,
            ix=self.ix,
            tag_a=self.c_available_tag.tag,
            tag_b=self.d_available_tag.tag,
            ticket=0,
            b_type="L2",
            inner_a=inner_a,
            inner_b=inner_b)
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))
        self.assertEqual(
            Bilateral.objects.filter(
                pk=bilateral.pk).first().peer_a.inner, inner_a)

    def test_inner_b_filled_and_inner_a_is_none(self):
        inner_a = None
        inner_b = 1010
        bilateral = create_bilateral_a_b_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=self.channel_peer_c,
            channel_b=self.channel_peer_d,
            ix=self.ix,
            tag_a=self.c_available_tag.tag,
            tag_b=self.d_available_tag.tag,
            ticket=0,
            b_type="L2",
            inner_a=inner_a,
            inner_b=inner_b)
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))
        self.assertEqual(
            Bilateral.objects.filter(
                pk=bilateral.pk).first().peer_a.inner, inner_a)

    def test_inner_a_and_b_are_none(self):
        inner_a = None
        inner_b = None
        bilateral = create_bilateral_a_b_qinq(
            peer_a=self.peer_a_asn,
            peer_b=self.peer_b_asn,
            channel_a=self.channel_peer_c,
            channel_b=self.channel_peer_d,
            ix=self.ix,
            tag_a=self.c_available_tag.tag,
            tag_b=self.d_available_tag.tag,
            ticket=0,
            b_type="L2",
            inner_a=inner_a,
            inner_b=inner_b)
        self.assertTrue(
            Bilateral.objects.filter(pk=bilateral.pk))
        self.assertEqual(
            Bilateral.objects.filter(
                pk=bilateral.pk).first().peer_a.inner, inner_a)
