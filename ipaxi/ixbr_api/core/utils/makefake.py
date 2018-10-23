from ixbr_api.core.models import *
from ixbr_api.core.tests.factories import *

CONTACTSBYIX = 15


class MakeFakeData(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MakeFakeData, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.ixs = []
        self.user = UserFactory()
        self.user.save()

        self.ports_ext_pix1_sp = []
        self.ports_pe_pix2_sp = []

        self.ports_ext_pix1_cpv = []

        self.channel_port_cisco_ext_pix1_sp = None

    def createIX(self):
        self.sp = IXFactory(code='sp',
                            shortname='saopaulo.sp',
                            fullname='São Paulo - SP',
                            create_ips=True,
                            tags_policy='distributed')
        print('IX sp created')
        self.cpv = IXFactory(code='cpv',
                             shortname='campinagrande.pb',
                             fullname='Campina Grande - PB',
                             create_ips=True,
                             tags_policy='ix_managed')
        print('IX cpv created')

    def createPIX(self):
        self.pix_sp_1 = PIXFactory(ix=self.sp)
        print('PIX ' + self.pix_sp_1.code + ' in sp created')
        self.pix_sp_2 = PIXFactory(ix=self.sp)
        print('PIX ' + self.pix_sp_2.code + ' in sp created')
        self.pix_cpv_1 = PIXFactory(ix=self.cpv)
        print('PIX ' + self.pix_cpv_1.code + ' in cpv created')
        self.pix_cpv_2 = PIXFactory(ix=self.cpv)
        print('PIX ' + self.pix_cpv_2.code + ' in cpv created')

    def createSwitches(self):
        self.cisco = SwitchModelFactory(model='ASR9922', vendor='CISCO')
        print('Cisco switch model created')
        self.ext = SwitchModelFactory(model='X670a-48x', vendor='EXTREME')
        print('Extreme switch model created')
        self.port_cisco = SwitchPortRangeFactory(name_format='TenGigE0/0/0/{0}',
                                                 capacity=1000, connector_type='SFP', switch_model=self.cisco)
        print('Cisco port range created')
        self.port_ext = SwitchPortRangeFactory(name_format='{0}',
                                               capacity=1000, connector_type='SFP', switch_model=self.ext)
        print('Extreme port range created')

        self.cisco_pix1_sp = SwitchFactory(
            model=self.cisco, create_ports=True, pix=self.pix_sp_1)
        self.cisco_pix1_sp.is_pe = True
        self.cisco_pix1_sp.save()
        print('Pix1 SP Cisco PE created')

        self.ext_pix1_sp = SwitchFactory(
            model=self.ext, create_ports=True, pix=self.pix_sp_1)
        print('Pix1 SP Extreme created')

        self.cisco_pix2_sp = SwitchFactory(
            model=self.cisco, create_ports=True, pix=self.pix_sp_2)
        self.cisco_pix2_sp.is_pe = True
        self.cisco_pix2_sp.save()
        print('Pix2 SP Cisco PE created')

        self.ext_pix2_sp = SwitchFactory(
            model=self.ext, create_ports=True, pix=self.pix_sp_2)
        print('Pix2 SP Extreme created')

        self.ext_pix1_cpv = SwitchFactory(
            model=self.ext, create_ports=True, pix=self.pix_cpv_1)
        print('Pix1 CPV Extreme created')

        self.ext_pix2_cpv = SwitchFactory(
            model=self.ext, create_ports=True, pix=self.pix_cpv_2)
        print('Pix2 CPV Extreme created')

        self.ports_pe_pix1_sp = list(
            Port.objects.filter(switch=self.cisco_pix1_sp))
        self.ports_pe_pix2_sp = list(
            Port.objects.filter(switch=self.cisco_pix2_sp))

        self.ports_ext_pix1_sp = list(
            Port.objects.filter(switch=self.ext_pix1_sp))
        self.ports_ext_pix2_sp = list(
            Port.objects.filter(switch=self.ext_pix2_sp))

        self.channel_port_ext_cisco_pix1_sp = ChannelPortFactory(
            create_tags=False, tags_type='Indirect-Bundle-Ether')
        print('Channel Port extreme pix1 SP created')

        self.channel_port_cisco_ext_pix1_sp = ChannelPortFactory(
            create_tags=False, tags_type='Direct-Bundle-Ether')
        print('Channel Port cisco pe pix1 SP created')

        self.channel_port_cisco1_cisco2_sp = ChannelPortFactory(
            create_tags=False, tags_type='Core')
        print('Channel Port cisco pix1  cisco pix2 SP created')

        self.channel_port_cisco2_cisco1_sp = ChannelPortFactory(
            create_tags=False, tags_type='Core')
        print('Channel Port cisco pix2  cisco pix1 SP created')

        self.channel_port_ext_cisco_pix2_sp = ChannelPortFactory(
            create_tags=False, tags_type='Indirect-Bundle-Ether')
        print('Channel Port extreme pix2 SP created')

        self.channel_port_cisco_ext_pix2_sp = ChannelPortFactory(
            create_tags=False, tags_type='Direct-Bundle-Ether')
        print('Channel Port cisco pe pix2 SP created')

        # exteme pix 1 to cisco pe pix 1

        self.port_channel_port_cisco_ext_pix1_sp = self.ports_pe_pix1_sp.pop()
        self.port_channel_port_cisco_ext_pix1_sp.channel_port = self.channel_port_cisco_ext_pix1_sp
        self.port_channel_port_cisco_ext_pix1_sp.status = 'INFRASTRUCTURE'
        self.port_channel_port_cisco_ext_pix1_sp.save()
        self.downlink_cisco_ext_pix1_sp = DownlinkChannelFactory(
            name='dl-BE1010', is_lag=False,
            channel_port=self.channel_port_cisco_ext_pix1_sp)
        print('Downlink channel cisco pe pix1 sp created')

        self.channel_port_cisco_ext_pix1_sp.create_tags = True
        self.channel_port_cisco_ext_pix1_sp.save()
        self.channel_port_cisco_ext_pix1_sp.create_tags = False
        self.channel_port_cisco_ext_pix1_sp.save()

        self.port_channel_port_ext_cisco_pix1_sp = self.ports_ext_pix1_sp.pop()
        self.port_channel_port_ext_cisco_pix1_sp.channel_port = self.channel_port_ext_cisco_pix1_sp
        self.port_channel_port_ext_cisco_pix1_sp.status = 'INFRASTRUCTURE'
        self.port_channel_port_ext_cisco_pix1_sp.save()
        self.uplink_ext_cisco_pix1_sp = UplinkChannelFactory(
            name='ul-1', is_lag=False,
            channel_port=self.channel_port_ext_cisco_pix1_sp,
            downlink_channel=self.downlink_cisco_ext_pix1_sp)
        print('Uplink channel extreme pix1 sp created')

        # lag core pix 1 to pix 2
        self.port1_channel_port_cisco2_cisco1_sp = self.ports_pe_pix2_sp.pop()
        self.port1_channel_port_cisco2_cisco1_sp.channel_port = self.channel_port_cisco2_cisco1_sp
        self.port1_channel_port_cisco2_cisco1_sp.status = 'INFRASTRUCTURE'
        self.port1_channel_port_cisco2_cisco1_sp.save()

        self.port2_channel_port_cisco2_cisco1_sp = self.ports_pe_pix2_sp.pop()
        self.port2_channel_port_cisco2_cisco1_sp.channel_port = self.channel_port_cisco2_cisco1_sp
        self.port2_channel_port_cisco2_cisco1_sp.status = 'INFRASTRUCTURE'
        self.port2_channel_port_cisco2_cisco1_sp.save()
        self.channel_port_cisco2_cisco1_sp.port_set.add(
            self.port1_channel_port_cisco2_cisco1_sp)
        self.channel_port_cisco2_cisco1_sp.port_set.add(
            self.port2_channel_port_cisco2_cisco1_sp)
        self.port2_channel_port_cisco2_cisco1_sp.save()

        self.core_cisco2_cisco1 = CoreChannelFactory(
            name='cc-BE1020', is_lag=True,
            channel_port=self.channel_port_cisco2_cisco1_sp)
        print('Core channel cisco pix2 to cisco pix1 sp created')

        self.port1_channel_port_cisco1_cisco2_sp = self.ports_pe_pix1_sp.pop()
        self.port1_channel_port_cisco1_cisco2_sp.channel_port = self.channel_port_cisco1_cisco2_sp
        self.port1_channel_port_cisco1_cisco2_sp.status = 'INFRASTRUCTURE'
        self.port1_channel_port_cisco1_cisco2_sp.save()

        self.port2_channel_port_cisco1_cisco2_sp = self.ports_pe_pix1_sp.pop()
        self.port2_channel_port_cisco1_cisco2_sp.channel_port = self.channel_port_cisco1_cisco2_sp
        self.port2_channel_port_cisco1_cisco2_sp.status = 'INFRASTRUCTURE'
        self.port2_channel_port_cisco1_cisco2_sp.save()
        self.core_cisco1_cisco2 = CoreChannelFactory(
            name='cc-BE1020', is_lag=True,
            channel_port=self.channel_port_cisco1_cisco2_sp)
        print('Core channel cisco pix1 to cisco pix2 sp created')

        ###########

        # extreme pix 2 to cisco pe pix 2
        self.port_channel_port_cisco_ext_pix2_sp = self.ports_pe_pix2_sp.pop()
        self.port_channel_port_cisco_ext_pix2_sp.channel_port = self.channel_port_cisco_ext_pix2_sp
        self.port_channel_port_cisco_ext_pix2_sp.status = 'INFRASTRUCTURE'
        self.port_channel_port_cisco_ext_pix2_sp.save()
        self.channel_port_cisco_ext_pix2_sp.port_set.add(
            self.port_channel_port_cisco_ext_pix2_sp)
        self.downlink_cisco_ext_pix1_sp = DownlinkChannelFactory(
            name='dl-BE1110', is_lag=False,
            channel_port=self.channel_port_cisco_ext_pix2_sp)
        print('Downlink channel cisco pe pix 2 sp created')
        self.channel_port_cisco_ext_pix2_sp.create_tags = True
        self.channel_port_cisco_ext_pix2_sp.save()
        self.channel_port_cisco_ext_pix2_sp.create_tags = False
        self.channel_port_cisco_ext_pix2_sp.save()

        self.port_channel_port_ext_cisco_pix2_sp = self.ports_ext_pix2_sp.pop()
        self.port_channel_port_ext_cisco_pix2_sp.channel_port = self.channel_port_ext_cisco_pix2_sp
        self.port_channel_port_ext_cisco_pix2_sp.status = 'INFRASTRUCTURE'
        self.port_channel_port_ext_cisco_pix2_sp.save()
        self.uplink_ext_cisco_pix1_sp = UplinkChannelFactory(
            name='ul-1', is_lag=False,
            channel_port=self.channel_port_ext_cisco_pix2_sp,
            downlink_channel=self.downlink_cisco_ext_pix1_sp)
        print('Uplink channel extreme pix2 sp created')

        # EXTREMES CPV
        self.ports_ext_pix1_cpv = list(
            Port.objects.filter(switch=self.ext_pix1_cpv))
        self.ports_ext_pix2_cpv = list(
            Port.objects.filter(switch=self.ext_pix2_cpv))

        self.ext_pix1_cpv_ext_pix2_cpv_channel_port = ChannelPortFactory(
            create_tags=False, tags_type='Indirect-Bundle-Ether')

        self.ext_pix2_cpv_ext_pix1_cpv_channel_port = ChannelPortFactory(
            create_tags=False, tags_type='Indirect-Bundle-Ether')

        self.port_pop_ext_pix1_cpv = self.ports_ext_pix1_cpv.pop()
        self.port_pop_ext_pix1_cpv.channel_port = self.ext_pix1_cpv_ext_pix2_cpv_channel_port
        self.port_pop_ext_pix1_cpv.status = 'INFRASTRUCTURE'
        self.port_pop_ext_pix1_cpv.save()
        self.core_pix1_pix2_cpv = CoreChannelFactory(
            is_lag=False, channel_port=self.ext_pix1_cpv_ext_pix2_cpv_channel_port)
        print('Core channel pix1 to pix2 cpv created')

        self.port_pop_ext_pix2_cpv = self.ports_ext_pix2_cpv.pop()
        self.port_pop_ext_pix2_cpv.channel_port = self.ext_pix2_cpv_ext_pix1_cpv_channel_port
        self.port_pop_ext_pix2_cpv.status = 'INFRASTRUCTURE'
        self.port_pop_ext_pix2_cpv.save()
        self.core_pix2_pix1_cpv = CoreChannelFactory(
            name='cc-1', is_lag=False,
            channel_port=self.ext_pix2_cpv_ext_pix1_cpv_channel_port)
        print('Core channel pix1 to pix2 cpv created')

        self.channel_port_ext_cisco_pix1_sp.save()
        self.channel_port_cisco_ext_pix1_sp.save()
        self.channel_port_cisco1_cisco2_sp.save()
        self.channel_port_cisco2_cisco1_sp.save()
        self.channel_port_ext_cisco_pix2_sp.save()
        self.channel_port_cisco_ext_pix2_sp.save()

    def createContacts(self):
        for ix in IX.objects.all():
            for i in range(CONTACTSBYIX):
                self.asn = ASNFactory(modified_by=self.user)
                self.org = OrganizationFactory(modified_by=self.user)
                self.phone = PhoneFactory()
                self.contact = self.phone.contact
                self.map = ContactsMapFactory(organization=self.org,
                                              asn=self.asn, ix=ix, noc_contact=self.contact,
                                              modified_by=self.user)
                self.asn.save()
                self.phone.save()
                self.contact.save()
                self.map.save()
                print("created contact " +
                      str(self.contact) + " in ix " + str(ix))

    def createCustomerChannels(self):
        self.sp_asns = list(ASN.objects.filter(contactsmap__ix='sp'))
        self.cpv_asns = list(ASN.objects.filter(contactsmap__ix='cpv'))

        self.channel_port_sp_ext = ChannelPortFactory(
            create_tags=False, tags_type='Indirect-Bundle-Ether')
        self.port_customer_ext_pix1_sp = self.ports_ext_pix1_sp.pop()
        self.port_customer_ext_pix1_sp.channel_port = self.channel_port_sp_ext
        self.port_customer_ext_pix1_sp.status = 'CUSTOMER'

        self.channel_port_sp_ext.port_set.add(self.port_customer_ext_pix1_sp)

        self.customer_channel_ext_pix1_sp = CustomerChannelFactoryVanilla(
            channel_port=self.channel_port_sp_ext,
            ix=IX.objects.get(pk='sp'),
            is_lag=False,
            asn=self.sp_asns.pop(),
            cix_type=0)
        print('Customer Channel as ' +
              str(self.customer_channel_ext_pix1_sp.asn) + ' created')
        self.port_customer_ext_pix1_sp.save()

        self.channel_port_sp_cisco = ChannelPortFactory(
            create_tags=False, tags_type='Direct-Bundle-Ether')
        self.port_customer_cisco_pix2_sp = self.ports_pe_pix2_sp.pop()
        self.port_customer_cisco_pix2_sp.channel_port = self.channel_port_sp_cisco
        self.port_customer_cisco_pix2_sp.status = 'CUSTOMER'
        self.channel_port_sp_cisco.port_set.add(self.port_customer_cisco_pix2_sp)

        self.customer_channel_cisco_pix2_sp = CustomerChannelFactoryVanilla(
            name='ct-BE2010',
            channel_port=self.channel_port_sp_cisco,
            ix=IX.objects.get(pk='sp'),
            is_lag=False,
            asn=self.sp_asns.pop(),
            cix_type=0)
        self.port_customer_cisco_pix2_sp.save()
        print('Customer Channel as ' +
              str(self.customer_channel_cisco_pix2_sp.asn) + ' created at cisco')

        self.channel_port_cpv_ext = ChannelPortFactory(
            create_tags=False, tags_type='Indirect-Bundle-Ether')
        self.port_customer_ext_cpv = self.ports_ext_pix1_cpv.pop()
        self.port_customer_ext_cpv.channel_port = self.channel_port_cpv_ext
        self.port_customer_ext_cpv.status = 'CUSTOMER'

        self.channel_port_cpv_ext.port_set.add(self.port_customer_ext_cpv)

        self.customer_channel_ext_cpv = CustomerChannelFactoryVanilla(
            channel_port=self.channel_port_cpv_ext,
            ix=IX.objects.get(pk='cpv'),
            is_lag=False,
            asn=self.cpv_asns.pop(),
            cix_type=0)
        self.port_customer_ext_cpv.save()
        print('Customer Channel as ' +
              str(self.customer_channel_ext_cpv.asn) + ' created at cpv extreme')

        self.ipv4s_sp = list(IPv4Address.objects.filter(ix='sp'))
        self.ipv6s_sp = list(IPv6Address.objects.filter(ix='sp'))

        self.ipv4s_cpv = list(IPv4Address.objects.filter(ix='cpv'))
        self.ipv6s_cpv = list(IPv6Address.objects.filter(ix='cpv'))

        self.tags_ext_pix1_sp = list(Tag.objects.filter(
            tag_domain=self.channel_port_cisco_ext_pix1_sp))

        self.tag_mplpav4_extreme_sp = self.tags_ext_pix1_sp.pop()
        self.mlpav4_ext_sp = MLPAv4Factory(
            status='PRODUCTION',
            mlpav4_address=self.ipv4s_sp.pop(),
            asn=self.customer_channel_ext_pix1_sp.asn,
            customer_channel=self.customer_channel_ext_pix1_sp,
            tag=self.tag_mplpav4_extreme_sp)
        self.tag_mplpav4_extreme_sp.status = 'PRODUCTION'
        self.tag_mplpav4_extreme_sp.save()

        print('created MLPAv4 extreme pix1 SP')

        self.tag_mlpav6_cisco_sp = self.tags_ext_pix1_sp.pop()
        self.mlpav6_ext_sp = MLPAv6Factory(
            status='PRODUCTION',
            mlpav6_address=self.ipv6s_sp.pop(),
            asn=self.customer_channel_ext_pix1_sp.asn,
            customer_channel=self.customer_channel_ext_pix1_sp,
            tag=self.tag_mlpav6_cisco_sp)
        self.tag_mlpav6_cisco_sp.status = 'PRODUCTION'
        self.tag_mlpav6_cisco_sp.save()

        print('created MLPAv6 extreme pix1 SP')

        self.tag_mlpav4_cisco_sp = TagFactory(
            tag=1,
            ix=IX.objects.get(pk='sp'),
            tag_domain=self.channel_port_sp_cisco,
            status='PRODUCTION')
        self.mlpav4_ext_sp = MLPAv4Factory(
            status='PRODUCTION',
            mlpav4_address=self.ipv4s_sp.pop(),
            asn=self.customer_channel_cisco_pix2_sp.asn,
            customer_channel=self.customer_channel_cisco_pix2_sp,
            tag=self.tag_mlpav4_cisco_sp)
        print('created MLPAv4 cisco pix1 SP')

        self.tag_mlpav6_cisco_sp = TagFactory(
            tag=2,
            ix=IX.objects.get(pk='sp'),
            tag_domain=self.channel_port_sp_cisco,
            status='PRODUCTION')

        self.mlpav6_cisco_sp = MLPAv6Factory(
            status='PRODUCTION',
            mlpav6_address=self.ipv6s_sp.pop(),
            asn=self.customer_channel_cisco_pix2_sp.asn,
            customer_channel=self.customer_channel_cisco_pix2_sp,
            tag=self.tag_mlpav6_cisco_sp)

        print('created MLPAv6 cisco pix1 SP')

        self.tags_ext_pix1_cpv = list(
            Tag.objects.filter(ix=IX.objects.get(pk='cpv')))

        self.tag_mplpav4_extreme_cpv = self.tags_ext_pix1_cpv.pop()

        self.mlpav4_ext_cpv = MLPAv4Factory(
            status='PRODUCTION',
            mlpav4_address=self.ipv4s_cpv.pop(),
            asn=self.customer_channel_ext_cpv.asn,
            customer_channel=self.customer_channel_ext_cpv,
            tag=self.tag_mplpav4_extreme_cpv)

        self.tag_mplpav4_extreme_cpv.status = 'PRODUCTION'
        self.tag_mplpav4_extreme_cpv.save()

        print('created MLPAv4 extreme pix1 CPV')

        self.tag_mplpav6_extreme_cpv = self.tags_ext_pix1_cpv.pop()

        self.mlpav6_ext_cpv = MLPAv6Factory(
            status='PRODUCTION',
            mlpav6_address=self.ipv6s_cpv.pop(),
            asn=self.customer_channel_ext_cpv.asn,
            customer_channel=self.customer_channel_ext_cpv,
            tag=self.tag_mplpav4_extreme_cpv)
        self.tag_mplpav6_extreme_cpv.status = 'PRODUCTION'
        self.tag_mplpav6_extreme_cpv.save()

        print('created MLPAv6 extreme pix1 CPV')

    def makeData(self):
        self.createIX()
        self.createPIX()
        self.createSwitches()
        self.createContacts()
        self.createCustomerChannels()
