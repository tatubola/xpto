import ipaddress
import random
import string

import factory
from factory_djoy import CleanModelFactory

from ixbr_api.users.tests.factories import UserFactory

from .. import models
from ..utils.constants import (PORT_CAPACITY_CONNECTOR_TYPE,
                               PORT_TYPE_CONNECTOR_TYPE,)


class IXFactory(CleanModelFactory):

    class Meta:
        model = 'core.IX'

    # creates a code field following a list a sequence number given in sequence
    @factory.sequence
    def code(n):
        KNOWN_IX = ['sp', 'rj', 'ria', 'igu', 'cas', 'ce', 'cxj', 'vix', 'pr',
                    'ame', 'se', 'ba', 'bel', 'mg', 'df', 'rs', 'cgb', 'gyn',
                    'laj', 'mao', 'mgf', 'rn', 'pe', 'sca', 'sjc', 'es', 'cpv']

        if n < len(KNOWN_IX):
            return KNOWN_IX[n]

        while True:
            length = 2 if random.randint(0, 1) else 3
            code = ''.join(
                (random.choice(string.ascii_lowercase) for _ in range(length)))

            if not models.IX.objects.filter(code=code):
                return code

    shortname = factory.Iterator(['saopaulo.sp',
                                  'riodejaneiro.rj',
                                  'campinagrande.pb',
                                  'fozdoiguacu.pr',
                                  'campinas.sp',
                                  'fortaleza.ce',
                                  'caxiasdosul.rs',
                                  'vitoria.es',
                                  'curitiba.pr',
                                  'santamaria.rs'])

    fullname = factory.Iterator(['São Paulo - SP',
                                 'Rio de Janeiro - RJ',
                                 'Campina Grande - PB',
                                 'Foz do Iguaçu - PR',
                                 'Campinas - SP',
                                 'Fortaleza - CE',
                                 'Caxias do Sul - RS',
                                 'Vitória - ES',
                                 'Curitiba - PR',
                                 'Santa Maria - RS'])

    ipv4_prefix = factory.Iterator(['10.0.0.0/22',
                                    '11.0.0.0/24',
                                    '12.0.0.0/24',
                                    '13.0.0.0/24',
                                    '14.0.0.0/24',
                                    '15.0.0.0/24',
                                    '16.0.0.0/24',
                                    '17.0.0.0/24',
                                    '18.0.0.0/24', ])

    ipv6_prefix = factory.Iterator(['2001:12f0::0/64',
                                    '2001:12f1::0/64',
                                    '2001:12f2::0/64',
                                    '2001:12f3::0/64',
                                    '2001:12f4::0/64',
                                    '2001:12f5::0/64',
                                    '2001:12f6::0/64',
                                    '2001:12f7::0/64',
                                    '2001:12f8::0/64', ])

    management_prefix = factory.Iterator(['192.168.0.0/24',
                                          '192.168.1.0/24',
                                          '192.168.2.0/24',
                                          '192.168.3.0/24',
                                          '192.168.4.0/24',
                                          '192.168.5.0/24',
                                          '192.168.6.0/24',
                                          '192.168.7.0/24',
                                          '192.168.8.0/24', ])
    tags_policy = 'distributed'
    create_ips = False
    last_ticket = 0
    description = factory.LazyAttribute(
        lambda a: 'IX.br de {0}'.format(a.fullname))
    modified_by = factory.SubFactory(UserFactory)


class PIXFactory(CleanModelFactory):

    class Meta:
        model = 'core.PIX'

    ix = factory.SubFactory(IXFactory)
    code = factory.Faker('last_name_female')
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class OrganizationFactory(CleanModelFactory):

    class Meta:
        model = 'core.Organization'

    name = factory.Faker('company')
    shortname = factory.LazyAttribute(lambda a: '{0}'.format(
        a.name.split(' ')[0].split(',')[0].lower()))
    url = factory.Faker('url')
    cnpj = factory.Iterator(['11.626.836/0001-12',
                             '88.682.602/0001-17',])
    address = factory.Faker('address')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class ASNFactory(CleanModelFactory):

    class Meta:
        model = 'core.ASN'

    class Params:
        # See
        # https://factoryboy.readthedocs.io/en/latest/reference.html#factory.Trait
        ix = factory.Trait(
            #  SubFactory should be given as an absolute string because
            # it's not declared yet
            contacts_map__ix=factory.SelfAttribute('ix'))

    number = factory.Iterator([12000, 18881, 22548, 62000, 11000, 15000,
                               17000, 18000, 16397, 10733, 61860, 28206,
                               28580, 28630, 53065, 28165, 262750,
                               52992, 264598, 262887, 28343, 28292, 52869,
                               16735, 262579, 28657, 28360, 14551, 28272,
                               264367, 265110, 265464, 262650, 262807, 262605,
                               266065, 262878, 262883, 263047, 35788, 262791,
                               30122, 23128, 28326, 61905, 28198, 28264,
                               265271, 263165, 53068, 28328, 262893])

    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def contacts_map(obj, created, extracted, **kwargs):
        if not kwargs:
            return
        kwargs['asn'] = obj
        strategy = (factory.CREATE_STRATEGY
                    if created else factory.BUILD_STRATEGY)
        ContactsMapFactory.generate(strategy, **kwargs)


class ChannelPortFactory(CleanModelFactory):

    class Meta:
        model = 'core.ChannelPort'

    class Params:
        port__num = 1

    tags_type = 'Indirect-Bundle-Ether'
    create_tags = False
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def port(obj, *args, **kwargs):
        obj._options = kwargs


class ContactFactory(CleanModelFactory):

    class Meta:
        model = 'core.Contact'

    email = factory.Faker('company_email')
    name = factory.Faker('name')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class ContactsMapFactory(CleanModelFactory):

    class Meta:
        model = 'core.ContactsMap'

    ix = factory.SubFactory(IXFactory)
    asn = factory.SubFactory(ASNFactory)
    organization = factory.SubFactory(OrganizationFactory)
    noc_contact = factory.SubFactory(ContactFactory)
    adm_contact = factory.SubFactory(ContactFactory)
    peer_contact = factory.SubFactory(ContactFactory)
    com_contact = factory.SubFactory(ContactFactory)
    org_contact = factory.SubFactory(ContactFactory)
    peering_url = factory.Faker('url')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class DIOFactory(CleanModelFactory):

    class Meta:
        model = 'core.DIO'

    pix = factory.SubFactory(PIXFactory)
    name = factory.LazyAttribute(
        lambda a: 'DIO {0} {1}'.format(str(a.pix), random.randint(1, 20)))
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class IPv4AddressFactory(CleanModelFactory):

    class Meta:
        model = 'core.IPv4Address'

    address = factory.Faker('ipv4')
    reverse_dns = ''
    in_lg = factory.Faker('pybool')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)
    ix = factory.SubFactory(IXFactory)


class IPv6AddressFactory(CleanModelFactory):

    class Meta:
        model = 'core.IPv6Address'

    address = factory.Faker('ipv6')
    reverse_dns = ''
    in_lg = factory.Faker('pybool')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)
    ix = factory.SubFactory(IXFactory)


class MACAddressFactory(CleanModelFactory):

    class Meta:
        model = 'core.MACAddress'

    address = factory.Faker('mac_address')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class PhysicalInterfaceFactory(CleanModelFactory):

    class Meta:
        model = 'core.PhysicalInterface'

    serial_number = factory.Faker('pystr')
    connector_type = factory.Iterator(
        ['SFP', 'SFP+', 'XFP', 'CFP', 'CPAK', 'QSFP28'])
    port_type = factory.LazyAttribute(
        lambda o: PORT_TYPE_CONNECTOR_TYPE[o.connector_type][0])
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class PhoneFactory(CleanModelFactory):

    class Meta:
        model = 'core.Phone'

    number = factory.Sequence(lambda n: '1234-%04d' % n)
    contact = factory.SubFactory(ContactFactory)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class RouteFactory(CleanModelFactory):

    class Meta:
        model = 'core.Route'

    last_ticket = 0
    description = factory.Sequence(lambda a: 'route {0}'.format(a))
    modified_by = factory.SubFactory(UserFactory)


class SwitchModelFactory(CleanModelFactory):

    class Meta:
        model = 'core.SwitchModel'

    class Params:
        switch_ports_range = factory.Trait(
            create_ports=True)

    model = factory.Iterator(['X670a-48x',
                              'X480-48t',
                              'X450-24x',
                              'X350-48t',
                              'X460-48t'])

    vendor = 'EXTREME'
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def create_ports(obj, created, extracted, **kwargs):
        if not extracted:
            return
        kwargs['switch_model'] = obj
        strategy = (factory.CREATE_STRATEGY
                    if created else factory.BUILD_STRATEGY)
        SwitchPortRangeFactory.generate(strategy, **kwargs)


class SwitchPortRangeFactory(CleanModelFactory):

    class Meta:
        model = 'core.SwitchPortRange'

    capacity = factory.Iterator([100, 1000, 10000, 40000, 100000, 400000])

    connector_type = factory.Iterator(
        ['SFP', 'SFP+', 'XFP', 'CFP', 'CPAK', 'QSFP28'])

    name_format = factory.Iterator(['{0}'])
    begin = 1
    # end = 2 + random.randint(0, 25)
    end = 25
    switch_model = factory.SubFactory(SwitchModelFactory)
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class SwitchFactory(CleanModelFactory):

    class Meta:
        model = 'core.Switch'

    pix = factory.SubFactory(PIXFactory)
    is_pe = False
    model = factory.SubFactory(SwitchModelFactory, switch_ports_range=True)
    translation = False
    create_ports = False
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)
    while True:
        try:
            management_ip = factory.LazyAttribute(
                lambda a: ipaddress.ip_network(
                    a.pix.ix.management_prefix).network_address +
                random.randint(1, 252))
            break
        except Exception:
            pass

#    @factory.lazy_attribute_sequence
#    def management_ip(self, n):
# return
# ipaddress.ip_network(self.pix.ix.management_prefix).network_address + n


class PortFactory(CleanModelFactory):

    class Meta:
        model = 'core.Port'

    name = factory.Sequence(lambda n: '%s' % n)
    connector_type = factory.Iterator(['SFP', 'SFP+', 'XFP', 'CFP', 'QSFP28'])
    channel_port = None
    capacity = factory.LazyAttribute(
        lambda o: PORT_CAPACITY_CONNECTOR_TYPE[o.connector_type][0])
    physical_interface = factory.SubFactory(
        PhysicalInterfaceFactory,
        connector_type=factory.SelfAttribute('..connector_type'))
    switch = factory.SubFactory(SwitchFactory)
    route = None
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)
    status = "AVAILABLE"
    # status = factory.Iterator(["AVAILABLE","CUSTOMER","INFRASTRUCTURE"])


class DIOPortFactory(CleanModelFactory):

    class Meta:
        model = 'core.DIOPort'

    dio = factory.SubFactory(DIOFactory)
    ix_position = factory.Faker('sentence', nb_words=13)
    datacenter_position = factory.Faker('sentence', nb_words=13)
    switch_port = factory.SubFactory(
        PortFactory, connector_type='SFP', capacity=1000)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class CoreChannelFactory(CleanModelFactory):

    class Meta:
        model = 'core.CoreChannel'

    name = factory.LazyAttribute(
        lambda a: 'cc-{0}'.format(random.randint(1, 10)))
    is_lag = factory.Faker('pybool')
    is_mclag = False
    channel_port = factory.SubFactory(ChannelPortFactory)

    other_core_channel = None
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class CustomerChannelFactory(CleanModelFactory):

    class Meta:
        model = 'core.CustomerChannel'
        exclude = {'ix'}

    ix = factory.SubFactory(IXFactory)

    name = factory.LazyAttribute(
        lambda a: 'ct-{0}'.format(random.randint(1, 10)))
    is_lag = factory.Faker('pybool')
    is_mclag = False
    asn = factory.SubFactory(ASNFactory)
    cix_type = random.randint(0, 3)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    channel_port = factory.SubFactory(
        ChannelPortFactory, port__ix=factory.SelfAttribute('..ix'))

    #  The Ports must be created at this point, for a Port can only have a
    # PortChannel if the latter have a Channel. This method is called when both
    # the Channel and the PortChannel have been created
    def _after_postgeneration(obj, create, results):
        if hasattr(obj.channel_port, '_options') and obj.channel_port:
            strategy = (factory.CREATE_STRATEGY
                        if create else factory.BUILD_STRATEGY)
            options = obj.channel_port._options
            filters = {'channel_port': obj.channel_port, 'status': 'CUSTOMER'}

            if not options.get('ix', None):
                if obj.asn.contactsmap_set.exists():
                    filters[
                        'switch__pix__ix'] = obj.asn.contactsmap_set.first().ix
            else:
                filters['switch__pix__ix'] = options['ix']

            PortFactory.generate_batch(strategy, options['num'], **filters)

            del obj.channel_port._options

        return CleanModelFactory._after_postgeneration(obj, create, results)


class CustomerChannelFactoryVanilla(CleanModelFactory):

    class Meta:
        model = 'core.CustomerChannel'
        exclude = {'ix'}

    ix = factory.SubFactory(IXFactory)

    name = factory.LazyAttribute(
        lambda a: 'ct-{0}'.format(random.randint(1, 10)))
    is_lag = factory.Faker('pybool')
    is_mclag = False
    asn = factory.SubFactory(ASNFactory)
    cix_type = random.randint(0, 3)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    channel_port = factory.SubFactory(
        ChannelPortFactory, port__ix=factory.SelfAttribute('..ix'))


class DownlinkChannelFactory(CleanModelFactory):

    class Meta:
        model = 'core.DownlinkChannel'

    name = factory.LazyAttribute(
        lambda a: 'dl-{0}'.format(random.randint(1, 10)))
    is_lag = factory.Faker('pybool')
    is_mclag = False
    channel_port = factory.SubFactory(ChannelPortFactory)
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class TranslationChannelFactory(CleanModelFactory):

    class Meta:
        model = 'core.TranslationChannel'

    name = 'as{0}-tr'.format(random.randint(1, 50000))
    is_lag = factory.Faker('pybool')
    is_mclag = False
    channel_port = factory.SubFactory(ChannelPortFactory)

    customer_channel = factory.SubFactory(CustomerChannelFactory)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class UplinkChannelFactory(CleanModelFactory):

    class Meta:
        model = 'core.UplinkChannel'

    name = factory.LazyAttribute(
        lambda a: 'ul-{0}'.format(random.randint(1, 10)))
    is_lag = factory.Faker('pybool')
    is_mclag = False
    channel_port = factory.SubFactory(ChannelPortFactory)

    downlink_channel = factory.SubFactory(DownlinkChannelFactory)
    last_ticket = 0
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class TagFactory(CleanModelFactory):

    class Meta:
        model = 'core.Tag'

    tag = random.randint(0, 4095)
    ix = factory.SubFactory(IXFactory)
    tag_domain = None
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class BilateralPeerFactory(CleanModelFactory):

    class Meta:
        model = 'core.BilateralPeer'

    tag = factory.SubFactory(TagFactory)
    inner = random.randint(0, 4095)
    status = factory.Iterator(
        ['ALLOCATED', 'INTERNAL', 'PRODUCTION', 'QUARANTINE'])
    customer_channel = factory.SubFactory(CustomerChannelFactory)
    shortname = factory.LazyAttribute(
        lambda a: 'as{0}-bp'.format(a.asn.number))
    asn = factory.SubFactory(ASNFactory)
    # pe = factory.Faker('ipv4')
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def mac_addresses(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for mac_address in extracted:
                self.mac_addresses.add(mac_address)


class BilateralFactory(CleanModelFactory):

    class Meta:
        model = 'core.Bilateral'

    label = factory.LazyAttribute(
        lambda a: 'AS{0}-AS{1}'.format(
            a.peer_a.asn.number, a.peer_b.asn.number))
    bilateral_type = factory.Iterator(['L2', 'VPWS', 'VXLAN'])
    peer_a = factory.SubFactory(BilateralPeerFactory)
    peer_b = factory.SubFactory(BilateralPeerFactory)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)


class MLPAv4Factory(CleanModelFactory):

    class Meta:
        model = 'core.MLPAv4'

    inner = random.randint(0, 4095)
    status = factory.Iterator(
        ['ALLOCATED', 'INTERNAL', 'PRODUCTION', 'QUARANTINE'])
    shortname = factory.LazyAttribute(
        lambda a: 'as{0}-mlpav4'.format(a.asn.number))
    mlpav4_address = factory.SubFactory(IPv4AddressFactory)
    prefix_limit = 100
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    asn = factory.SubFactory(
        ASNFactory,
        ix=factory.SelfAttribute('..mlpav4_address.ix'))

    customer_channel = factory.SubFactory(
        CustomerChannelFactory,
        asn=factory.SelfAttribute('..asn'),
        ix=factory.SelfAttribute('..mlpav4_address.ix'))

    tag = factory.SubFactory(
        TagFactory,
        ix=factory.SelfAttribute('..mlpav4_address.ix'))

    @factory.post_generation
    def mac_addresses(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for mac_address in extracted:
                self.mac_addresses.add(mac_address)


class MLPAv6Factory(CleanModelFactory):

    class Meta:
        model = 'core.MLPAv6'

    inner = random.randint(0, 4095)
    status = factory.Iterator(
        ['ALLOCATED', 'INTERNAL', 'PRODUCTION', 'QUARANTINE'])
    shortname = factory.LazyAttribute(
        lambda a: 'as{0}-mlpav6'.format(a.asn.number))
    mlpav6_address = factory.SubFactory(IPv6AddressFactory)
    prefix_limit = 100
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    asn = factory.SubFactory(
        ASNFactory,
        ix=factory.SelfAttribute('..mlpav6_address.ix'))

    customer_channel = factory.SubFactory(
        CustomerChannelFactory,
        asn=factory.SelfAttribute('..asn'),
        ix=factory.SelfAttribute('..mlpav6_address.ix'))

    tag = factory.SubFactory(
        TagFactory,
        ix=factory.SelfAttribute('..mlpav6_address.ix'))

    @factory.post_generation
    def mac_addresses(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for mac_address in extracted:
                self.mac_addresses.add(mac_address)


class Monitorv4Factory(CleanModelFactory):

    class Meta:
        model = 'core.Monitorv4'

    inner = random.randint(0, 4095)
    status = factory.Iterator(
        ['ALLOCATED', 'INTERNAL', 'PRODUCTION', 'QUARANTINE'])
    shortname = factory.LazyAttribute(
        lambda a: 'as{0}-monitv4'.format(a.asn.number))
    monitor_address = factory.SubFactory(IPv4AddressFactory)
    last_ticket = factory.Faker('pyint')
    description = factory.Faker('bs')
    modified_by = factory.SubFactory(UserFactory)

    asn = factory.SubFactory(
        ASNFactory,
        ix=factory.SelfAttribute('..monitor_address.ix'))

    customer_channel = factory.SubFactory(
        CustomerChannelFactory,
        asn=factory.SelfAttribute('..asn'),
        ix=factory.SelfAttribute('..monitor_address.ix'))

    tag = factory.SubFactory(
        TagFactory,
        ix=factory.SelfAttribute('..monitor_address.ix'))

    @factory.post_generation
    def mac_addresses(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for mac_address in extracted:
                self.mac_addresses.add(mac_address)
