from ixbr_api.core.models import *
from ixbr_api.core.tests.factories import *

# ###########################################
# ### Settings to IX without bundle: RIA ####
# ###########################################

class MakeSantaMaria(object):

    def __init__(self):

        self.user = UserFactory()
        self.user.save()

        # ############# IX Settings #############
        self.ria = IX.objects.create(
            code='ria',
            description='IX.br de Santa Maria',
            fullname='Santa Maria - RIA',
            ipv4_prefix='187.16.205.0/24',
            ipv6_prefix='2001:12f8:0:28::/64',
            last_ticket='0',
            modified_by=self.user,
            management_prefix='192.168.28.0/26',
            shortname='santamaria.rs',
            tags_policy='ix_managed',
            create_ips=True,
            create_tags=True)

    def createRIAPix(self):

        self.avato = PIX.objects.create(
            ix=self.ria,
            code="AVATO",
            modified_by=self.user,
            last_ticket='2222'
        )

    def createRIASwitche_01(self):
        # ############# Switch Settings #############
        self.extreme_01 = SwitchModel.objects.create(
            model='X460-48t',
            vendor='EXTREME',
            modified_by=self.user,
            last_ticket='2424')
        self.extreme_port_range_01 = SwitchPortRange.objects.create(
            switch_model=self.extreme_01,
            name_format='{0}',
            capacity=1000,
            connector_type='UTP',
            begin=1, end=48,
            modified_by=self.user,
            last_ticket='2525')
        self.extreme_pix_avato_01 = Switch.objects.create(
            translation=False,
            pix=self.avato,
            model=self.extreme_01,
            management_ip='192.168.28.2',
            last_ticket='2626',
            modified_by=self.user,
            create_ports=True)

    def createRIASwitche_02(self):
        self.extreme_02 = SwitchModel.objects.create(
            model='X670-72x',
            vendor='EXTREME',
            modified_by=self.user,
            last_ticket='2424')
        self.extreme_port_range_02 = SwitchPortRange.objects.create(
            switch_model=self.extreme_02,
            name_format='{0}',
            capacity=1000,
            connector_type='SFP+',
            begin=1, end=72,
            modified_by=self.user,
            last_ticket='2525')
        self.extreme_pix_avato_02 = Switch.objects.create(
            translation=False,
            pix=self.avato,
            model=self.extreme_02,
            management_ip='192.168.28.3',
            last_ticket='2626',
            modified_by=self.user,
            create_ports=True)

    def createRIAASN(self):
        # ############# ASN and Organization Settings #############
        self.simet = ASN.objects.create(number=14026,
                                        last_ticket='221',
                                        modified_by=self.user)
        self.simet_organization = Organization.objects.create(
            name="Simet",
            last_ticket='1212',
            shortname='simet',
            cnpj='05.506.560/0001-36',
            url='http://simet.nic.br/',
            modified_by=self.user,
            address='Av. das Nações Unidas, 11541')

        self.route_server = ASN.objects.create(number=26162,
                                               last_ticket='222',
                                               modified_by=self.user)
        self.route_server_organization = Organization.objects.create(
            name="IX.br",
            last_ticket='1213',
            shortname='ix',
            cnpj='05.506.560/0001-36',
            url='http://ix.br/',
            modified_by=self.user,
            address='Av. das Nações Unidas, 11541')

        self.lg_sara = ASN.objects.create(number=20121,
                                               last_ticket='222',
                                               modified_by=self.user)
        self.lg_sara_organization = Organization.objects.create(
            name="LG-SARA",
            last_ticket='1213',
            shortname='lg-sara',
            cnpj='05.506.560/0001-36',
            url='http://ix.br/',
            modified_by=self.user,
            address='Av. das Nações Unidas, 11541')

        self.lg_meu_ix = ASN.objects.create(number=263044,
                                               last_ticket='222',
                                               modified_by=self.user)
        self.lg_meu_ix_organization = Organization.objects.create(
            name="LG-Meu.ix.br",
            last_ticket='1213',
            shortname='lg-meu.ix',
            cnpj='05.506.560/0001-36',
            url='http://ix.br/',
            modified_by=self.user,
            address='Av. das Nações Unidas, 11541')

    def createRIAContacts(self):
        # ############# Contacts Settings #############
        # Simet Contact
        simet_noc_contact = Contact.objects.create(
            email='paulo@nic.br',
            name='Paulo',
            modified_by=self.user,
            last_ticket='1212')
        simet_noc_phone = Phone.objects.create(
            contact=simet_noc_contact,
            category='INOC-DBA',
            number='11 55093537 4047',
            modified_by=self.user,
            last_ticket='1212')
        simet_peer_contact = Contact.objects.create(
            email='rmaegaki@nic.br',
            name='Rogerio Maegaki',
            modified_by=self.user,
            last_ticket='1212')
        simet_peer_phone = Phone.objects.create(
            contact=simet_peer_contact,
            category='Mobile',
            number='11 55093537 4057',
            modified_by=self.user,
            last_ticket='1212')
        simet_contactsmap = ContactsMap.objects.create(
            ix=self.ria,
            asn=self.simet,
            organization=self.simet_organization,
            noc_contact=simet_noc_contact,
            peer_contact=simet_peer_contact,
            com_contact=simet_peer_contact,
            org_contact=simet_peer_contact,
            adm_contact=simet_peer_contact,
            peering_url='http://simet.com',
            modified_by=self.user,
            last_ticket='2121')

        # Route Servers Contact
        route_server_noc_contact = Contact.objects.create(
            email='noc@ix.br',
            name='NOC IX.br',
            modified_by=self.user,
            last_ticket='1212')
        route_server_noc_phone = Phone.objects.create(
            contact=route_server_noc_contact,
            category='INOC-DBA',
            number='26162*100',
            modified_by=self.user,
            last_ticket='1212')
        route_server_peer_contact = Contact.objects.create(
            email='bgp@ptt.br',
            name='Routing PTT.br',
            modified_by=self.user,
            last_ticket='1212')
        route_server_peer_phone = Phone.objects.create(
            contact=route_server_peer_contact,
            category='Business',
            number='11 55093500',
            modified_by=self.user,
            last_ticket='1212')
        route_server_contactsmap = ContactsMap.objects.create(
            ix=self.ria,
            asn=self.route_server,
            organization=self.route_server_organization,
            noc_contact=route_server_noc_contact,
            peer_contact=route_server_peer_contact,
            com_contact=route_server_peer_contact,
            org_contact=route_server_peer_contact,
            adm_contact=route_server_peer_contact,
            peering_url='http://ix.br',
            modified_by=self.user,
            last_ticket='2121')

        # LG-SARA Contact
        lg_sara_contactsmap = ContactsMap.objects.create(
            ix=self.ria,
            asn=self.lg_sara,
            organization=self.lg_sara_organization,
            noc_contact=simet_noc_contact,
            peer_contact=simet_peer_contact,
            com_contact=simet_peer_contact,
            org_contact=simet_peer_contact,
            adm_contact=simet_peer_contact,
            peering_url='http://ix.br',
            modified_by=self.user,
            last_ticket='2121')

        # LG-Meu.ix Servers Contact
        lg_meu_ix_contactsmap = ContactsMap.objects.create(
            ix=self.ria,
            asn=self.lg_meu_ix,
            organization=self.lg_meu_ix_organization,
            noc_contact=route_server_noc_contact,
            peer_contact=route_server_peer_contact,
            com_contact=route_server_peer_contact,
            org_contact=route_server_peer_contact,
            adm_contact=route_server_peer_contact,
            peering_url='http://ix.br',
            modified_by=self.user,
            last_ticket='2121')

    ### JPA CONTACTS ######
        route_server_contactsmap_jpa = ContactsMap.objects.create(
            ix=self.jpa,
            asn=self.route_server,
            organization=self.route_server_organization,
            noc_contact=route_server_noc_contact,
            peer_contact=route_server_peer_contact,
            com_contact=route_server_peer_contact,
            org_contact=route_server_peer_contact,
            adm_contact=route_server_peer_contact,
            peering_url='http://ix.br',
            modified_by=self.user,
            last_ticket='2121')

        # LG-SARA Contact
        lg_sara_contactsmap_jpa = ContactsMap.objects.create(
            ix=self.jpa,
            asn=self.lg_sara,
            organization=self.lg_sara_organization,
            noc_contact=simet_noc_contact,
            peer_contact=simet_peer_contact,
            com_contact=simet_peer_contact,
            org_contact=simet_peer_contact,
            adm_contact=simet_peer_contact,
            peering_url='http://ix.br',
            modified_by=self.user,
            last_ticket='2121')

        # LG-Meu.ix Servers Contact
        lg_meu_ix_contactsmap_jpa = ContactsMap.objects.create(
            ix=self.jpa,
            asn=self.lg_meu_ix,
            organization=self.lg_meu_ix_organization,
            noc_contact=route_server_noc_contact,
            peer_contact=route_server_peer_contact,
            com_contact=route_server_peer_contact,
            org_contact=route_server_peer_contact,
            adm_contact=route_server_peer_contact,
            peering_url='http://ix.br',
            modified_by=self.user,
            last_ticket='2121')




    def createIPsRIA(self):

        self.ipv4_ria_simet = IPv4Address.objects.get(address='187.16.205.10')
        self.ipv4_ria_simet.in_lg=True
        
        self.ipv6_ria_simet = IPv6Address.objects.get(address='2001:12f8:0:28::10')
        self.ipv6_ria_simet.in_lg=True
        
        self.ipv4_ria_lg_meu_ix = IPv4Address.objects.get(address='187.16.205.249')
        self.ipv4_ria_lg_meu_ix.in_lg=True
        
        self.ipv6_ria_lg_meu_ix = IPv6Address.objects.get(address='2001:12f8:0:28::249')
        self.ipv6_ria_lg_meu_ix.in_lg=True

        self.ipv4_ria_lg_sara = IPv4Address.objects.get(address='187.16.205.252')
        self.ipv4_ria_lg_sara.in_lg=True
        
        self.ipv6_ria_lg_sara = IPv6Address.objects.get(address='2001:12f8:0:28::252')
        self.ipv6_ria_lg_sara.in_lg=True
        

        self.ipv4_ria_rs1 = IPv4Address.objects.get(address='187.16.205.253')
        self.ipv4_ria_rs1.in_lg=True
        
        self.ipv6_ria_rs1 = IPv6Address.objects.get(address='2001:12f8:0:28::253')
        self.ipv6_ria_rs1.in_lg=True
        
        self.ipv4_ria_rs2 = IPv4Address.objects.get(address='187.16.205.254')
        self.ipv4_ria_rs2.in_lg=True

        self.ipv6_ria_rs2 = IPv6Address.objects.get(address='2001:12f8:0:28::254')
        self.ipv6_ria_rs2.in_lg=True
        

    def createChannelPortRIA(self):

        self.channel_port_ria_rs_430_42 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_rs_430_43 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_rs_430_44 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_rs_430_45 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_rs_430_46 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_thin_client_47 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_internet_48 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_corechannel_52 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_simet_01 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_ria_corechannel_72 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

    def createPortRIA(self):

        self.port_ria_sw01_42 = Port.objects.get(switch=self.extreme_pix_avato_01, name='42')
        self.port_ria_sw01_42.channel_port=self.channel_port_ria_rs_430_42
        self.port_ria_sw01_42.status='UNAVAILABLE'
        self.port_ria_sw01_42.save()


        self.port_ria_sw01_43 = Port.objects.get(switch=self.extreme_pix_avato_01, name='43')
        self.port_ria_sw01_43.channel_port=self.channel_port_ria_rs_430_43
        self.port_ria_sw01_43.status='UNAVAILABLE'
        self.port_ria_sw01_43.save()

        self.port_ria_sw01_44 = Port.objects.get(switch=self.extreme_pix_avato_01, name='44')
        self.port_ria_sw01_44.channel_port=self.channel_port_ria_rs_430_44
        self.port_ria_sw01_44.status='UNAVAILABLE'
        self.port_ria_sw01_44.save()

        self.port_ria_sw01_45 = Port.objects.get(switch=self.extreme_pix_avato_01, name='45')
        self.port_ria_sw01_45.channel_port=self.channel_port_ria_rs_430_45
        self.port_ria_sw01_45.status='UNAVAILABLE'
        self.port_ria_sw01_45.save()

        self.port_ria_sw01_46 = Port.objects.get(switch=self.extreme_pix_avato_01, name='46')
        self.port_ria_sw01_46.channel_port=self.channel_port_ria_rs_430_46
        self.port_ria_sw01_46.status='UNAVAILABLE'
        self.port_ria_sw01_46.save()

        self.port_ria_sw01_47 = Port.objects.get(switch=self.extreme_pix_avato_01, name='47')
        self.port_ria_sw01_47.channel_port=self.channel_port_ria_thin_client_47
        self.port_ria_sw01_47.status='UNAVAILABLE'
        self.port_ria_sw01_47.save()

        self.port_ria_sw01_48 = Port.objects.get(switch=self.extreme_pix_avato_01, name='48')
        self.port_ria_sw01_48.channel_port=self.channel_port_ria_internet_48
        self.port_ria_sw01_48.status='UNAVAILABLE'
        self.port_ria_sw01_48.save()

        self.port_ria_sw02_01 = Port.objects.get(switch=self.extreme_pix_avato_02, name='1')
        self.port_ria_sw02_01.channel_port=self.channel_port_ria_simet_01
        self.port_ria_sw02_01.status='UNAVAILABLE'
        self.port_ria_sw02_01.save()


        self.port_ria_corechannel_72_sw02 = Port.objects.get(switch=self.extreme_pix_avato_02, name='72')
        self.port_ria_corechannel_72_sw02.channel_port=self.channel_port_ria_corechannel_72
        self.port_ria_corechannel_72_sw02.status='INFRASTRUCTURE'
        self.port_ria_corechannel_72_sw02.save()


        self.port_ria_corechannel_52_sw01 = Port.objects.create(
            capacity=10000,
            connector_type='SFP+',
            switch=self.extreme_pix_avato_01,
            channel_port=self.channel_port_ria_corechannel_52,
            name='52',
            status='INFRASTRUCTURE',
            modified_by=self.user,
            last_ticket='2121')


        self.channel_port_ria_rs_430_42.port_set.add(self.port_ria_sw01_42)
        self.channel_port_ria_rs_430_43.port_set.add(self.port_ria_sw01_43)
        self.channel_port_ria_rs_430_44.port_set.add(self.port_ria_sw01_44)
        self.channel_port_ria_rs_430_45.port_set.add(self.port_ria_sw01_45)
        self.channel_port_ria_rs_430_46.port_set.add(self.port_ria_sw01_46)
        self.channel_port_ria_thin_client_47.port_set.add(self.port_ria_sw01_47)
        self.channel_port_ria_internet_48.port_set.add(self.port_ria_sw01_48)
        self.channel_port_ria_simet_01.port_set.add(self.port_ria_sw02_01)

        self.channel_port_ria_corechannel_52.port_set.add(
            self.port_ria_corechannel_52_sw01)
        self.channel_port_ria_corechannel_72.port_set.add(
            self.port_ria_corechannel_72_sw02)

    def createCustomerChannelRIA(self):
        self.customer_channel_rs_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-42',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_rs_430_42)

        self.customer_channel_rs_2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-43',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_rs_430_43)

        self.customer_channel_rs_3 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-44',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_rs_430_44)

        self.customer_channel_rs_4 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-45',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_rs_430_45)

        self.customer_channel_gb2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-46',
            last_ticket='663',
            modified_by=self.user,
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_rs_430_46)

        self.customer_channel_thin_client_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-47',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_thin_client_47)

        self.customer_channel_internet_1 = CustomerChannel.objects.create(
            asn=self.lg_meu_ix,
            name='ct-48',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_internet_48)

        self.customer_channel_simet_1 = CustomerChannel.objects.create(
            asn=self.simet,
            name='ct-1',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_simet_01)


        self.port_ria_sw01_42.status='CUSTOMER'
        self.port_ria_sw01_42.save()
        self.port_ria_sw01_43.status='CUSTOMER'
        self.port_ria_sw01_43.save()
        self.port_ria_sw01_44.status='CUSTOMER'
        self.port_ria_sw01_44.save()
        self.port_ria_sw01_45.status='CUSTOMER'
        self.port_ria_sw01_45.save()
        self.port_ria_sw01_46.status='CUSTOMER'
        self.port_ria_sw01_46.save()
        self.port_ria_sw01_47.status='CUSTOMER'
        self.port_ria_sw01_47.save()
        self.port_ria_sw01_48.status='CUSTOMER'
        self.port_ria_sw01_48.save()
        self.port_ria_sw02_01.status='CUSTOMER'
        self.port_ria_sw02_01.save()


    def createCoreChannelRIA(self):
        self.core_channel_sw01_52 = CoreChannel.objects.create(
            name='cc-52',
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_corechannel_52,
            modified_by=self.user,
            last_ticket='4454')

        self.core_channel_sw02_72 = CoreChannel.objects.create(
            name='cc-72',
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_ria_corechannel_72,
            modified_by=self.user,
            last_ticket='4454')

        self.core_channel_sw01_52.status = 'INFRASTRUCTURE'
        self.core_channel_sw02_72.status = 'INFRASTRUCTURE'

    def tagsRIA(self):
        # ############# Tag Setttings #############
        self.tag_ria_rs_v4 = Tag.objects.get(tag=10, ix=self.ria)
        self.tag_ria_rs_v4.status='PRODUCTION'
        self.tag_ria_rs_v4.save()
        self.tag_ria_rs_v6 = Tag.objects.get(tag=20, ix=self.ria)
        self.tag_ria_rs_v6.status='PRODUCTION'
        self.tag_ria_rs_v6.save()
        self.tag_ria_reserved_99 = Tag.objects.get(tag=99, ix=self.ria)
        self.tag_ria_reserved_99.status='ALLOCATED'
        self.tag_ria_reserved_99.save()
        self.tag_ria_reserved_100 = Tag.objects.get(tag=100, ix=self.ria)
        self.tag_ria_reserved_100.status='ALLOCATED'
        self.tag_ria_reserved_100.save()
        self.tag_ria_reserved_201 = Tag.objects.get(tag=201, ix=self.ria)
        self.tag_ria_reserved_201.status='ALLOCATED'
        self.tag_ria_reserved_201.save()
        self.tag_ria_reserved_202 = Tag.objects.get(tag=202, ix=self.ria)
        self.tag_ria_reserved_202.status='ALLOCATED'
        self.tag_ria_reserved_202.save()
        self.tag_ria_reserved_203 = Tag.objects.get(tag=203, ix=self.ria)
        self.tag_ria_reserved_203.status='ALLOCATED'
        self.tag_ria_reserved_203.save()
        self.tag_ria_reserved_204 = Tag.objects.get(tag=204, ix=self.ria)
        self.tag_ria_reserved_204.status='ALLOCATED'
        self.tag_ria_reserved_204.save()
        self.tag_ria_reserved_205 = Tag.objects.get(tag=205, ix=self.ria)
        self.tag_ria_reserved_205.status='ALLOCATED'
        self.tag_ria_reserved_205.save()
        self.tag_ria_reserved_206 = Tag.objects.get(tag=206, ix=self.ria)
        self.tag_ria_reserved_206.status='ALLOCATED'
        self.tag_ria_reserved_206.save()
        self.tag_ria_reserved_207 = Tag.objects.get(tag=207, ix=self.ria)
        self.tag_ria_reserved_207.status='ALLOCATED'
        self.tag_ria_reserved_207.save()
        self.tag_ria_reserved_208 = Tag.objects.get(tag=208, ix=self.ria)
        self.tag_ria_reserved_208.status='ALLOCATED'
        self.tag_ria_reserved_208.save()
        self.tag_ria_reserved_209 = Tag.objects.get(tag=209, ix=self.ria)
        self.tag_ria_reserved_209.status='ALLOCATED'
        self.tag_ria_reserved_209.save()
        self.tag_ria_reserved_210 = Tag.objects.get(tag=210, ix=self.ria)
        self.tag_ria_reserved_210.status='ALLOCATED'
        self.tag_ria_reserved_210.save()
        self.tag_ria_reserved_301 = Tag.objects.get(tag=301, ix=self.ria)
        self.tag_ria_reserved_301.status='ALLOCATED'
        self.tag_ria_reserved_301.save()
        self.tag_ria_reserved_302 = Tag.objects.get(tag=302, ix=self.ria)
        self.tag_ria_reserved_302.status='ALLOCATED'
        self.tag_ria_reserved_302.save()
        self.tag_ria_reserved_303 = Tag.objects.get(tag=303, ix=self.ria)
        self.tag_ria_reserved_303.status='ALLOCATED'
        self.tag_ria_reserved_303.save()
        self.tag_ria_reserved_304 = Tag.objects.get(tag=304, ix=self.ria)
        self.tag_ria_reserved_304.status='ALLOCATED'
        self.tag_ria_reserved_304.save()
        self.tag_ria_reserved_305 = Tag.objects.get(tag=305, ix=self.ria)
        self.tag_ria_reserved_305.status='ALLOCATED'
        self.tag_ria_reserved_305.save()
        self.tag_ria_reserved_306 = Tag.objects.get(tag=306, ix=self.ria)
        self.tag_ria_reserved_306.status='ALLOCATED'
        self.tag_ria_reserved_306.save()
        self.tag_ria_reserved_307 = Tag.objects.get(tag=307, ix=self.ria)
        self.tag_ria_reserved_307.status='ALLOCATED'
        self.tag_ria_reserved_307.save()
        self.tag_ria_reserved_308 = Tag.objects.get(tag=308, ix=self.ria)
        self.tag_ria_reserved_308.status='ALLOCATED'
        self.tag_ria_reserved_308.save()
        self.tag_ria_reserved_309 = Tag.objects.get(tag=309, ix=self.ria)
        self.tag_ria_reserved_309.status='ALLOCATED'
        self.tag_ria_reserved_309.save()
        self.tag_ria_reserved_310 = Tag.objects.get(tag=310, ix=self.ria)
        self.tag_ria_reserved_310.status='ALLOCATED'
        self.tag_ria_reserved_310.save()

        self.tag_ria_simet_v4 = Tag.objects.get(tag=2008, ix=self.ria)
        self.tag_ria_simet_v4.status='PRODUCTION'
        self.tag_ria_simet_v4.save()
        self.tag_ria_simet_v6 = Tag.objects.get(tag=2009, ix=self.ria)
        self.tag_ria_simet_v6.status='PRODUCTION'
        self.tag_ria_simet_v6.save()


    def servicesRIA(self):
        self.mlpv4_ria_rs_1 = MLPAv4.objects.create(
            tag=self.tag_ria_rs_v4,
            asn=self.route_server,
            mlpav4_address=self.ipv4_ria_rs1,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.route_server.number) + 'mlpav4')
        self.mlpv6_ria_rs_1 = MLPAv6.objects.create(
            tag=self.tag_ria_rs_v6,
            asn=self.route_server,
            mlpav6_address=self.ipv6_ria_rs1,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1000,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.route_server.number) + 'mlpav6')

        self.mlpv4_ria_rs_2 = MLPAv4.objects.create(
            tag=self.tag_ria_rs_v4,
            asn=self.route_server,
            mlpav4_address=self.ipv4_ria_rs2,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.route_server.number) + 'mlpav4')
        self.mlpv6_ria_rs_2 = MLPAv6.objects.create(
            tag=self.tag_ria_rs_v6,
            asn=self.route_server,
            mlpav6_address=self.ipv6_ria_rs2,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1001,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.route_server.number) + 'mlpav6')

        self.mlpv4_ria_lg_sara = MLPAv4.objects.create(
            tag=self.tag_ria_rs_v4,
            asn=self.lg_sara,
            mlpav4_address=self.ipv4_ria_lg_sara,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.lg_sara.number) + 'mlpav4')
        self.mlpv6_ria_lg_sara = MLPAv6.objects.create(
            tag=self.tag_ria_rs_v6,
            asn=self.lg_sara,
            mlpav6_address=self.ipv6_ria_lg_sara,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1002,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.lg_sara.number) + 'mlpav6')

        self.mlpv4_ria_lg_meu_ix = MLPAv4.objects.create(
            tag=self.tag_ria_rs_v4,
            asn=self.lg_meu_ix,
            mlpav4_address=self.ipv4_ria_lg_meu_ix,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.lg_meu_ix.number) + 'mlpav4')
        self.mlpv6_ria_lg_meu_ix = MLPAv6.objects.create(
            tag=self.tag_ria_rs_v6,
            asn=self.lg_meu_ix,
            mlpav6_address=self.ipv6_ria_lg_meu_ix,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1003,
            customer_channel=self.customer_channel_gb2,
            shortname='as-' + str(self.lg_meu_ix.number) + 'mlpav6')

        self.mlpv4_ria_simet = MLPAv4.objects.create(
            tag=self.tag_ria_simet_v4,
            asn=self.simet,
            mlpav4_address=self.ipv4_ria_simet,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_simet_1,
            shortname='as-' + str(self.simet.number) + 'mlpav4')
        self.mlpv6_ria_simet = MLPAv6.objects.create(
            tag=self.tag_ria_simet_v6,
            asn=self.simet,
            mlpav6_address=self.ipv6_ria_simet,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1004,
            customer_channel=self.customer_channel_simet_1,
            shortname='as-' + str(self.simet.number) + 'mlpav6')



##########################################################################
#############               JOAO PESSOA                      #############
##########################################################################

    def createJPA(self):
        self.user = UserFactory()
        self.user.save()
        self.jpa = IX.objects.create(
            code='jpa',
            description='IX.br de Joao Pessoa',
            fullname='Joao Pessoa - JPA',
            ipv4_prefix='187.16.193.0/24',
            ipv6_prefix='2001:12f8:0:16::/64',
            last_ticket='0',
            modified_by=self.user,
            management_prefix='192.168.16.0/26',
            shortname='joaopessoa.pa',
            tags_policy='ix_managed',
            create_ips=True,
            create_tags=True)

    def createJPApix(self):

        self.anid = PIX.objects.create(
                ix = self.jpa,
                code = 'ANID',
                modified_by=self.user,
                last_ticket='2222'
            )

        self.hostdime = PIX.objects.create(
                ix = self.jpa,
                code = 'HOSTDIME',
                modified_by = self.user,
                last_ticket = '2222'
            )

    def createJPASwitche_01(self):
        # ############# Switch Settings #############
        self.extreme_01 = SwitchModel.objects.get(
            model='X460-48t')
        self.extreme_port_range_01 = SwitchPortRange.objects.create(
            switch_model=self.extreme_01,
            name_format='{0}',
            capacity=10000,
            connector_type='SFP+',
            begin=49, end=54,
            modified_by=self.user,
            last_ticket='2222')
        self.extreme_pix_anid_01 = Switch.objects.create(
            translation=False,
            pix=self.anid,
            model=self.extreme_01,
            management_ip='192.168.16.2',
            last_ticket='2222',
            modified_by=self.user,
            create_ports=True)

    def createJPASwitche_02(self):
        # ############# Switch Settings #############
        self.extreme_02 = SwitchModel.objects.create(
            model='X670-48x',
            vendor='EXTREME',
            modified_by=self.user,
            last_ticket='2222')
        self.extreme_port_range_02 = SwitchPortRange.objects.create(
            switch_model=self.extreme_02,
            name_format='{0}',
            capacity=10000,
            connector_type='SFP+',
            begin=1, end=48,
            modified_by=self.user,
            last_ticket='2222')
        self.extreme_pix_anid_02 = Switch.objects.create(
            translation=False,
            pix=self.anid,
            model=self.extreme_02,
            management_ip='192.168.16.3',
            last_ticket='2222',
            modified_by=self.user,
            create_ports=True)

    def createJPASwitche_03(self):
        # ############# Switch Settings #############
        self.extreme_pix_hostdime_01 = Switch.objects.create(
            translation=False,
            pix=self.hostdime,
            model=self.extreme_01,
            management_ip='192.168.16.4',
            last_ticket='2222',
            modified_by=self.user,
            create_ports=True)

    def createIPsJPA(self):

        self.ipv4_jpa_lg_meu_ix = IPv4Address.objects.get(address='187.16.193.249')
        self.ipv4_jpa_lg_meu_ix.in_lg=True
        
        self.ipv6_jpa_lg_meu_ix = IPv6Address.objects.get(address='2001:12f8:0:16::249')
        self.ipv6_jpa_lg_meu_ix.in_lg=True

        self.ipv4_jpa_lg_publico = IPv4Address.objects.get(address='187.16.193.250')
        self.ipv4_jpa_lg_publico.in_lg=True
        
        self.ipv6_jpa_lg_publico = IPv6Address.objects.get(address='2001:12f8:0:16::250')
        self.ipv6_jpa_lg_publico.in_lg=True

        self.ipv4_jpa_lg_sara = IPv4Address.objects.get(address='187.16.193.252')
        self.ipv4_jpa_lg_sara.in_lg=True
        
        self.ipv6_jpa_lg_sara = IPv6Address.objects.get(address='2001:12f8:0:16::252')
        self.ipv6_jpa_lg_sara.in_lg=True
        

        self.ipv4_jpa_rs1 = IPv4Address.objects.get(address='187.16.193.253')
        self.ipv4_jpa_rs1.in_lg=True
        
        self.ipv6_jpa_rs1 = IPv6Address.objects.get(address='2001:12f8:0:16::253')
        self.ipv6_jpa_rs1.in_lg=True
        
        self.ipv4_jpa_rs2 = IPv4Address.objects.get(address='187.16.193.254')
        self.ipv4_jpa_rs2.in_lg=True

        self.ipv6_jpa_rs2 = IPv6Address.objects.get(address='2001:12f8:0:16::254')
        self.ipv6_jpa_rs2.in_lg=True

    def createChannelPortJPA(self):

        self.channel_port_jpa_R430_38 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_39 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_40 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_41 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_42 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_43 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_idrac_44 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_45 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_46 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_R430_idrac_47 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_internet_48 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_uplink_sw2_sw3_53_54 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        # self.channel_port_jpa_simet_01 = ChannelPort.objects.create(
        #     tags_type='Port-Specific',
        #     last_ticket='2121',
        #     modified_by=self.user,
        #     create_tags=False)

        self.channel_port_jpa_downlink_sw2_sw3_45_46 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_downlink_sw3_sw4_47_48 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

        self.channel_port_jpa_uplink_sw3_sw4_53_54 = ChannelPort.objects.create(
            tags_type='Port-Specific',
            last_ticket='2121',
            modified_by=self.user,
            create_tags=False)

    def createPortJPA(self):

        self.port_jpa_sw02_38 = Port.objects.get(switch=self.extreme_pix_anid_01, name='38')
        self.port_jpa_sw02_38.channel_port=self.channel_port_jpa_R430_38
        self.port_jpa_sw02_38.status='UNAVAILABLE'
        self.port_jpa_sw02_38.save()

        self.port_jpa_sw02_39 = Port.objects.get(switch=self.extreme_pix_anid_01, name='39')
        self.port_jpa_sw02_39.channel_port=self.channel_port_jpa_R430_39
        self.port_jpa_sw02_39.status='UNAVAILABLE'
        self.port_jpa_sw02_39.save()

        self.port_jpa_sw02_40 = Port.objects.get(switch=self.extreme_pix_anid_01, name='40')
        self.port_jpa_sw02_40.channel_port=self.channel_port_jpa_R430_40
        self.port_jpa_sw02_40.status='UNAVAILABLE'
        self.port_jpa_sw02_40.save()

        self.port_jpa_sw02_41 = Port.objects.get(switch=self.extreme_pix_anid_01, name='41')
        self.port_jpa_sw02_41.channel_port=self.channel_port_jpa_R430_41
        self.port_jpa_sw02_41.status='UNAVAILABLE'
        self.port_jpa_sw02_41.save()

        self.port_jpa_sw02_42 = Port.objects.get(switch=self.extreme_pix_anid_01, name='42')
        self.port_jpa_sw02_42.channel_port=self.channel_port_jpa_R430_42
        self.port_jpa_sw02_42.status='UNAVAILABLE'
        self.port_jpa_sw02_42.save()

        self.port_jpa_sw02_43 = Port.objects.get(switch=self.extreme_pix_anid_01, name='43')
        self.port_jpa_sw02_43.channel_port=self.channel_port_jpa_R430_43
        self.port_jpa_sw02_43.status='UNAVAILABLE'
        self.port_jpa_sw02_43.save()

        self.port_jpa_sw02_44 = Port.objects.get(switch=self.extreme_pix_anid_01, name='44')
        self.port_jpa_sw02_44.channel_port=self.channel_port_jpa_R430_idrac_44
        self.port_jpa_sw02_44.status='UNAVAILABLE'
        self.port_jpa_sw02_44.save()

        self.port_jpa_sw02_45 = Port.objects.get(switch=self.extreme_pix_anid_01, name='45')
        self.port_jpa_sw02_45.channel_port=self.channel_port_jpa_R430_45
        self.port_jpa_sw02_45.status='UNAVAILABLE'
        self.port_jpa_sw02_45.save()

        self.port_jpa_sw02_46 = Port.objects.get(switch=self.extreme_pix_anid_01, name='46')
        self.port_jpa_sw02_46.channel_port=self.channel_port_jpa_R430_46
        self.port_jpa_sw02_46.status='UNAVAILABLE'
        self.port_jpa_sw02_46.save()

        self.port_jpa_sw02_47 = Port.objects.get(switch=self.extreme_pix_anid_01, name='47')
        self.port_jpa_sw02_47.channel_port=self.channel_port_jpa_R430_idrac_47
        self.port_jpa_sw02_47.status='UNAVAILABLE'
        self.port_jpa_sw02_47.save()

        self.port_jpa_sw02_48 = Port.objects.get(switch=self.extreme_pix_anid_01, name='48')
        self.port_jpa_sw02_48.channel_port=self.channel_port_jpa_internet_48
        self.port_jpa_sw02_48.status='UNAVAILABLE'
        self.port_jpa_sw02_48.save()

        self.port_jpa_sw02_53 = Port.objects.get(switch=self.extreme_pix_anid_01, name='53')
        self.port_jpa_sw02_53.channel_port=self.channel_port_jpa_uplink_sw2_sw3_53_54
        self.port_jpa_sw02_53.status='INFRASTRUCTURE'
        self.port_jpa_sw02_53.save()

        self.port_jpa_sw02_54 = Port.objects.get(switch=self.extreme_pix_anid_01, name='54')
        self.port_jpa_sw02_54.channel_port=self.channel_port_jpa_uplink_sw2_sw3_53_54
        self.port_jpa_sw02_54.status='INFRASTRUCTURE'
        self.port_jpa_sw02_54.save()

        self.port_jpa_sw03_45 = Port.objects.get(switch=self.extreme_pix_anid_02, name='45')
        self.port_jpa_sw03_45.channel_port=self.channel_port_jpa_downlink_sw2_sw3_45_46
        self.port_jpa_sw03_45.status='INFRASTRUCTURE'
        self.port_jpa_sw03_45.save()

        self.port_jpa_sw03_46 = Port.objects.get(switch=self.extreme_pix_anid_02, name='46')
        self.port_jpa_sw03_46.channel_port=self.channel_port_jpa_downlink_sw2_sw3_45_46
        self.port_jpa_sw03_46.status='INFRASTRUCTURE'
        self.port_jpa_sw03_46.save()

        self.route_01 = Route.objects.create(
            description='Av. RS - Rota 1',
            last_ticket='0',
            modified_by=self.user)
        self.route_02 = Route.objects.create(
            description='Av. RS - Rota 2',
            last_ticket='0',
            modified_by=self.user)

        self.port_jpa_sw03_47 = Port.objects.get(switch=self.extreme_pix_anid_02, name='47')
        self.port_jpa_sw03_47.channel_port=self.channel_port_jpa_downlink_sw3_sw4_47_48
        self.port_jpa_sw03_47.status='INFRASTRUCTURE'
        self.port_jpa_sw03_47.route=self.route_01
        self.port_jpa_sw03_47.save()

        self.port_jpa_sw03_48 = Port.objects.get(switch=self.extreme_pix_anid_02, name='48')
        self.port_jpa_sw03_48.channel_port=self.channel_port_jpa_downlink_sw3_sw4_47_48
        self.port_jpa_sw03_48.status='INFRASTRUCTURE'
        self.port_jpa_sw03_48.route=self.route_02
        self.port_jpa_sw03_48.save()

        self.port_jpa_sw04_53 = Port.objects.get(switch=self.extreme_pix_hostdime_01, name='53')
        self.port_jpa_sw04_53.channel_port=self.channel_port_jpa_uplink_sw3_sw4_53_54
        self.port_jpa_sw04_53.status='INFRASTRUCTURE'
        self.port_jpa_sw04_53.route=self.route_01
        self.port_jpa_sw04_53.save()

        self.port_jpa_sw04_54 = Port.objects.get(switch=self.extreme_pix_hostdime_01, name='54')
        self.port_jpa_sw04_54.channel_port=self.channel_port_jpa_uplink_sw3_sw4_53_54
        self.port_jpa_sw04_54.status='INFRASTRUCTURE'
        self.port_jpa_sw04_54.route=self.route_02
        self.port_jpa_sw04_54.save()

    def createCustomerChannelJPA(self):
        self.customer_channel_gb3_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-38',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_38)

        self.customer_channel_gb4_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-39',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_39)

        self.customer_channel_gb3_2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-40',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_40)

        self.customer_channel_gb4_2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-41',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_41)

        self.customer_channel_gb1_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-42',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_42)

        self.customer_channel_gb2_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-43',
            last_ticket='663',
            modified_by=self.user,
            cix_type=1,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_43)

        self.customer_channel_idrac_1 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-44',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_idrac_44)

        self.customer_channel_gb1_2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-45',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_45)

        self.customer_channel_gb2_2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-46',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_46)

        self.customer_channel_idrac_2 = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-47',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_R430_idrac_47)

        self.customer_channel_internet = CustomerChannel.objects.create(
            asn=self.route_server,
            name='ct-48',
            last_ticket='663',
            modified_by=self.user,
            cix_type=0,
            is_lag=False,
            is_mclag=False,
            channel_port=self.channel_port_jpa_internet_48)



        self.port_jpa_sw02_38.status='CUSTOMER'
        self.port_jpa_sw02_38.save()
        self.port_jpa_sw02_39.status='CUSTOMER'
        self.port_jpa_sw02_39.save()

        self.port_jpa_sw02_40.status='CUSTOMER'
        self.port_jpa_sw02_40.save()

        self.port_jpa_sw02_41.status='CUSTOMER'
        self.port_jpa_sw02_41.save()

        self.port_jpa_sw02_42.status='CUSTOMER'
        self.port_jpa_sw02_42.save()

        self.port_jpa_sw02_43.status='CUSTOMER'
        self.port_jpa_sw02_43.save()

        self.port_jpa_sw02_44.status='CUSTOMER'
        self.port_jpa_sw02_44.save()

        self.port_jpa_sw02_45.status='CUSTOMER'
        self.port_jpa_sw02_45.save()

        self.port_jpa_sw02_46.status='CUSTOMER'
        self.port_jpa_sw02_46.save()

        self.port_jpa_sw02_47.status='CUSTOMER'
        self.port_jpa_sw02_47.save()

        self.port_jpa_sw02_48.status='CUSTOMER'
        self.port_jpa_sw02_48.save()

    def createInfraChannelJPA(self):
        self.downlink_channel_sw2_sw3 = DownlinkChannel.objects.create(
            name='dl-45',
            is_lag=True,
            is_mclag=False,
            channel_port=self.channel_port_jpa_downlink_sw2_sw3_45_46,
            modified_by=self.user,
            last_ticket='4454')

        self.uplink_channel_sw2_sw3 = UplinkChannel.objects.create(
            name='ul-53',
            is_lag=True,
            is_mclag=False,
            downlink_channel=self.downlink_channel_sw2_sw3,
            channel_port=self.channel_port_jpa_uplink_sw2_sw3_53_54,
            modified_by=self.user,
            last_ticket='4454')

        self.downlink_channel_sw3_sw4 = DownlinkChannel.objects.create(
            name='dl-47',
            is_lag=True,
            is_mclag=False,
            channel_port=self.channel_port_jpa_downlink_sw3_sw4_47_48,
            modified_by=self.user,
            last_ticket='4454')

        self.uplink_channel_sw3_sw4 = UplinkChannel.objects.create(
            name='ul-53',
            is_lag=True,
            is_mclag=False,
            downlink_channel=self.downlink_channel_sw3_sw4,
            channel_port=self.channel_port_jpa_uplink_sw3_sw4_53_54,
            modified_by=self.user,
            last_ticket='4454')


    def tagsJPA(self):
        # ############# Tag Setttings #############
        self.tag_jpa_rs_v4 = Tag.objects.get(tag=10, ix=self.jpa)
        self.tag_jpa_rs_v4.status='PRODUCTION'
        self.tag_jpa_rs_v6 = Tag.objects.get(tag=20, ix=self.jpa)
        self.tag_jpa_rs_v6.status='PRODUCTION'
        self.tag_jpa_public_1 = Tag.objects.get(tag=40, ix=self.jpa)
        self.tag_jpa_public_1.status='ALLOCATED'
        self.tag_jpa_public_2 = Tag.objects.get(tag=41, ix=self.jpa)
        self.tag_jpa_public_2.status='ALLOCATED'

        self.tag_jpa_drac = Tag.objects.get(tag=66, ix=self.jpa)
        self.tag_jpa_drac.status='ALLOCATED'
        self.tag_jpa_mgmt = Tag.objects.get(tag=99, ix=self.jpa)
        self.tag_jpa_mgmt.status='ALLOCATED'
        self.tag_jpa_servers = Tag.objects.get(tag=100, ix=self.jpa)
        self.tag_jpa_servers.status='ALLOCATED'

        self.tag_jpa_reserved_201 = Tag.objects.get(tag=201, ix=self.jpa)
        self.tag_jpa_reserved_201.status='ALLOCATED'
        self.tag_jpa_reserved_202 = Tag.objects.get(tag=202, ix=self.jpa)
        self.tag_jpa_reserved_202.status='ALLOCATED'
        self.tag_jpa_reserved_203 = Tag.objects.get(tag=203, ix=self.jpa)
        self.tag_jpa_reserved_203.status='ALLOCATED'
        self.tag_jpa_reserved_204 = Tag.objects.get(tag=204, ix=self.jpa)
        self.tag_jpa_reserved_204.status='ALLOCATED'
        self.tag_jpa_reserved_205 = Tag.objects.get(tag=205, ix=self.jpa)
        self.tag_jpa_reserved_205.status='ALLOCATED'
        self.tag_jpa_reserved_206 = Tag.objects.get(tag=206, ix=self.jpa)
        self.tag_jpa_reserved_206.status='ALLOCATED'
        self.tag_jpa_reserved_207 = Tag.objects.get(tag=207, ix=self.jpa)
        self.tag_jpa_reserved_207.status='ALLOCATED'
        self.tag_jpa_reserved_208 = Tag.objects.get(tag=208, ix=self.jpa)
        self.tag_jpa_reserved_208.status='ALLOCATED'
        self.tag_jpa_reserved_209 = Tag.objects.get(tag=209, ix=self.jpa)
        self.tag_jpa_reserved_209.status='ALLOCATED'
        self.tag_jpa_reserved_210 = Tag.objects.get(tag=210, ix=self.jpa)
        self.tag_jpa_reserved_210.status='ALLOCATED'
        self.tag_jpa_reserved_301 = Tag.objects.get(tag=301, ix=self.jpa)
        self.tag_jpa_reserved_301.status='ALLOCATED'
        self.tag_jpa_reserved_302 = Tag.objects.get(tag=302, ix=self.jpa)
        self.tag_jpa_reserved_302.status='ALLOCATED'
        self.tag_jpa_reserved_303 = Tag.objects.get(tag=303, ix=self.jpa)
        self.tag_jpa_reserved_303.status='ALLOCATED'
        self.tag_jpa_reserved_304 = Tag.objects.get(tag=304, ix=self.jpa)
        self.tag_jpa_reserved_304.status='ALLOCATED'
        self.tag_jpa_reserved_305 = Tag.objects.get(tag=305, ix=self.jpa)
        self.tag_jpa_reserved_305.status='ALLOCATED'
        self.tag_jpa_reserved_306 = Tag.objects.get(tag=306, ix=self.jpa)
        self.tag_jpa_reserved_306.status='ALLOCATED'
        self.tag_jpa_reserved_307 = Tag.objects.get(tag=307, ix=self.jpa)
        self.tag_jpa_reserved_307.status='ALLOCATED'
        self.tag_jpa_reserved_308 = Tag.objects.get(tag=308, ix=self.jpa)
        self.tag_jpa_reserved_308.status='ALLOCATED'
        self.tag_jpa_reserved_309 = Tag.objects.get(tag=309, ix=self.jpa)
        self.tag_jpa_reserved_309.status='ALLOCATED'
        self.tag_jpa_reserved_310 = Tag.objects.get(tag=310, ix=self.jpa)
        self.tag_jpa_reserved_310.status='ALLOCATED'

    def servicesJPA(self):
        self.mlpv4_jpa_rs_1 = MLPAv4.objects.create(
            tag=self.tag_jpa_rs_v4,
            asn=self.route_server,
            mlpav4_address=self.ipv4_jpa_rs1,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.route_server.number) + 'mlpav4')
        self.mlpv6_jpa_rs_1 = MLPAv6.objects.create(
            tag=self.tag_jpa_rs_v6,
            asn=self.route_server,
            mlpav6_address=self.ipv6_jpa_rs1,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1000,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.route_server.number) + 'mlpav6')

        self.mlpv4_jpa_rs_2 = MLPAv4.objects.create(
            tag=self.tag_jpa_rs_v4,
            asn=self.route_server,
            mlpav4_address=self.ipv4_jpa_rs2,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.route_server.number) + 'mlpav4')
        self.mlpv6_jpa_rs_2 = MLPAv6.objects.create(
            tag=self.tag_jpa_rs_v6,
            asn=self.route_server,
            mlpav6_address=self.ipv6_jpa_rs2,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1001,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.route_server.number) + 'mlpav6')

        self.mlpv4_jpa_lg_meu_ix = MLPAv4.objects.create(
            tag=self.tag_jpa_rs_v4,
            asn=self.lg_meu_ix,
            mlpav4_address=self.ipv4_jpa_lg_meu_ix,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.lg_meu_ix.number) + 'mlpav4')
        self.mlpv6_jpa_lg_meu_ix = MLPAv6.objects.create(
            tag=self.tag_jpa_rs_v6,
            asn=self.lg_meu_ix,
            mlpav6_address=self.ipv6_jpa_lg_meu_ix,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1003,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.lg_meu_ix.number) + 'mlpav6')

        self.mlpv4_jpa_lg_sara = MLPAv4.objects.create(
            tag=self.tag_jpa_rs_v4,
            asn=self.lg_sara,
            mlpav4_address=self.ipv4_jpa_lg_sara,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.lg_sara.number) + 'mlpav4')
        self.mlpv6_jpa_lg_sara = MLPAv6.objects.create(
            tag=self.tag_jpa_rs_v6,
            asn=self.lg_sara,
            mlpav6_address=self.ipv6_jpa_lg_sara,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1002,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.lg_sara.number) + 'mlpav6')

        self.mlpv4_jpa_lg_publico = MLPAv4.objects.create(
            tag=self.tag_jpa_rs_v4,
            asn=self.lg_meu_ix,
            mlpav4_address=self.ipv4_jpa_lg_publico,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.route_server.number) + 'mlpav4')
        self.mlpv6_jpa_lg_publico = MLPAv6.objects.create(
            tag=self.tag_jpa_rs_v6,
            asn=self.lg_meu_ix,
            mlpav6_address=self.ipv6_jpa_lg_publico,
            status='INTERNAL',
            last_ticket='2121',
            modified_by=self.user,
            #inner=1002,
            customer_channel=self.customer_channel_gb2_1,
            shortname='as-' + str(self.route_server.number) + 'mlpav6')
