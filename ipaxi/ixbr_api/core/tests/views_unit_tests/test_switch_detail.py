# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from ixbr_api.users.models import User
from model_mommy import mommy

from ...models import ASN
from ..factories import (ChannelPortFactory, ContactsMapFactory,
                         CustomerChannelFactoryVanilla, DownlinkChannelFactory,
                         IPv4AddressFactory, IPv6AddressFactory, IXFactory,
                         MLPAv4Factory, MLPAv6Factory, OrganizationFactory,
                         PIXFactory, PortFactory, SwitchFactory,
                         SwitchModelFactory, SwitchPortRangeFactory,
                         TagFactory, UplinkChannelFactory)


class SwitchViewTestBasics(TestCase):
    def setUp(self):
        # create a superuser
        self.superuser = User.objects.create_superuser(
            email='superuser@ix.br',
            password='V&ryS@f3Pwd',
            name='Super User')
        patcher = patch('ixbr_api.core.models.get_current_user')
        self.addCleanup(patcher.stop)

        self.get_user_mock = patcher.start()
        self.get_user_mock.return_value = self.superuser

        # instance a state code
        self.create_models()
        # Log into application
        self.login = self.client.login(
            email='superuser@ix.br',
            password='V&ryS@f3Pwd')

    def create_models(self):
        self.ix = IXFactory(code='sp', management_prefix='192.168.0.0/24')
        self.pix = PIXFactory(ix=self.ix, code='Hansen')
        self.switch_model = SwitchModelFactory(model='ASR9922', vendor='CISCO')
        self.switch_port = SwitchPortRangeFactory(
            switch_model=self.switch_model,
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=27,
            name_format='TenGigE0/0/0/{0}')
        self.switch = SwitchFactory(
            pix=self.pix,
            uuid='2cf97cbf-8d11-46e7-b1f4-0078dc313001',
            management_ip='192.168.0.8',
            translation=False,
            model=self.switch_model)

        # Primer port
        self.asn = mommy.make(ASN, number=62000)
        self.organization = OrganizationFactory(
            shortname='smith', name='Smith Inc')
        self.contact = ContactsMapFactory(
            ix=self.ix,
            asn=self.asn,
            organization=self.organization)
        self.channel = ChannelPortFactory()
        self.port = PortFactory(
            channel_port=self.channel,
            status='UNAVAILABLE',
            switch=self.switch)
        self.channel.port_set.add(self.port)
        self.downlink = DownlinkChannelFactory(
            name='dl-BE1090',
            is_lag=False,
            channel_port=self.channel,)
        self.custommer = CustomerChannelFactoryVanilla(
            asn=self.asn,
            is_lag=False,
            name='ct-BE1080',
            channel_port=self.channel,
            ix=self.ix)
        self.port = PortFactory(
            switch=self.switch,
            name='TenGigE0/0/0/9',
            status='CUSTOMER',
            channel_port=self.channel,
            capacity=1000,
            connector_type='SFP+',
            physical_interface=None,
            uuid='49755292-43fa-4559-9314-9cb315a625f4')
        self.uuid_1 = self.port.uuid
        self.ipv4 = IPv4AddressFactory(ix=self.ix, address='10.0.3.243')
        self.tag_1 = TagFactory(
            ix=self.ix,
            tag=4072,
            tag_domain_id=self.channel.uuid)
        self.mlpav4 = MLPAv4Factory(
            inner=76,
            status='QUARANTINE',
            shortname='as62000-mlpav4',
            mlpav4_address=self.ipv4,
            asn=self.asn,
            customer_channel=self.custommer,
            tag=self.tag_1)
        self.ipv6 = IPv6AddressFactory(ix=self.ix, address='2001:12f0::3:243')
        self.tag_2 = TagFactory(
            ix=self.ix, tag=4071, tag_domain_id=self.channel.uuid)
        self.mlpav6 = MLPAv6Factory(
            inner=1089, status='QUARANTINE',
            shortname='as62000-mlpav6',
            mlpav6_address=self.ipv6,
            asn=self.asn,
            customer_channel=self.custommer,
            tag=self.tag_2)

        # Second port
        self.channel = ChannelPortFactory()
        self.port = PortFactory(
            channel_port=self.channel,
            status='UNAVAILABLE',
            switch=self.switch)
        self.channel.port_set.add(self.port)
        self.uuid_down = self.downlink.uuid
        self.uplink = UplinkChannelFactory(
            name='ul-BE1030', is_lag=False,
            is_mclag=False, channel_port=self.channel,
            downlink_channel=self.downlink)
        self.port = PortFactory(
            switch=self.switch, name='TenGigE0/0/0/1',
            status='INFRASTRUCTURE', channel_port=self.channel,
            capacity=1000, connector_type='SFP+', physical_interface=None)
        self.uuid_2 = self.port.uuid
        self.downlink = DownlinkChannelFactory(
            name='dl-BE1090',
            is_lag=False,
            channel_port=self.channel,
            uuid='98f26186-7cf9-4e52-8fe7-be80b28b7d43')
        self.name_pix = self.port.channel_port.uplinkchannel.\
            downlink_channel.channel_port.port_set.first().switch.pix
        self.management_ip = self.port.channel_port.uplinkchannel.\
            downlink_channel.channel_port.port_set.first().switch.management_ip

        # Tercer port
        self.port = PortFactory(
            switch=self.switch, name='TenGigE0/0/0/21',
            capacity=1000, connector_type='SFP+',
            physical_interface=None,
            uuid='dcaba642-e580-41ca-bbda-5c042bd7ac48')
        self.uuid_3 = self.port.uuid

        # 4 Port
        self.asn = mommy.make(ASN, number=28630)
        self.organization = OrganizationFactory(
            shortname='mcintosh',
            name='Mcintosh, Cummings and Garcia')
        self.contact = ContactsMapFactory(
            ix=self.ix, asn=self.asn, organization=self.organization)
        self.channel = ChannelPortFactory()
        self.port = PortFactory(
            channel_port=self.channel,
            status='UNAVAILABLE',
            switch=self.switch)
        self.channel.port_set.add(self.port)
        self.downlink = DownlinkChannelFactory(
            name='dl-BE1090', is_lag=False,
            channel_port=self.channel)
        self.custommer = CustomerChannelFactoryVanilla(
            asn=self.asn, is_lag=True, name='ct-BE1080',
            channel_port=self.channel, ix=self.ix)
        self.port = PortFactory(
            switch=self.switch, name='TenGigE0/0/0/6',
            status='CUSTOMER', channel_port=self.channel,
            capacity=1000, connector_type='SFP+', physical_interface=None,
            uuid='eec02e65-245e-47cb-bef8-4ca43ce4e522')
        self.uuid_4 = self.port.uuid
        self.port = PortFactory(
            switch=self.switch, name='TenGigE0/0/0/7',
            status='CUSTOMER', channel_port=self.channel,
            capacity=1000, connector_type='SFP+',
            physical_interface=None,
            uuid='3f0643b6-130f-4911-8ac9-7a0d865f763c')
        self.ipv4 = IPv4AddressFactory(ix=self.ix, address='10.0.3.245')
        self.tag_1 = TagFactory(
            ix=self.ix, tag=4076, tag_domain_id=self.channel.uuid)
        self.mlpav4 = MLPAv4Factory(
            inner=76, status='ALLOCATED',
            shortname='as28630-mlpav4', mlpav4_address=self.ipv4,
            asn=self.asn, customer_channel=self.custommer, tag=self.tag_1)
        self.ipv6 = IPv6AddressFactory(ix=self.ix, address='2001:12f0::3:245')
        self.tag_2 = TagFactory(
            ix=self.ix, tag=4075, tag_domain_id=self.channel.uuid)
        self.mlpav6 = MLPAv6Factory(
            inner=1089, status='ALLOCATED',
            shortname='as28630-mlpav6', mlpav6_address=self.ipv6,
            asn=self.asn, customer_channel=self.custommer, tag=self.tag_2)
        self.lags = self.port.channel_port.port_set.all().values_list('name')

    def test_ports_basics(self):
        """Test that the solo view returns a 200 response, uses
        the correct template, and has the correct context
        """
        # Instance a Request Factory
        self.response = self.client.get(reverse(
            'core:switch_detail', args=[self.ix.code, self.switch.uuid]))
        self.assertEqual(200, self.response.status_code)
        self.assertTemplateUsed('core/switch_detail.html')
