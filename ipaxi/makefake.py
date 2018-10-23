from ixbr_api.core.models import *
from ixbr_api.core.tests.factories import *

IXLIMIT = 3
PIXBYIX = 2
CONTACTSBYIX = 15
SWITCHBYPIX = 2
MACSLIMIT = CONTACTSBYIX*PIXBYIX*IXLIMIT*2

class MakeFakeData(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MakeFakeData, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.ixs = []
        self.user = UserFactory()
        self.user.save()

    def createIX(self):
        for x in range(IXLIMIT):
            self.ix = IXFactory(modified_by=self.user)
            self.ix.save()
            self.ixs.append(self.ix)
            print("created ix %s : "%(x) + str(self.ix) )

    def createPIX(self):
        for ix in self.ixs:
            for i in range(PIXBYIX):
                self.pix = PIXFactory(ix = ix, modified_by=self.user)
                self.pix.save()
                print("created pix %s in" %i +str(ix))

    def createContacts(self):
        for ix in self.ixs:
            for i in range(CONTACTSBYIX):
                self.asn = ASNFactory(modified_by=self.user)
                self.org = OrganizationFactory(modified_by=self.user)
                self.phone = PhoneFactory()
                self.contact = self.phone.contact
                self.map = ContactsMapFactory(organization=self.org,
                    asn=self.asn, ix = ix, noc_contact=self.contact, 
                    modified_by=self.user)
                self.asn.save()
                self.phone.save()
                self.contact.save()
                self.map.save()
                print("created contact " + str(self.contact) + " in ix " + str(ix))

    def createSwitches(self):
        self.range = SwitchPortRangeFactory(modified_by=self.user)
        self.model = SwitchModelFactory(switch_ports_range=self.range, modified_by=self.user)
        for pix in PIX.objects.all():
            for i in range(SWITCHBYPIX):
                self.switch = SwitchFactory(pix=pix, model=self.model, create_ports=True, 
                    modified_by=self.user)
                print("created switch %s "%i + "in PIX " + str(pix))

    def createCustomerChannels(self):
        asnlist = {}

        for ix in IX.objects.all():
            asnlist[ix.pk] = []
            for asn in ASN.objects.filter(contactsmap__ix__pk=ix.pk):
                asnlist[ix.pk].append(asn)

        for switch in list(Switch.objects.all()):
            portlist = list(switch.port_set.all())
            for i in range(round(CONTACTSBYIX/(SWITCHBYPIX*PIXBYIX))-1):
                if i == round(CONTACTSBYIX/(SWITCHBYPIX*PIXBYIX))-2:
                    for i in range(1):
                        self.channelport = ChannelPortFactory(modified_by=self.user)
                        current_asn = asnlist[str(switch.pix.ix.pk)].pop()
                        self.customer = CustomerChannelFactoryVanilla(ix=IX.objects.get(pk='sp'), channel_port=self.channelport, is_lag=True, asn=current_asn,
                            modified_by=self.user)
                        self.porta = portlist.pop()
                        self.porta.channel_port = self.channelport
                        self.porta.status = 'CUSTOMER'                        
                        self.portb = portlist.pop()
                        self.portb.channel_port = self.channelport
                        self.portb.status = 'CUSTOMER'
                        print("created LAG Customer Channel in Pix: " + str(switch.pix) + " Switch " + str(switch) + " owner " + str(current_asn))
                        self.channelport.save()
                        self.porta.save()
                        self.portb.save()
                        self.customer.save()
                    break
                else:
                    self.channelport = ChannelPortFactory(modified_by=self.user)
                    current_asn = asnlist[str(switch.pix.ix.pk)].pop()
                    self.customer = CustomerChannelFactoryVanilla(ix=IX.objects.get(pk='sp'), channel_port=self.channelport, is_lag=False, asn=current_asn,
                        modified_by=self.user)
                    self.porta = portlist.pop()
                    self.porta.channel_port = self.channelport
                    self.porta.status = 'CUSTOMER'
                    print("created Customer Channel in Pix: " + str(switch.pix) + " Switch " + str(switch) + " owner " + str(current_asn))
                    self.channelport.save()
                    self.porta.save()
                    self.customer.save()

        for ix in IX.objects.all():
            self.channelport = ChannelPortFactory(modified_by=self.user)
            self.downlink = DownlinkChannelFactory(modified_by=self.user, create_tags=True, is_pe=True, is_lag=False)
            self.ports = Port.objects.first(status='AVAILABLE', switch__pix__ix__pk=ix.pk)
            self.porta = self.ports.pop()
            self.porta.channel_port = self.channelport
            self.downlink.channel_port = self.channelport
            self.channelport.save()
            self.downlink.save()
            self.porta.save()
            print("created DownlinkChannel in Port " + str(self.porta) + " in Switch " + str(self.porta.switch))
            for port in ports:
                if port.switch.pix.pk == self.porta.switch.pix.pk:
                    ports.pop()
                else
                    self.portb = port
                    self.channelb = ChannelPortFactory(modified_by=self.user)
                    self.portb.channel_port = self.channelb
                    self.uplink = UplinkChannelFactory(modified_by=self.user,
                        downlink_channel=self.downlink, channel_port=self.channelb, is_lag=False)
                    self.portb.save()
                    self.channelb.save()
                    self.uplink.save()
                    print("created UplinkChannel in Port " + str(self.portb) + " in Switch " + str(self.portb.switch))
                    break




    def createMlpaServices(self):
        channels = list(CustomerChannel.objects.all())
        
        for number in range(MACSLIMIT):
            self.mac = MACAddressFactory()
            print("created MAC address: " + self.mac.address)
            self.mac.save()

        for channel in channels:
            print(channel)

    def makeData(self):
        self.createIX()
        self.createPIX()
        self.createContacts()
        self.createSwitches()
        self.createCustomerChannels()
        self.createMlpaServices()
