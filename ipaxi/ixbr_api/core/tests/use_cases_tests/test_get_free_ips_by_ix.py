from itertools import cycle
from unittest.mock import patch

from django.test import TestCase
from ixbr_api.core.models import IX, IPv4Address, IPv6Address, MLPAv4, MLPAv6
from ixbr_api.core.tests.login import DefaultLogin
from ixbr_api.core.use_cases.get_free_ips_by_ix import get_free_ips_by_ix
from model_mommy import mommy


class TestGetFreeIPSByIX(TestCase):

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

        self.ix = mommy.make(
            IX,
            tags_policy='distributed',
            create_tags=False)

        self.ipv4_addresses = [
            '187.16.205.4',
            '187.16.205.5',
            '187.16.205.6',
            '187.16.205.7',
            ]

        self.ipv6_addresses = [
            '2001:12f8:0:28::4',
            '2001:12f8:0:28::5',
            '2001:12f8:0:28::6',
            '2001:12f8:0:28::7',
            '2001:12f8:0:28::8',
            '2001:12f8:0:28::9',
            ]

        self.ipv4_list = mommy.make(
            IPv4Address,
            _quantity=4,
            address=cycle(self.ipv4_addresses),
            ix=self.ix)

        self.ipv6_list = mommy.make(
            IPv6Address,
            _quantity=6,
            address=cycle(self.ipv6_addresses),
            ix=self.ix)

    @staticmethod
    def __allocate_ips(ip_list):
        for ip in ip_list:
            if type(ip) == IPv4Address:
                mommy.make(MLPAv4, mlpav4_address=ip)
            else:
                mommy.make(MLPAv6, mlpav6_address=ip)

    def test_ix_with_free_ips_only(self):
        ipv4 = mommy.make(IPv4Address, address='187.16.205.4', ix=self.ix)
        ipv6 = mommy.make(IPv6Address, address='2001:12f8:0:28::4', ix=self.ix)

        free_ips = get_free_ips_by_ix('v4_and_v6', self.ix)
        self.assertEqual({'ipv6': ipv6, 'ipv4': ipv4}, free_ips)

    def test_ix_with_some_allocated_ips_1(self):
        # Free:
        # 187.16.205.5, 187.16.205.6, 187.16.205.7
        # 2001:12f8:0:28::4, 2001:12f8:0:28::6, 2001:12f8:0:28::7
        # Expected suggestion:
        # 187.16.205.6, 2001:12f8:0:28::6
        TestGetFreeIPSByIX.__allocate_ips([self.ipv4_list[0], self.ipv6_list[1]])

        free_ips = get_free_ips_by_ix('v4_and_v6', self.ix)
        self.assertEqual(free_ips['ipv4'].address, self.ipv4_list[2].address)
        self.assertEqual(free_ips['ipv6'].address, self.ipv6_list[2].address)

    def test_get_recomendation_v4_v6_when_the_first_ones_are_used(self):

        # Free:
        # 187.16.205.5, 187.16.205.6, 187.16.205.7
        # 2001:12f8:0:28::6, 2001:12f8:0:28::7, 2001:12f8:0:28::9
        # Expected suggestion:
        # 187.16.205.6, 2001:12f8:0:28::6
        TestGetFreeIPSByIX.__allocate_ips([
            self.ipv4_list[0],  # .4
            self.ipv6_list[0],  # ::4
            self.ipv6_list[1],  # ::5
            self.ipv6_list[4],  # ::8
            ])

        free_ips = get_free_ips_by_ix('v4_and_v6', self.ix)
        self.assertEqual(free_ips['ipv4'].address, self.ipv4_list[2].address)
        self.assertEqual(free_ips['ipv6'].address, self.ipv6_list[2].address)

    def test_ix_with_some_allocated_ips_3(self):
        # Free:
        # 187.16.205.5, 187.16.205.7
        # 2001:12f8:0:28::6
        # Expected suggestion:
        # 187.16.205.5, 2001:12f8:0:28::6
        TestGetFreeIPSByIX.__allocate_ips([
            self.ipv4_list[0],
            self.ipv4_list[2],
            self.ipv4_list[3],
            self.ipv6_list[0],
            self.ipv6_list[1],
            ])
        free_ips = get_free_ips_by_ix('v4_and_v6', self.ix)
        self.assertEqual(free_ips['ipv4'].address, self.ipv4_list[1].address)
        self.assertEqual(free_ips['ipv6'].address, self.ipv6_list[2].address)

    def test_ix_with_some_allocated_ips_4(self):
        # Free:
        # 187.16.205.5, 187.16.205.7
        # 2001:12f8:0:28::5, 2001:12f8:0:28::7
        # Expected suggestion:
        # 187.16.205.5, 2001:12f8:0:28::5
        TestGetFreeIPSByIX.__allocate_ips([
            self.ipv4_list[0],
            self.ipv4_list[2],
            self.ipv6_list[0],
            self.ipv6_list[2],
            ])

        free_ips = get_free_ips_by_ix('v4_and_v6', self.ix)
        self.assertEqual({'ipv6': self.ipv6_list[1], 'ipv4': self.ipv4_list[1]},
                         free_ips)

    def test_ix_with_some_reserved_ips(self):
        # Free:
        # 187.16.205.7
        # 2001:12f8:0:28::7
        # Reserved
        # 187.16.205.5
        # 2001:12f8:0:28::5
        # Expected suggestion:
        # 187.16.205.7, 2001:12f8:0:28::7
        TestGetFreeIPSByIX.__allocate_ips([
            self.ipv4_list[0],
            self.ipv4_list[2],
            self.ipv6_list[0],
            self.ipv6_list[2],
            ])
        self.ipv4_list[1].reserve_this()
        self.ipv6_list[1].reserve_this()

        free_ips = get_free_ips_by_ix('v4_and_v6', self.ix)
        self.assertEqual(free_ips['ipv4'].address, self.ipv4_list[3].address)
        self.assertEqual(free_ips['ipv6'].address, self.ipv6_list[3].address)
