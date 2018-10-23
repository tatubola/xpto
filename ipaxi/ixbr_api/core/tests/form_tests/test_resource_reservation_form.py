""" This test the reservation of some resources to perform migrations
"""

# System Imports
from unittest.mock import patch

# Third-party Imports
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

# Local source tree Imports
from ixbr_api.core.models import (IPv4Address, IPv6Address, Port, IX, Tag)
from ..login import DefaultLogin


class ReserveResource(TestCase):
    def setUp(self):
        DefaultLogin.__init__(self)

        p = patch('ixbr_api.core.models.HistoricalTimeStampedModel.full_clean')
        p.start()
        self.addCleanup(p.stop)

        p = patch('ixbr_api.core.models.create_all_ips')
        p.start()
        self.addCleanup(p.stop)

        self.ix = mommy.make(IX, code='sp')
        self.tags = mommy.make(Tag, ix=self.ix, status='AVAILABLE', _quantity=1)
        self.port = mommy.make(Port, configured_capacity=100, capacity=40000)

    def test_IPv4_resource_reserved_modification(self):
        """
        Creates a reserved IPv4 resource and tries to edit it

        Returns:

        """

        self.ipsv4_in_ix = mommy.make(IPv4Address, ix=self.ix, _quantity=1)
        self.ipsv4_in_ix[0].reserve_this()
        self.ipsv4_in_ix[0].last_ticket = 1122
        with self.assertRaises(ValidationError):
            self.ipsv4_in_ix[0].save()

    def test_IPv6_resource_reserved_modification(self):
        """
        Creates a reserved IPv4 resource and tries to edit it

        Returns:

        """
        self.ipsv6_in_ix = mommy.make(IPv6Address, ix=self.ix, _quantity=1)
        self.ipsv6_in_ix[0].reserve_this()
        self.ipsv6_in_ix[0].last_ticket = 1122
        with self.assertRaises(ValidationError):
            self.ipsv6_in_ix[0].save()

    def test_port_resource_reserved_modification(self):
        """
        Tries to edit a reserved Port

        Returns:

        """
        self.port.reserve_this()
        self.port.last_ticket = 1122
        with self.assertRaises(ValidationError):
            self.port.save()

    def test_vlan_resource_reserved_modification(self):
        """
        Creates a reserved Vlan Tag resource and tries to edit it

        Returns:

        """
        self.tags[0].reserve_this()
        self.tags[0].last_ticket = 1122
        with self.assertRaises(ValidationError):
            self.tags[0].save()

    def test_IPv4_resource_reserved_deletion(self):
        """
        Tries to delete a reserved resource

        Returns:

        """
        self.ipsv4_in_ix = mommy.make(IPv4Address, ix=self.ix, _quantity=1)
        self.ipsv4_in_ix[0].reserve_this()
        with self.assertRaises(ValidationError):
            self.ipsv4_in_ix[0].delete()

    def test_IPv6_resource_reserved_deletion(self):
        """
        Tries to delete a reserved resource

        Returns:

        """
        self.ipsv6_in_ix = mommy.make(IPv6Address, ix=self.ix, _quantity=1)
        self.ipsv6_in_ix[0].reserve_this()
        with self.assertRaises(ValidationError):
            self.ipsv6_in_ix[0].delete()

    def test_Port_resource_reserved_deletion(self):
        """
        Tries to delete a reserved resource

        Returns:

        """
        self.port.reserve_this()
        with self.assertRaises(ValidationError):
            self.port.delete()


    def test_Tag_resource_reserved_deletion(self):
        """
        Tries to delete a reserved resource

        Returns:

        """
        self.tags[0].reserve_this()
        with self.assertRaises(ValidationError):
            self.tags[0].delete()
