# ##############################################
# ################# IMPORTANT ##################
# ##############################################
# Take care of change any parameter in this file
# because it can affect other tests. If you need
# make any change certify where it has been used
# and update these tests too. (‾ʖ̫‾)

from unittest.mock import patch

from ixbr_api.users.models import User

from ..models import (ASN, DIO, IX, PIX, Bilateral, BilateralPeer,
                      ChannelPort, Contact, ContactsMap, CoreChannel,
                      CustomerChannel, DIOPort, DownlinkChannel, IPv4Address,
                      IPv6Address, MACAddress, MLPAv4, MLPAv6, Monitorv4,
                      Organization, Phone, PhysicalInterface, Port, Switch,
                      SwitchModel, SwitchPortRange, Tag, UplinkChannel,)


class GeneralSettings(object):
    def __init__(self):
        # ###########################################
        # ############ General Settings #############
        # ###########################################
        # Its is general settings that are used to create first settings
        self.superuser = User.objects.create_superuser(
            email='tupi@ix.br',
            password='tUp1Gu4r4n1',
            name='Joseph Mallord William Turner ')
        patcher = patch('ixbr_api.core.models.get_current_user')
        self.addCleanup(patcher.stop)

        self.get_user_mock = patcher.start()
        self.get_user_mock.return_value = self.superuser

        # Log into application
        self.login = self.client.login(
            email='tupi@ix.br',
            password='tUp1Gu4r4n1')


class MakeFakeTestData(object):
    """ixbr_api.users.models
    This class reproduce ..utils.makefake.MakeFakeData.
    However, in a testable scale. In other words, this create/simulate
    an IX structure in a minimize scale in order to test.

    Examples:
        Example of how to call this class in a test. Note that a
        Test Class will merge this __init__ class in these setUp that
        is method of django.test.TestCase, which already globalize
        the __init__ of the test class.

        >>> from ..makefaketestdata import MakeFakeTestData
        >>> class TagListViewTestBasics(TestCase):
        >>>     def setUp(self):
        >>>         (super user creation here ...)
        >>>         (login creation here ...)
        >>>         MakeFakeTestData.__init__(self)
    """

    def __init__(self):

        GeneralSettings.__init__(self)
        SP.__init__(self)
        CPV.__init__(self)


# ###########################################
# ### Settings to IX without bundle: CPV ####
# ###########################################
class CPV(object):
    def __init__(self):
        # ############# IX Settings #############
        self.cpv = IX.objects.create(
            code='cpv',
            description='IX.br de Campina Grande',
            fullname='Campina Grande - CPV',
            ipv4_prefix='11.0.0.0/22',
            ipv6_prefix='2001:12f5::0/64',
            last_ticket='0',
            management_prefix='192.168.4.0/24',
            shortname='cgrande.cpv',
            tags_policy='ix_managed',
            create_ips=False,
            create_tags=False)
        PIXFromCPV.__init__(self)
        SwitchFromCPV.__init__(self)
        ASNFromCPV.__init__(self)
        ContactsFromCPV.__init__(self)
        ChannelPortFromCPV.__init__(self)
        PortsFromCPV.__init__(self)
        CustomerChannelFromCPV.__init__(self)
        TagsFromCPV.__init__(self)
        IPsFromCPV.__init__(self)
        MACAdressFromCPV.__init__(self)
        BilateralPeerFromCPV.__init__(self)
        ServicesFromCPV.__init__(self)
        PhysicalInterfaceFromCPV.__init__(self)


class PIXFromCPV(object):
    def __init__(self):
        # ############# PIX Settings #############
        self.kapotnhinore = PIX.objects.create(
            ix=self.cpv,
            code="Kapotnhinore",
            last_ticket='2121')


class SwitchFromCPV(object):
    def __init__(self):
        # ############# Switch Settings #############
        self.extreme = SwitchModel.objects.create(
            model='ASR9003',
            vendor='CISCO',
            last_ticket='2121')
        self.extreme_port_range = SwitchPortRange.objects.create(
            switch_model=self.extreme,
            name_format='TenGigE0/0/1/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=48,
            last_ticket='2121')

        self.extreme_pix_kapotnhinore = Switch.objects.create(
            pix=self.kapotnhinore,
            model=self.extreme,
            management_ip='192.168.4.253',
            last_ticket='2121',
            translation=False,
            create_ports=False)


class PhysicalInterfaceFromCPV(object):
    def __init__(self):
        self.interface_1 = PhysicalInterface.objects.create(
            connector_type='CFP',
            port_type='ER4',
            serial_number='XOdSwevnQlzkLRngKtqJ',
            last_ticket='764')

        self.interface_2 = PhysicalInterface.objects.create(
            connector_type='SFP',
            port_type='BD',
            serial_number='AggEembXcawLcGpFQlds',
            last_ticket='764')

        self.interface_3 = PhysicalInterface.objects.create(
            connector_type='CFP',
            port_type='LR4',
            serial_number='vBluLuUMbtVDNmQGGZtm',
            last_ticket='764')

        self.interface_4 = PhysicalInterface.objects.create(
            connector_type='CFP',
            port_type='SR4',
            serial_number='AFiPALHzvGKWLADDXwek',
            last_ticket='764')

        self.interface_5 = PhysicalInterface.objects.create(
            connector_type='SFP',
            port_type='UTP',
            serial_number='kyMmpfIgJCEWUBsRKrRC',
            last_ticket='764')


class ASNFromCPV(object):
    def __init__(self):
        # ############# ASN and Organization Settings #############
        # Kayapo Settings
        self.kayapo = ASN.objects.create(number=57976, last_ticket='112')
        self.kayapo_organization = Organization.objects.create(
            name="Kayapó",
            last_ticket='2121',
            shortname='kayapo',
            cnpj='38.257.855/0001-75',
            url='http://kayapo.com',
            address='Reserva Indígena dos Kayapo')

        # Metuktire Settings
        self.metuktire = ASN.objects.create(number=28571, last_ticket='113')
        self.metuktire_organization = Organization.objects.create(
            name="Metuktire",
            shortname='metuktire',
            cnpj='84.233.857/0001-41',
            url='http://metuktire.com',
            last_ticket='2121',
            address='Reserva Indígena dos Metuktire')

        # Yudja Settings
        self.yudja = ASN.objects.create(number=1200, last_ticket='114')
        self.yudja_organization = Organization.objects.create(
            name="Yudja",
            shortname='yudja',
            cnpj='28.241.527/0001-27',
            url='http://yudja.com',
            last_ticket='2121',
            address='Reserva Indígena dos Yudja')


class ContactsFromCPV(object):
    def __init__(self):
        # ############# Contacts Settings #############
        # Kayapo Contact
        self.kayapo_noc_contact = Contact.objects.create(
            email='potira@kayapo.com',
            name='Potira',
            last_ticket='2121')
        self.kayapo_noc_phone = Phone.objects.create(
            contact=self.kayapo_noc_contact,
            category='INOC-DBA',
            number='011 3652-4155',
            last_ticket='423')
        self.kayapo_peer_contact = Contact.objects.create(
            email='raira@kayapo.com',
            name='Raira',
            last_ticket='2121')
        self.kayapo_peer_phone = Phone.objects.create(
            contact=self.kayapo_peer_contact,
            category='Mobile',
            number='011 95652-4123',
            last_ticket='423')
        self.kayapo_contactsmap = ContactsMap.objects.create(
            ix=self.cpv,
            asn=self.kayapo,
            organization=self.kayapo_organization,
            noc_contact=self.kayapo_noc_contact,
            peer_contact=self.kayapo_peer_contact,
            com_contact=self.kayapo_peer_contact,
            org_contact=self.kayapo_peer_contact,
            adm_contact=self.kayapo_peer_contact,
            peering_url='http://kayapo.com',
            last_ticket='2121')

        # Metuktire Contact
        self.metuktire_noc_contact = Contact.objects.create(
            email='juraci@metuktire.com',
            name='Juraci',
            last_ticket='2121')
        self.metuktire_noc_phone = Phone.objects.create(
            contact=self.metuktire_noc_contact,
            category='INOC-DBA',
            number='011 5545-4155',
            last_ticket='423')
        self.metuktire_peer_contact = Contact.objects.create(
            email='aruana@metuktire.com',
            name='Aruana',
            last_ticket='2121')
        self.metuktire_peer_phone = Phone.objects.create(
            contact=self.metuktire_peer_contact,
            category='Mobile',
            number='011 95425-6598',
            last_ticket='423')
        self.metuktire_contactsmap = ContactsMap.objects.create(
            ix=self.cpv,
            asn=self.metuktire,
            organization=self.metuktire_organization,
            noc_contact=self.metuktire_noc_contact,
            peer_contact=self.metuktire_peer_contact,
            com_contact=self.metuktire_peer_contact,
            org_contact=self.metuktire_peer_contact,
            adm_contact=self.metuktire_peer_contact,
            peering_url='http://metuktire.com',
            last_ticket='2121')

        # Yudja Contact
        self.yudja_noc_contact = Contact.objects.create(
            email='pora@yudja.com',
            name='Porã',
            last_ticket='2121')
        self.yudja_noc_phone = Phone.objects.create(
            contact=self.yudja_noc_contact,
            category='INOC-DBA',
            number='011 8547-3965',
            last_ticket='423')
        self.yudja_peer_contact = Contact.objects.create(
            email='bartira@yudja.com',
            name='Bartira',
            last_ticket='2121')
        self.yudja_peer_phone = Phone.objects.create(
            contact=self.yudja_peer_contact,
            category='Business',
            number='011 5244-6598',
            last_ticket='423')
        self.yudja_contactsmap = ContactsMap.objects.create(
            ix=self.cpv,
            asn=self.yudja,
            organization=self.yudja_organization,
            noc_contact=self.yudja_noc_contact,
            peer_contact=self.yudja_peer_contact,
            com_contact=self.yudja_peer_contact,
            org_contact=self.yudja_peer_contact,
            adm_contact=self.yudja_peer_contact,
            peering_url='http://yudja.com',
            last_ticket='2121')


class ChannelPortFromCPV(object):
    def __init__(self):
        # ############# Channel Port Settings #############
        self.channel_port_cpv_kapotnhinore_1 = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.channel_port_cpv_kapotnhinore_2 = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.channel_port_cpv_kapotnhinore_3 = ChannelPort.objects.create(
            tags_type='Indirect-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)


class CustomerChannelFromCPV(object):
    def __init__(self):
        # ############# Customer Channel Settings #############
        self.customer_channel_kayapo = CustomerChannel.objects.create(
            asn=self.kayapo,
            name='ct-BE3007',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_cpv_kapotnhinore_1)

        self.customer_channel_metuktire = CustomerChannel.objects.create(
            asn=self.metuktire,
            name='ct-BE3006',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_cpv_kapotnhinore_2)

        self.customer_channel_yudja = CustomerChannel.objects.create(
            asn=self.yudja,
            name='ct-BE3001',
            last_ticket='663',
            cix_type=1,
            is_lag=True,
            is_mclag=False,
            channel_port=self.channel_port_cpv_kapotnhinore_3)

        self.port_cpv_kapotnhinore_1.status = 'CUSTOMER'
        self.port_cpv_kapotnhinore_2.status = 'CUSTOMER'
        self.port_cpv_kapotnhinore_3.status = 'CUSTOMER'


class PortsFromCPV(object):
    def __init__(self):
        # ############# Port Settings #############
        self.port_cpv_kapotnhinore_1 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_cpv_kapotnhinore_1,
            physical_interface=None,
            name='TenGigE0/0/1/1',
            status='UNAVAILABLE',
            switch=self.extreme_pix_kapotnhinore,
            last_ticket='2121')

        self.port_cpv_kapotnhinore_2 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_cpv_kapotnhinore_2,
            physical_interface=None,
            name='TenGigE0/0/1/2',
            status='UNAVAILABLE',
            switch=self.extreme_pix_kapotnhinore,
            last_ticket='2121')

        self.port_cpv_kapotnhinore_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_cpv_kapotnhinore_3,
            physical_interface=None,
            name='TenGigE0/0/1/3',
            status='UNAVAILABLE',
            switch=self.extreme_pix_kapotnhinore,
            last_ticket='2121')

        self.channel_port_cpv_kapotnhinore_1.port_set.add(
            self.port_cpv_kapotnhinore_1)
        self.channel_port_cpv_kapotnhinore_2.port_set.add(
            self.port_cpv_kapotnhinore_2)
        self.channel_port_cpv_kapotnhinore_3.port_set.add(
            self.port_cpv_kapotnhinore_3)


class TagsFromCPV(object):
    def __init__(self):
        # ############# Tag Setttings #############
        # Tag Kayapo v4
        self.tag_cpv_kayapo_v4 = Tag.objects.create(
            tag='2998',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')
        # Tag Kayapo v6
        self.tag_cpv_kayapo_v6 = Tag.objects.create(
            tag='3770',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        # Tag Metuktire v4 1
        self.tag_cpv_metuktire_v4_1 = Tag.objects.create(
            tag='12',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        # Tag Metuktire v4 2
        self.tag_cpv_metuktire_v4_2 = Tag.objects.create(
            tag='19',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        # Tag Metuktire v6 1
        self.tag_cpv_metuktire_v6_1 = Tag.objects.create(
            tag='655',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        # Tag Metuktire v6 2
        self.tag_cpv_metuktire_v6_2 = Tag.objects.create(
            tag='733',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')

        # Not attributed Tag
        self.tag_cpv_none_1 = Tag.objects.create(
            tag='3050',
            ix=self.cpv,
            status='AVAILABLE',
            last_ticket='2121')

        # Tag Yudja
        self.tag_cpv_yudja = Tag.objects.create(
            tag='35',
            ix=self.cpv,
            status='PRODUCTION',
            last_ticket='2121')


class IPsFromCPV(object):
    def __init__(self):
        # ############# IPv4 and IPv6 Settings #############
        # IPv4 and IPv6 Kayapo
        self.ipv4_cpv_kayapo = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.1',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_cpv_kayapo = IPv6Address.objects.create(
            ix=self.cpv,
            address='2001:12f0::1:1',
            last_ticket='2121',
            in_lg=False)

        # IPv4 and IPv6 Metuktire 1
        self.ipv4_cpv_metuktire_1 = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.2',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_cpv_metuktire_1 = IPv6Address.objects.create(
            ix=self.cpv,
            address='2001:12f0::2:2',
            last_ticket='2121',
            in_lg=False)

        # IPv4 and IPv6 Metuktire 2
        self.ipv4_cpv_metuktire_2 = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.3',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_cpv_metuktire_2 = IPv6Address.objects.create(
            ix=self.cpv,
            address='2001:12f0::2:3',
            last_ticket='2121',
            in_lg=False)

        # IPv4 and IPv6 Yudja
        self.ipv4_cpv_yudja = IPv4Address.objects.create(
            ix=self.cpv,
            address='10.0.2.4',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_cpv_yudja = IPv6Address.objects.create(
            ix=self.cpv,
            address='2001:12f0::2:4',
            last_ticket='2121',
            in_lg=False)


class MACAdressFromCPV(object):
    def __init__(self):
        # ############# MACAddress Peer #############
        self.mac_address_cpv_1 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a8',
            last_ticket='1')

        self.mac_address_cpv_2 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:a9',
            last_ticket='2')

        self.mac_address_cpv_3 = MACAddress.objects.create(
            address='45:b3:b7:25:ee:aa',
            last_ticket='3')


class BilateralPeerFromCPV(object):
    def __init__(self):
        # ############# Bilateral Peer #############
        self.bilateral_peer_kayapo = BilateralPeer.objects.create(
            asn=self.kayapo,
            tag=self.tag_cpv_kayapo_v4,
            inner=1000,
            shortname='as{0}-bp'.format(self.kayapo.number),
            customer_channel=self.customer_channel_kayapo,
            last_ticket='1')

        self.bilateral_peer_metuktire = BilateralPeer.objects.create(
            asn=self.metuktire,
            tag=self.tag_cpv_metuktire_v4_1,
            inner=1000,
            shortname='as{0}-bp'.format(self.metuktire.number),
            customer_channel=self.customer_channel_metuktire,
            last_ticket='1')

        self.bilateral_peer_yudja = BilateralPeer.objects.create(
            asn=self.yudja,
            tag=self.tag_cpv_yudja,
            inner=1000,
            shortname='as{0}-bp'.format(self.yudja.number),
            customer_channel=self.customer_channel_yudja,
            last_ticket='1')


class ServicesFromCPV(object):
    def __init__(self):
        # ############# Services Settings #############
        # Kayapo Services
        self.mlpv4_cpv_kayapo = MLPAv4.objects.create(
            tag=self.tag_cpv_kayapo_v4,
            asn=self.kayapo,
            mlpav4_address=self.ipv4_cpv_kayapo,
            last_ticket='2121',
            customer_channel=self.customer_channel_kayapo,
            shortname='as-' + str(self.kayapo.number) + 'mlpav4')

        self.mlpv6_cpv_kayapo = MLPAv6.objects.create(
            tag=self.tag_cpv_kayapo_v6,
            asn=self.kayapo,
            mlpav6_address=self.ipv6_cpv_kayapo,
            last_ticket='2121',
            customer_channel=self.customer_channel_kayapo,
            shortname='as-' + str(self.kayapo.number) + 'mlpav6')

        # Metuktire Services
        self.mlpv4_cpv_metuktire_1 = MLPAv4.objects.create(
            tag=self.tag_cpv_metuktire_v4_1,
            asn=self.metuktire,
            inner=1000,
            mlpav4_address=self.ipv4_cpv_metuktire_1,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4',
            last_ticket='2121')

        self.mlpv6_cpv_metuktire_1 = MLPAv6.objects.create(
            tag=self.tag_cpv_metuktire_v6_1,
            asn=self.metuktire,
            inner=1000,
            mlpav6_address=self.ipv6_cpv_metuktire_1,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav6',
            last_ticket='2121')

        self.mlpv4_cpv_metuktire_2 = MLPAv4.objects.create(
            tag=self.tag_cpv_metuktire_v4_2,
            asn=self.metuktire,
            inner=1000,
            mlpav4_address=self.ipv4_cpv_metuktire_2,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav4',
            last_ticket='3123')

        self.mlpv6_cpv_metuktire_2 = MLPAv6.objects.create(
            tag=self.tag_cpv_metuktire_v6_2,
            asn=self.metuktire,
            inner=1000,
            mlpav6_address=self.ipv6_cpv_metuktire_2,
            customer_channel=self.customer_channel_metuktire,
            shortname='as-' + str(self.metuktire.number) + 'mlpav6',
            last_ticket='3123')

        # Yudja Services
        self.bilateral_cpv_metuktire_kayapo = Bilateral.objects.create(
            label='bilateral_metuktire',
            peer_a=self.bilateral_peer_metuktire,
            peer_b=self.bilateral_peer_kayapo,
            bilateral_type='L2',
            last_ticket='1')

        self.bilateral_cpv_yudja_metuktire = Bilateral.objects.create(
            label='bilateral_yudja',
            peer_a=self.bilateral_peer_yudja,
            peer_b=self.bilateral_peer_metuktire,
            bilateral_type='L2',
            last_ticket='1')


# ###########################################
# ##### Settings to IX with bundle: SP ######
# ###########################################
class SP(object):
    def __init__(self):
        # ############# IX Settings #############
        self.sp = IX.objects.create(
            code='sp',
            description='IX.br de São Paulo',
            fullname='São Paulo - SP',
            ipv4_prefix='10.0.0.0/22',
            ipv6_prefix='2001:12f0::0/64',
            last_ticket='0',
            management_prefix='192.168.5.0/24',
            shortname='saopaulo.sp',
            tags_policy='distributed',
            create_ips=False)
        PIXFromSP.__init__(self)
        SwitchFromSP.__init__(self)
        ASNFromSP.__init__(self)
        ContactsFromSP.__init__(self)
        ChannelPortFromSP.__init__(self)
        PortsFromSP.__init__(self)
        CoreChannelFromSP.__init__(self)
        DownlinkChannelFromSP.__init__(self)
        UplinkChannelFromSP.__init__(self)
        CustomerChannelFromSP.__init__(self)
        TagsFromSP.__init__(self)
        IPsFromSP.__init__(self)
        BilateralPeerFromSP.__init__(self)
        ServicesFromSP.__init__(self)
        DIOFromSP.__init__(self)
        DIOPortFromSP.__init__(self)


class PIXFromSP(object):
    def __init__(self):
        # ############# PIX Settings #############
        self.kadiweu = PIX.objects.create(
            ix=self.sp,
            code='Kadiweu',
            last_ticket='2131')

        self.araguaia = PIX.objects.create(
            ix=self.sp,
            code='Araguaia',
            last_ticket='212')


class SwitchFromSP(object):
    def __init__(self):
        # ############# Switch Settings #############
        self.cisco_sp_1 = SwitchModel.objects.create(
            model='ASR9451',
            vendor='CISCO',
            last_ticket='2121')
        self.cisco_sp_port = SwitchPortRange.objects.create(
            switch_model=self.cisco_sp_1,
            name_format='TenGigE0/0/0/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=27,
            last_ticket='2121')
        self.cisco_sp_kadiweu = Switch.objects.create(
            pix=self.kadiweu,
            model=self.cisco_sp_1,
            management_ip='192.168.5.254',
            last_ticket='2121',
            translation=False,
            create_ports=False)

        self.cisco_sp_2 = SwitchModel.objects.create(
            model='ASR9452',
            vendor='CISCO',
            last_ticket='27686')
        self.cisco_sp_araguaia_port = SwitchPortRange.objects.create(
            switch_model=self.cisco_sp_2,
            name_format='TenGigE0/0/2/{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=27,
            last_ticket='21661')
        self.cisco_sp_araguaia = Switch.objects.create(
            pix=self.araguaia,
            model=self.cisco_sp_2,
            management_ip='192.168.5.253',
            last_ticket='453',
            translation=False,
            create_ports=False)


class ASNFromSP(object):
    def __init__(self):
        # ############# ASN and Organization Settings #############
        # Chamacoco Settings
        self.chamacoco = ASN.objects.create(number=12222, last_ticket='212')
        self.chamacoco_organization = Organization.objects.create(
            name="Chamacoco",
            shortname='chamacoco',
            cnpj='18.672.331/0001-33',
            url='http://chamacoco.com',
            last_ticket='2121',
            address='Reserva Indígena dos Chamacoco')

        # Kinikinau Settings
        self.kinikinau = ASN.objects.create(number=10000, last_ticket='213')
        self.kinikinau_organization = Organization.objects.create(
            name="Kinikinau",
            shortname='kinikinau',
            cnpj='17.886.718/0001-20',
            url='http://kinikinau.com',
            last_ticket='2121',
            address='Reserva Indígena dos Kinikinau')

        # Terena Settings
        self.terena = ASN.objects.create(number=15000, last_ticket='214')
        self.terena_organization = Organization.objects.create(
            name="Terena",
            shortname='terena',
            cnpj='38.257.855/0001-75',
            url='http://terena.com',
            last_ticket='2121',
            address='Reserva Indígena dos Terena')

        self.nic = ASN.objects.create(number=22548, last_ticket='01')
        self.nic_organization = Organization.objects.create(
            name="Nucleo de Informação e Coordenacao do .br",
            shortname='nic.br',
            cnpj='05.506.560/0001-36',
            url='http://nic.com',
            last_ticket='2121',
            address='Avenida das Nações Unidas, 11541')

        # Guarani Kawiowa Settings
        self.guarani_kawiowa = ASN.objects.create(
            number=62000,
            last_ticket='215',)


class ContactsFromSP(object):
    def __init__(self):
        # ############# Contacts Settings #############
        # Chamacoco Contact
        self.chamacoco_noc_contact = Contact.objects.create(
            email='iracema@chamacoco.com',
            name='Iracema',
            last_ticket='2121')
        self.chamacoco_noc_phone = Phone.objects.create(
            contact=self.chamacoco_noc_contact,
            category='INOC-DBA',
            number='011 7542-4852',
            last_ticket='423')
        self.chamacoco_peer_contact = Contact.objects.create(
            email='ubiraci@chamacoco.com',
            name='Ubiraci',
            last_ticket='2121')
        self.chamacoco_peer_phone = Phone.objects.create(
            contact=self.chamacoco_peer_contact,
            category='Mobile',
            number='011 98452-2545',
            last_ticket='423')
        self.chamacoco_contactsmap = ContactsMap.objects.create(
            ix=self.sp,
            asn=self.chamacoco,
            organization=self.chamacoco_organization,
            noc_contact=self.chamacoco_noc_contact,
            peer_contact=self.chamacoco_peer_contact,
            com_contact=self.chamacoco_peer_contact,
            org_contact=self.chamacoco_peer_contact,
            adm_contact=self.chamacoco_peer_contact,
            peering_url='http://chamacoco.com',
            last_ticket='2121')

        # Kinikinau Contact
        self.kinikinau_noc_contact = Contact.objects.create(
            email='jurema@kinikinau.com',
            name='Jurema',
            last_ticket='2121')
        self.kinikinau_noc_phone = Phone.objects.create(
            contact=self.kinikinau_noc_contact,
            category='INOC-DBA',
            number='081 2365-4445',
            last_ticket='423')
        self.kinikinau_peer_contact = Contact.objects.create(
            email='acir@kinikinau.com',
            name='Acir',
            last_ticket='2121')
        self.kinikinau_peer_phone = Phone.objects.create(
            contact=self.kinikinau_peer_contact,
            category='Mobile',
            number='081 94554-6552',
            last_ticket='423')
        self.kinikinau_contactsmap = ContactsMap.objects.create(
            ix=self.sp,
            asn=self.kinikinau,
            organization=self.kinikinau_organization,
            noc_contact=self.kinikinau_noc_contact,
            peer_contact=self.kinikinau_peer_contact,
            com_contact=self.kinikinau_peer_contact,
            org_contact=self.kinikinau_peer_contact,
            adm_contact=self.kinikinau_peer_contact,
            peering_url='http://kinikinau.com',
            last_ticket='2121')

        # Terena Contact
        self.terena_noc_contact = Contact.objects.create(
            email='guaraci@terena.com',
            name='Guaraci',
            last_ticket='2121')
        self.terena_noc_phone = Phone.objects.create(
            contact=self.terena_noc_contact,
            category='INOC-DBA',
            number='033 2365-4445',
            last_ticket='423')
        self.terena_peer_contact = Contact.objects.create(
            email='ubiratan@terena.com',
            name='Ubiratan',
            last_ticket='2121')
        self.terena_peer_phone = Phone.objects.create(
            contact=self.terena_peer_contact,
            category='Landline',
            number='021 3255-5452',
            last_ticket='423')
        self.terena_contactsmap = ContactsMap.objects.create(
            ix=self.sp,
            asn=self.terena,
            organization=self.terena_organization,
            noc_contact=self.terena_noc_contact,
            peer_contact=self.terena_peer_contact,
            com_contact=self.terena_peer_contact,
            org_contact=self.terena_peer_contact,
            adm_contact=self.terena_peer_contact,
            peering_url='http://terena.com',
            last_ticket='2121')

        # Terena Contact
        self.nic_noc_contact = Contact.objects.create(
            email='noc@nic.br',
            name='Nic',
            last_ticket='2121')
        self.nic_noc_phone = Phone.objects.create(
            contact=self.nic_noc_contact,
            category='INOC-DBA',
            number='011 5509-3511',
            last_ticket='423')
        self.nic_peer_contact = Contact.objects.create(
            email='peer@nic.br',
            name='Nic',
            last_ticket='2121')
        self.nic_peer_phone = Phone.objects.create(
            contact=self.nic_peer_contact,
            category='Landline',
            number='011 5509-3511',
            last_ticket='423')
        self.nic_contactsmap = ContactsMap.objects.create(
            ix=self.sp,
            asn=self.nic,
            organization=self.nic_organization,
            noc_contact=self.nic_noc_contact,
            peer_contact=self.nic_peer_contact,
            com_contact=self.nic_peer_contact,
            org_contact=self.nic_peer_contact,
            adm_contact=self.nic_peer_contact,
            peering_url='http://nic.br',
            last_ticket='2121')


class ChannelPortFromSP(object):
    def __init__(self):
        # ############# Channel Port and Downlink settings #############
        self.channel_port_sp_kadiweu_1 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.channel_port_sp_kadiweu_2 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.channel_port_sp_kadiweu_3 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='432',
            create_tags=False)

        self.channel_port_sp_kadiweu_4 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='432',
            create_tags=False)

        self.channel_port_sp_araguaia_1 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)

        self.channel_port_sp_araguaia_2 = ChannelPort.objects.create(
            tags_type='Direct-Bundle-Ether',
            last_ticket='2121',
            create_tags=False)


class CoreChannelFromSP(object):
    def __init__(self):
        self.core_channel_sp_araguaia_1 = CoreChannel.objects.create(
            name='cc-BE1020',
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_1,
            last_ticket='4454')

        self.core_channel_sp_araguaia_2 = CoreChannel.objects.create(
            name='cc-BE1019',
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_araguaia_2,
            last_ticket='4454')


class CustomerChannelFromSP(object):
    def __init__(self):
        # ############# Customer Channel Settings #############
        self.customer_channel_chamacoco = CustomerChannel.objects.create(
            asn=self.chamacoco,
            name='ct-BE3002',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_kadiweu_1)

        self.customer_channel_kinikinau = CustomerChannel.objects.create(
            asn=self.kinikinau,
            name='ct-BE3000',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_kadiweu_2)

        self.customer_channel_terena = CustomerChannel.objects.create(
            asn=self.terena,
            name='ct-BE3003',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_kadiweu_3)

        self.customer_channel_nic = CustomerChannel.objects.create(
            asn=self.nic,
            name='ct-BE3004',
            last_ticket='663',
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_sp_kadiweu_4)

        self.port_sp_kadiweu_1.status = 'CUSTOMER'
        self.port_sp_kadiweu_2.status = 'CUSTOMER'
        self.port_sp_kadiweu_3.status = 'CUSTOMER'
        self.port_sp_kadiweu_4.status = 'CUSTOMER'



class DownlinkChannelFromSP(object):
    def __init__(self):
        self.downlink_channel_sp_kadiweu_1 = DownlinkChannel.objects.create(
            name='dl-BE1011',
            channel_port=self.channel_port_sp_kadiweu_1,
            is_mclag=False,
            last_ticket='2121',
            is_lag=True)

        self.downlink_channel_sp_kadiweu_2 = DownlinkChannel.objects.create(
            name='dl-BE1012',
            channel_port=self.channel_port_sp_kadiweu_2,
            last_ticket='2121',
            is_lag=True,
            is_mclag=False,)

        self.downlink_channel_sp_kadiweu_3 = DownlinkChannel.objects.create(
            name='dl-BE1013',
            channel_port=self.channel_port_sp_kadiweu_3,
            last_ticket='2121',
            is_lag=True,
            is_mclag=False,)

        self.port_sp_kadiweu_1.status = 'INFRASTRUCTURE'
        self.port_sp_kadiweu_2.status = 'INFRASTRUCTURE'
        self.port_sp_kadiweu_3.status = 'INFRASTRUCTURE'

class UplinkChannelFromSP(object):
    def __init__(self):
        self.uplink_channel_sp_kadiweu_1 = UplinkChannel.objects.create(
            name='ul-BE1011',
            is_mclag=False,
            channel_port=self.channel_port_sp_kadiweu_1,
            downlink_channel=self.downlink_channel_sp_kadiweu_1,
            last_ticket='2121',
            is_lag=True)


class PortsFromSP(object):
    def __init__(self):
        self.port_sp_kadiweu_1 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            channel_port=self.channel_port_sp_kadiweu_1,
            physical_interface=None,
            name='TenGigE0/0/0/1',
            status='UNAVAILABLE',
            switch=self.cisco_sp_kadiweu,
            last_ticket='2121')

        self.port_sp_kadiweu_2 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_kadiweu,
            channel_port=self.channel_port_sp_kadiweu_2,
            name='TenGigE0/0/0/2',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_kadiweu_3 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            switch=self.cisco_sp_kadiweu,
            channel_port=self.channel_port_sp_kadiweu_3,
            name='TenGigE0/0/0/3',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_kadiweu_4 = Port.objects.create(
            capacity=1000,
            connector_type='SFP+',
            switch=self.cisco_sp_kadiweu,
            channel_port=self.channel_port_sp_kadiweu_4,
            name='TenGigE0/0/0/4',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_1 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_1,
            name='TenGigE0/0/0/8',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.port_sp_araguaia_2 = Port.objects.create(
            capacity=1000,
            connector_type='SFP',
            switch=self.cisco_sp_araguaia,
            channel_port=self.channel_port_sp_araguaia_2,
            name='TenGigE0/0/2/7',
            status='UNAVAILABLE',
            last_ticket='2121')

        self.channel_port_sp_kadiweu_1.port_set.add(self.port_sp_kadiweu_1)
        self.channel_port_sp_kadiweu_2.port_set.add(self.port_sp_kadiweu_2)
        self.channel_port_sp_kadiweu_3.port_set.add(self.port_sp_kadiweu_3)
        self.channel_port_sp_kadiweu_4.port_set.add(self.port_sp_kadiweu_4)
        self.channel_port_sp_araguaia_1.port_set.add(self.port_sp_araguaia_1)
        self.channel_port_sp_araguaia_2.port_set.add(self.port_sp_araguaia_2)


class TagsFromSP(object):
    def __init__(self):
        # ############# Tag Setttings #############
        # Tag Chamacoco
        self.tag_sp_chamacoco = Tag.objects.create(
            tag='1', ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_1,
            status='ALLOCATED',
            last_ticket='2121')

        # Tag Kinikinau
        self.tag_sp_kinikinau = Tag.objects.create(
            tag='13',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_1,
            status='PRODUCTION',
            last_ticket='2121')

        # Not attributed Tags
        self.tag_sp_none_1 = Tag.objects.create(
            tag='120',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_1,
            status='AVAILABLE',
            last_ticket='2121')
        self.tag_sp_none_2 = Tag.objects.create(
            tag='457',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_1,
            status='AVAILABLE',
            last_ticket='2121')

        # Tag Terena
        self.tag_sp_terena = Tag.objects.create(
            tag='3711',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_3,
            status='PRODUCTION',
            last_ticket='2121')

        # Tag  Monitorv4
        self.tag_sp_monitor_v4_1 = Tag.objects.create(
            tag='4000',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_4,
            status='PRODUCTION',
            last_ticket='2121')

        self.tag_sp_monitor_v4_2 = Tag.objects.create(
            tag='4080',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_4,
            status='PRODUCTION',
            last_ticket='2121')

        self.tag_sp_monitor_v4_3 = Tag.objects.create(
            tag='4090',
            ix=self.sp,
            tag_domain=self.channel_port_sp_kadiweu_4,
            status='PRODUCTION',
            last_ticket='2121')


class IPsFromSP(object):
    def __init__(self):
        # ############# IPv4 and IPv6 Settings #############
        # IPv4 and IPv6 Chamacoco
        self.ipv4_sp_chamacoco = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.243',
            last_ticket='2121',
            in_lg=True)
        self.ipv6_sp_chamacoco = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:243',
            last_ticket='2121',
            in_lg=True)

        # IPv4 and IPv6 Kinikinau
        self.ipv4_sp_kinikinau = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.1',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_sp_kinikinau = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:1',
            last_ticket='2121',
            in_lg=False)

        # Not attributed IPv4 and IPv6
        self.ipv4_sp_none = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.244',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_sp_none = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:244',
            last_ticket='2121',
            in_lg=False)

        # IPv4 Terena
        self.ipv4_sp_terena = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.245',
            last_ticket='2121',
            in_lg=False)
        self.ipv6_sp_terena = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:245',
            last_ticket='2121',
            in_lg=False)

        # IPv4 Monitorv4
        self.ipv4_sp_monitor_v4_1 = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.2',
            last_ticket='45',
            in_lg=False)
        self.ipv6_sp_monitor_v4_1 = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:2',
            last_ticket='2121',
            in_lg=False)

        self.ipv4_sp_monitor_v4_2 = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.3',
            last_ticket='45',
            in_lg=False)
        self.ipv6_sp_monitor_v4_2 = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:3',
            last_ticket='2121',
            in_lg=False)

        self.ipv4_sp_monitor_v4_3 = IPv4Address.objects.create(
            ix=self.sp,
            address='10.0.3.4',
            last_ticket='45',
            in_lg=False)
        self.ipv6_sp_monitor_v4_3 = IPv6Address.objects.create(
            ix=self.sp,
            address='2001:12f0::3:4',
            last_ticket='2121',
            in_lg=False)


class BilateralPeerFromSP(object):
    def __init__(self):
        # ############# Bilateral Peer #############
        self.bilateral_peer_chamacoco = BilateralPeer.objects.create(
            asn=self.chamacoco,
            tag=self.tag_sp_chamacoco,
            inner=1000,
            shortname='as{0}-bp'.format(self.chamacoco.number),
            customer_channel=self.customer_channel_chamacoco,
            last_ticket='1')

        self.bilateral_peer_kinikinau = BilateralPeer.objects.create(
            asn=self.kinikinau,
            tag=self.tag_sp_kinikinau,
            inner=1000,
            shortname='as{0}-bp'.format(self.kinikinau.number),
            customer_channel=self.customer_channel_kinikinau,
            last_ticket='1')

        self.bilateral_peer_terena = BilateralPeer.objects.create(
            asn=self.terena,
            tag=self.tag_sp_terena,
            inner=1000,
            shortname='as{0}-bp'.format(self.terena.number),
            customer_channel=self.customer_channel_terena,
            last_ticket='1')


class ServicesFromSP(object):
    def __init__(self):
        # ############# Services Settings #############
        # Chamacoco Services
        self.mlpv4_sp_chamacoco = MLPAv4.objects.create(
            tag=self.tag_sp_chamacoco,
            asn=self.chamacoco,
            mlpav4_address=self.ipv4_sp_chamacoco,
            last_ticket='2121',
            customer_channel=self.customer_channel_chamacoco,
            shortname='as-' + str(self.chamacoco.number) + 'mlpav4')

        self.mlpv6_sp_chamacoco = MLPAv6.objects.create(
            tag=self.tag_sp_chamacoco,
            asn=self.chamacoco,
            mlpav6_address=self.ipv6_sp_chamacoco,
            last_ticket='2121',
            inner=1000,
            customer_channel=self.customer_channel_chamacoco,
            shortname='as-' + str(self.chamacoco.number) + 'mlpav6')

        # Kinikinau Services
        self.mlpv4_sp_kinikinau = MLPAv4.objects.create(
            tag=self.tag_sp_kinikinau,
            asn=self.kinikinau,
            mlpav4_address=self.ipv4_sp_kinikinau,
            last_ticket='2121',
            customer_channel=self.customer_channel_kinikinau,
            shortname='as-' + str(self.kinikinau.number) + 'mlpav4')

        # Terena Services
        self.mlpv4_sp_terena = MLPAv4.objects.create(
            tag=self.tag_sp_terena,
            asn=self.terena,
            mlpav4_address=self.ipv4_sp_terena,
            last_ticket='2121',
            customer_channel=self.customer_channel_terena,
            shortname='as-' + str(self.terena.number) + 'mlpav4')

        self.bilateral_sp_terena_kinikinau = Bilateral.objects.create(
            label='bilateral_terena',
            peer_a=self.bilateral_peer_terena,
            peer_b=self.bilateral_peer_kinikinau,
            bilateral_type='L2',
            last_ticket='1')

        # Monitorv4 Services
        self.monitorv4_sp_1 = Monitorv4.objects.create(
            asn=self.nic,
            tag=self.tag_sp_monitor_v4_1,
            inner=1000,
            monitor_address=self.ipv4_sp_monitor_v4_1,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-1',
            last_ticket='4363')

        self.monitorv4_sp_2 = Monitorv4.objects.create(
            asn=self.nic,
            tag=self.tag_sp_monitor_v4_2,
            inner=1000,
            monitor_address=self.ipv4_sp_monitor_v4_2,
            customer_channel=self.customer_channel_nic,
            shortname='as-' + str(self.nic.number) + 'monitorv4-2',
            last_ticket='4645')

        self.monitorv4_sp_3 = Monitorv4.objects.create(
            asn=self.terena,
            tag=self.tag_sp_monitor_v4_3,
            inner=1002,
            monitor_address=self.ipv4_sp_monitor_v4_3,
            customer_channel=self.customer_channel_terena,
            shortname='as-' + str(self.terena.number) + 'monitorv4-3',
            last_ticket='86')


class DIOFromSP(object):
    def __init__(self):
        self.dio_kadiweu_1 = DIO.objects.create(
            name='dio kadiweu 1',
            pix=self.kadiweu,
            last_ticket='2312')

        self.dio_kadiweu_2 = DIO.objects.create(
            name='dio kadiweu 2',
            pix=self.kadiweu,
            last_ticket='475')

        self.dio_araguaia_1 = DIO.objects.create(
            name='dio araguaia 1',
            pix=self.araguaia,
            last_ticket='653')


class DIOPortFromSP(object):
    def __init__(self):
        self.dio_port_kadiweu_1 = DIOPort.objects.create(
            datacenter_position='datacenterfirst',
            dio=self.dio_kadiweu_1,
            switch_port=self.port_sp_araguaia_1,
            ix_position='ixpositionfirst',
            last_ticket='5465')

        self.dio_port_kadiweu_2 = DIOPort.objects.create(
            datacenter_position='datacentersecond',
            dio=self.dio_kadiweu_2,
            switch_port=self.port_sp_araguaia_1,
            ix_position='ixpositionsecond',
            last_ticket='5465')

        self.dio_port_araguaia_1 = DIOPort.objects.create(
            datacenter_position='datacenterthird',
            dio=self.dio_araguaia_1,
            switch_port=self.port_sp_araguaia_1,
            ix_position='ixpositionthird',
            last_ticket='5465')

        self.dio_port_araguaia_2 = DIOPort.objects.create(
            datacenter_position='datacenterfourth',
            dio=self.dio_araguaia_1,
            switch_port=self.port_sp_araguaia_1,
            ix_position='ixpositionfourth',
            last_ticket='5465')
