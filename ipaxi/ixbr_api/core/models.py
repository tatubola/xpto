import uuid
from difflib import SequenceMatcher
from logging import WARN

import ipaddress
from django.core.exceptions import ValidationError
from django.core.validators import (MaxLengthValidator, MaxValueValidator,
                                    MinLengthValidator, MinValueValidator,
                                    validate_email)
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from ixbr_api.users.models import User
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from .use_cases.mac_address_converter_to_system_pattern import \
    MACAddressConverterToSystemPattern
from .utils.calculate_percent_use_of_switch_ports import (
    calculate_percent_use_of_switch_ports)
from .utils.constants import (MAX_TAG_NUMBER, MIN_TAG_NUMBER,
                              PHYSICAL_INTERFACE_PORT_CONNECTOR_TYPE,
                              PORT_CAPACITY_CONNECTOR_TYPE,
                              PORT_TYPE_CONNECTOR_TYPE, VENDORS,
                              CAPACITIES_MAX, CAPACITIES_CONF,
                              CONNECTOR_TYPES, PORT_TYPES)
from .utils.globals import get_current_user
from .utils.logging_handlers import log_object
from .utils.port_utils import port_sorting
from .validators import (validate_as_number, validate_channel_name,
                         validate_cnpj, validate_ipv4_network,
                         validate_ipv6_network, validate_ix_code,
                         validate_ix_fullname, validate_ix_shortname,
                         validate_mac_address, validate_name_format,
                         validate_pix_code, validate_switch_model,
                         validate_url_format, RESERVED_IP)


class IXAPIQuerySet(QuerySet):
    """
    Adds a method to QuerySet class to handle Error when object does not exist.
    Method get_or_none can be used to return a NONE when a querie is issued
    and the given object does not exist.
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class PortQuerySet(IXAPIQuerySet):
    def order_by_port_name(self, **kwargs):
        return self.extra(
            select={
                'port_int':
                '''
                CAST
                    (REGEXP_REPLACE
                        (REGEXP_REPLACE(name, '([a-zA-Z]|(?:\s)|(?:-))','','g'),
                    '\/', '00','g')
                AS INTEGER)'''
            }).order_by('switch__management_ip', 'port_int')


class DIOPortQuerySet(IXAPIQuerySet):
    def order_by_datacenter_position(self, **kwargs):
        return self.extra(
            select={
                'datacenter_position_int':
                '''
                CAST
                    (REGEXP_REPLACE
                        (REGEXP_REPLACE(datacenter_position,
                        '([a-zA-Z]|(?:\s)|(?:-))','','g'),
                    '\/', '00','g')
                AS INTEGER)'''
            }).order_by('datacenter_position_int')


class HistoricalTimeStampedModel(TimeStampedModel):
    """
    An abstract base class model to track which user modified and
    stores the history related to model data.
    """
    modified_by = models.ForeignKey(User, models.PROTECT)
    history = HistoricalRecords(inherit=True)
    description = models.CharField(max_length=255, blank=True)
    last_ticket = models.PositiveIntegerField()
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    objects = IXAPIQuerySet.as_manager()

    class Meta:
        abstract = True
        get_latest_by = 'modified_date'
        ordering = 'modified_date'

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value

    # When use clean() method, remember that order matters,
    # for error messages and dealing with database.
    # Use block_update_pk() then block_update_fields() and
    # others validation.

    @property
    def resource_is_reservable(self):
        if getattr(self, "is_reserved", None):
            return True
        else:
            return False

    def save(self, *args, **kwargs):

        log_object("Object updated", self, **kwargs)

        modified_by = get_current_user()

        if self.resource_is_reservable:
            if self.is_reserved:
                raise ValidationError('This resource is Reserved')

        if not modified_by or not isinstance(modified_by, User):
            log_object("Could not get user that modified object",
                       self,
                       severity=WARN)
        else:
            self.modified_by = modified_by
        # Call clean validations before save.
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.resource_is_reservable:
            if self.is_reserved:
                raise ValidationError('This resource is Reserved')
        else:
            super().delete(*args, **kwargs)

    # Block pk field update
    def block_update_pk(self):
        if(not self._state.adding and
           not self.__class__.objects.filter(pk=self.pk)):
            raise ValidationError(_(
                'Trying to update non updatable field: {}.{}'.format(
                    self.__class__.__name__, self._meta.pk.name)))

    # Block field update passed as arg
    def block_update_fields(self, block_field):
        if self.__class__.objects.filter(pk=self.pk):
            old = self.__class__.objects.get(pk=self.pk)
            if self.__dict__[block_field] != old.__dict__[block_field]:
                raise ValidationError(
                    ('Trying to update non updatable field: {0}.{1}'.format(
                        self.__class__.__name__,
                        self.__class__._meta.get_field(block_field).name)))


class ReservableModel(models.Model):
    """
    This class is used to implement Resource Reservation for some models
    """

    reserved = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def reserve_this(self, *args, **kwargs):
        """ This method reserves the resource

        Returns: True if the resource was free and the reservation occurred
        successfully or False if the resource was alredy reserved.

        """
        if self.reserved:
            return False
        else:
            self.reserved = True
            self.full_clean()
            super().save(*args, **kwargs)
            return True

    def free_this(self, *args, **kwargs):
        """ This method free the resource

        Returns: True if the resource was reserved and freeing the resource
        occurred successfully or False if the resource was already free
        """
        if not self.reserved:
            return False
        else:
            self.reserved = False
            self.full_clean()
            super().save(*args, **kwargs)
            return True

    @property
    def is_reserved(self):
        """ Get the reservation status of a resource

        Returns: True if the resource is reserved or False otherwise

        """
        return self.reserved


class ASN(HistoricalTimeStampedModel):
    """Autonomous System (AS) Number representation."""
    uuid = None
    number = models.BigIntegerField(primary_key=True,
                                    validators=[validate_as_number])

    class Meta:
        ordering = ('number',)
        verbose_name = _('ASN')
        verbose_name_plural = _('ASNs')

    def __str__(self):
        if ContactsMap.objects.filter(asn=self):
            return "[AS%s: %s]" % (self.number, ContactsMap.objects.filter(
                asn=self)[0].organization,)
        else:
            return "[AS%s]" % (self.number,)

    def clean(self):
        self.block_update_pk()

    def get_stats_amount(self, ix):
        return {"mlpav4_amount": MLPAv4.objects.filter(asn=self.number,
                                                       tag__ix=ix).count(),
                "mlpav6_amount": MLPAv6.objects.filter(
                    asn=self.number, tag__ix=ix).count(),
                "bilateral_amount": BilateralPeer.objects.filter(
                    asn=self.number, tag__ix=ix).count()}


class Bilateral(HistoricalTimeStampedModel):
    """Bilateral peers' pair."""
    label = models.CharField(max_length=20, blank=True)

    BILATERAL_TYPES = (('L2', 'L2'),
                       ('VPWS', 'VPWS'),
                       ('VXLAN', 'VXLAN'),)
    bilateral_type = models.CharField(
        max_length=5, choices=BILATERAL_TYPES, default='L2')
    peer_a = models.OneToOneField(
        'BilateralPeer', models.PROTECT, related_name='peer_a_related')
    peer_b = models.OneToOneField(
        'BilateralPeer', models.PROTECT, related_name='peer_b_related')

    class Meta:
        ordering = ('label',)
        verbose_name = _('Bilateral')
        verbose_name_plural = _('Bilaterals')

    def __str__(self):
        return "[%s: AS%s-AS%s]" % (self.label,
                                    self.peer_a.asn.number,
                                    self.peer_b.asn.number,)

    def validate_different_peers(self):
        if self.peer_a == self.peer_b:
            raise ValidationError(_('Peer a and Peer b must be different.'))

    def validate_label_by_type(self):
        if self.bilateral_type == 'VPWS':
            try:
                i_label = int(self.label)
                if i_label.bit_length() > 64:
                    raise ValidationError(_('VPWS Bilateral\'s label must be '
                                            'a 64bits number'))
            except ValueError:
                raise ValidationError(_('VPWS Bilateral\'s label must be a '
                                        '64bits number'))
        if self.bilateral_type == 'VXLAN':
            try:
                i_label = int(self.label)
                if i_label.bit_length() > 24:
                    raise ValidationError(_('VXLAN Bilateral\'s label must be '
                                            'a 24bits number'))
            except ValueError:
                raise ValidationError(_('VXLAN Bilateral\'s label must be a '
                                        '24bits number'))

    def clean(self):
        self.block_update_fields('label')
        self.block_update_fields('peer_a_id')
        self.block_update_fields('peer_b_id')
        self.validate_different_peers()
        self.validate_label_by_type()


class Channel(HistoricalTimeStampedModel):
    """Network switch channel representation."""
    name = models.CharField(max_length=255)
    is_lag = models.BooleanField()
    is_mclag = models.BooleanField()
    channel_port = models.OneToOneField('ChannelPort', models.PROTECT)

    class Meta:
        abstract = True
        # Remember to put this line in derived classes
        # ordering = ('name',)
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')

    def validate_ports_channel(self):
        if(not self.is_mclag and
           Port.objects.filter(channel_port=self.channel_port)):
            switch_count = len(set(Port.objects.filter(
                channel_port=self.channel_port).values_list('switch',
                                                            flat=True)))
            if switch_count != 1:
                raise ValidationError(
                    _('Switch is not the same in ports of this Channel.'))
        elif self.is_mclag:
            ix = None
            for port in Port.objects.filter(channel_port=self.channel_port):
                if ix is None:
                    ix = port.switch.pix.ix
                elif port.switch.pix.ix != ix:
                    raise ValidationError(
                        _('IX is not the same in Switches of ports on this '
                          'Channel.'))

    def get_ports(self):
        return self.channel_port.port_set.all()

    def get_switches(self):
        switches = set([port.switch for port in self.get_ports()])
        if None in switches:
            switches.remove(None)
        return switches

    def is_extreme(self):
        vendors = [
        switch.model.vendor for switch in self.get_switches()]
        if 'EXTREME' in vendors:
            return True
        else:
            return False

    def check_channel_name_port(self):

        if self.is_extreme():
            for port in self.get_ports():
                if str(port.name) in self.name:
                    return True
            raise ValidationError(_("{} master port has nos association with him".
                               format(self.name)))
        else:
            True

    def get_master_port(self):

        if self.is_extreme() and self.check_channel_name_port():
            master_number = self.name.split("-")[1]
            master_port = self.get_ports().get(name=master_number)
            return master_port
        else:
            return self.get_ports().first()

    def clean(self):
        self.block_update_fields('channel_port_id')
        self.validate_ports_channel()
        self.check_channel_name_port()
        validate_channel_name(self)

    def __str__(self):
        lag = 'L' if self.is_lag else ''
        return "[%s%s]" % (self.name, lag, )

    @classmethod
    def get_channel_class(cls):
        return eval(cls.__name__)

    @classmethod
    def get_channels_of_switch(cls, switch):
        channel_class = cls.get_channel_class()
        if channel_class == Channel:
            channels = list()
            channels.extend(CustomerChannel.get_channels_of_switch(switch))
            channels.extend(DownlinkChannel.get_channels_of_switch(switch))
            channels.extend(UplinkChannel.get_channels_of_switch(switch))
            channels.extend(TranslationChannel.get_channels_of_switch(switch))
            channels.extend(CoreChannel.get_channels_of_switch(switch))
            return channels
        else:
            return list(cls.get_channel_class().objects.filter(
                channel_port__port__switch=switch))


class ChannelPort(HistoricalTimeStampedModel):
    """Model to relate a channel to a set of ports."""

    TAG_TYPES = (('Direct-Bundle-Ether', "Direct-Bundle-Ether"),
                 ('Indirect-Bundle-Ether', "Indirect-Bundle-Ether"),
                 ('Port-Specific', "Port-Specific"),
                 ('Core', "Core"),)
    tags_type = models.CharField(
        max_length=32, choices=TAG_TYPES, default='Direct-Bundle-Ether')
    create_tags = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('ChannelPort')
        verbose_name_plural = _('ChannelPorts')

    def __str__(self):
        return "[%s]" % (self.uuid, )


class Contact(HistoricalTimeStampedModel):
    """Organization contact representation."""
    email = models.EmailField(blank=True, validators=[validate_email])
    name = models.CharField(blank=True, max_length=255)

    class Meta:
        ordering = ('email',)
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return "[%s: %s]" % (self.email, self.name, )

    def clean(self):
        self.block_update_fields('email')
        self.block_update_fields('name')


class ContactsMap(HistoricalTimeStampedModel):
    ix = models.ForeignKey('IX', models.PROTECT)
    organization = models.ForeignKey('Organization', models.PROTECT,
                                     blank=True, null=True)
    asn = models.ForeignKey('ASN', models.PROTECT,
                            verbose_name=ASN._meta.verbose_name)
    noc_contact = models.ForeignKey(
        'Contact', models.PROTECT, related_name='noc_related')
    adm_contact = models.ForeignKey(
        'Contact', models.PROTECT, related_name='adm_related')
    peer_contact = models.ForeignKey(
        'Contact', models.PROTECT, related_name='peer_related')
    com_contact = models.ForeignKey(
        'Contact', models.PROTECT, related_name='com_related')
    org_contact = models.ForeignKey(
        'Contact', models.PROTECT, related_name='org_related')
    peering_url = models.CharField(
        max_length=255, validators=[validate_url_format])

    POLICIES = (('OPEN', 'All peering accepted'),
                ('CASE-BY-CASE', 'Peer decide case by case'),
                ('SELECTIVE', 'Peer in ATM but in selective perspective'),
                ('CLOSED', 'Only Bilateral'),
                ('CUSTOM', 'Peer in ATM but Bilateral selective'),
                ('ROUTE-SERVER-ONLY', 'Just receive routes'), )
    peering_policy = models.CharField(
        max_length=32, choices=POLICIES, default='OPEN')

    class Meta:
        unique_together = (('organization', 'asn', 'ix'),)
        ordering = ('asn', 'ix', )
        verbose_name = _('ContactsMap')
        verbose_name_plural = _('ContactsMaps')

    def __str__(self):
        return "[AS%s: %s: %s]" % (self.asn, self.ix, self.peer_contact,)

    def clean(self):
        self.block_update_fields('ix_id')


class DIO(HistoricalTimeStampedModel):
    """DIO representation."""
    pix = \
        models.ForeignKey('PIX', models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255,
                            validators=[MinLengthValidator(10),
                                        MaxLengthValidator(255)])

    class Meta:
        unique_together = (('pix', 'name'),)
        ordering = ('pix', 'name',)
        verbose_name = _('DIO')
        verbose_name_plural = _('DIOs')

    def __str__(self):
        return "[PIX %s: DIO %s]" % (self.pix.code, self.name, )

    def clean(self):
        self.block_update_fields('pix_id')

    def validate_unique_ix_position(self, dio_port, ix_position):
        return self.dioport_set.exclude(pk=dio_port.pk).filter(
            ix_position=ix_position).count() == 0

    def validate_unique_dc_position(self, dio_port, dc_position):
        return self.dioport_set.exclude(pk=dio_port.pk).filter(
            datacenter_position=dc_position).count() == 0


class DIOPort(HistoricalTimeStampedModel):
    """DIO port representation."""
    objects = DIOPortQuerySet.as_manager()
    dio = models.ForeignKey('DIO', models.CASCADE)
    ix_position = models.CharField(max_length=255,
                                   blank=True,
                                   validators=[MaxLengthValidator(255)])

    datacenter_position = models.CharField(
        max_length=255, validators=[MinLengthValidator(1), MaxLengthValidator(255)])
    switch_port = models.ForeignKey('Port',
                                    models.SET_NULL,
                                    blank=True,
                                    null=True)  # revisar

    class Meta:
        unique_together = ('dio', 'ix_position', 'datacenter_position',
                           'switch_port',)
        ordering = ('dio',)
        verbose_name = _('DIOPort')
        verbose_name_plural = _('DIOPorts')

    def __str__(self):
        return "[DIO %s: POS %s]" % (self.dio.name, self.datacenter_position,)

    def clean(self):
        self.block_update_fields('dio_id')


class IPv4Address(HistoricalTimeStampedModel, ReservableModel):
    """Global IPv4 address to be used in IX' services."""
    uuid = None
    ix = models.ForeignKey('IX', models.PROTECT, null=False, blank=False)
    address = models.GenericIPAddressField(
        'IPv4', primary_key=True, validators=[validate_ipv4_network])
    reverse_dns = models.CharField(
        max_length=255, blank=True, validators=[validate_url_format])
    in_lg = models.BooleanField()

    class Meta:
        ordering = ('address',)
        verbose_name = _('IPv4Address')
        verbose_name_plural = _('IPv4Addresses')

    def __str__(self):
        lg = 'L' if self.in_lg else ''
        return "[%s%s]" % (self.address, lg,)

    def clean(self):
        self.block_update_pk()

    def get_status(self):
        if(MLPAv4.objects.filter(mlpav4_address=self.address, mlpav4_address__ix=self.ix) or
           Monitorv4.objects.filter(monitor_address=self.address, monitor_address__ix=self.ix)):
            return 'ALLOCATED'
        else:
            return 'FREE'

    def last_group(self):
        return int(self.address.rsplit(".", 1)[-1])


class IPv6Address(HistoricalTimeStampedModel, ReservableModel):
    """Global IPv6 address to be used in IX' services."""
    uuid = None
    ix = models.ForeignKey('IX', models.PROTECT, null=False, blank=False)
    address = models.GenericIPAddressField(
        'IPv6', primary_key=True, validators=[validate_ipv6_network])
    reverse_dns = models.CharField(
        max_length=255, blank=True, validators=[validate_url_format])
    in_lg = models.BooleanField()

    class Meta:
        ordering = ('address',)
        verbose_name = _('IPv6Address')
        verbose_name_plural = _('IPv6Addresses')

    def __str__(self):
        lg = 'L' if self.in_lg else ''
        return "[%s%s]" % (self.address, lg,)

    def clean(self):
        self.block_update_pk()

    def get_status(self):
        if MLPAv6.objects.filter(mlpav6_address=self, mlpav6_address__ix=self.ix):
            return 'ALLOCATED'
        else:
            return 'FREE'

    def last_group(self):
        return int(self.address.rsplit(":", 1)[-1])


class IX(HistoricalTimeStampedModel):
    """Internet Exchange (IX) site representation."""

    TAGS_POLICIES = (('ix_managed', "IX_managed"),
                     ('distributed', "Distributed"),)
    uuid = None
    code = models.CharField(max_length=4, primary_key=True,
                            validators=[MinLengthValidator(2),
                                        MaxLengthValidator(4),
                                        validate_ix_code])
    shortname = models.CharField(max_length=16, unique=True, validators=[
                                 validate_ix_shortname])
    fullname = models.CharField(
        max_length=48, validators=[validate_ix_fullname])
    ipv4_prefix = models.CharField(
        max_length=18, unique=True, validators=[validate_ipv4_network])
    ipv6_prefix = models.CharField(
        max_length=43, unique=True, validators=[validate_ipv6_network])
    management_prefix = models.CharField(
        max_length=18, validators=[validate_ipv4_network])
    create_ips = models.BooleanField(default=True)
    create_tags = models.BooleanField(default=True)
    tags_policy = models.CharField(
        max_length=32, choices=TAGS_POLICIES, default='Bundle-Ether')
    prefix_update = False

    class Meta:
        ordering = ('code',)
        verbose_name = _('IX')
        verbose_name_plural = _('IXs')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._original_ipv4_prefix = self.ipv4_prefix
        self._original_ipv6_prefix = self.ipv6_prefix

    def __str__(self):
        return "[%s]" % (self.code,)

    def get_ipv4_network(self):
        return ipaddress.ip_network(self.ipv4_prefix)

    def get_ipv6_network(self):
        return ipaddress.ip_network(self.ipv6_prefix)

    def validate_mgmt_network(self):
        if isinstance(ipaddress.ip_network(self.management_prefix),
                      ipaddress.IPv4Network):
            if not ipaddress.ip_network(self.management_prefix).is_private:
                raise ValidationError(_("{} is not a private network".
                                        format(self.management_prefix)))
        else:
            raise ValidationError(_("{} is not a IPv4 network".
                                    format(self.management_prefix)))

    def validate_ip_network_intersect(self):
        current_v4 = ipaddress.ip_network(self.ipv4_prefix)
        current_v6 = ipaddress.ip_network(self.ipv6_prefix)
        for ix in IX.objects.all():
            if ix.code == self.code:
                continue
            other_v4 = ipaddress.ip_network(ix.ipv4_prefix)
            other_v6 = ipaddress.ip_network(ix.ipv6_prefix)
            if current_v4.overlaps(other_v4):
                raise ValidationError(_("{} overlaps with {} from IX: {}".
                                        format(current_v4, other_v4, ix)))
            if current_v6.overlaps(other_v6):
                raise ValidationError(_("{} overlaps with {} from IX: {}".
                                        format(current_v6, other_v6, ix)))

    def clean(self):
        self.block_update_pk()
        self.validate_mgmt_network()
        self.validate_ip_network_intersect()

    def create_ipv4(self, old_addresses=[]):
        """
        Create all IPv4Addresses that belong to this IX IPv4 prefix.
        Raises ValueError if one of those IPs already exist and is assigned
        to another IX.

        """
        prefix = self.get_ipv4_network()
        old_prefix = ipaddress.ip_network(self._original_ipv4_prefix)

        expansion = prefix.overlaps(old_prefix) and prefix < old_prefix

        if expansion:
            new_addresses = (ip for ip in prefix.hosts()
                             if ip not in old_prefix.hosts())

            for address in new_addresses:
                ip = IPv4Address(address=address, ix=self, in_lg=False,
                                 last_ticket=self.last_ticket,
                                 modified_by=self.modified_by)
                ip.save()
        else:
            difference = int(prefix.network_address) - \
                         int(old_prefix.network_address)
            for address in old_addresses:
                ip_address = ipaddress.ip_address(address.address)

                address = IPv4Address(
                    address=ip_address + difference,
                    ix=self,
                    reverse_dns=address.reverse_dns,
                    in_lg=address.in_lg,
                    last_ticket=address.last_ticket,
                    modified_by=self.modified_by)
                address.save()

            # If the new prefix is bigger, create the remaining addresses
            remaining = list(prefix.hosts())[len(old_addresses):]
            for address in remaining:
                ip = IPv4Address(address=address, ix=self, in_lg=False,
                                 last_ticket=self.last_ticket,
                                 modified_by=self.modified_by)
                ip.save()

    def map_new_address_ipv4(self, *services):
        """
        Change address of services to match new prefix. If the new prefix
        contains the old one, no alteration is made. Else, the new address of a
        given service is calculated by keeping the same offset from the old
        prefix.

        """
        prefix = self.get_ipv4_network()
        old_prefix = ipaddress.ip_network(self._original_ipv4_prefix)

        expansion = prefix.overlaps(old_prefix) and prefix < old_prefix

        if expansion:
            return
        else:
            for service in services:
                service_address = ipaddress.ip_address(
                    service.get_address().address)
                offset = int(service_address) - int(old_prefix.network_address)
                new_address = prefix.network_address + offset

                service.set_address(
                    IPv4Address.objects.get(address=str(new_address)))
                service.save()

    def update_ips(self):
        """
        Called after an IX has one of its prefixes changed.
        Create new IP objects and change the address of its services
        for the new prefix. They are not changed if the new prefix contains the
        old one (expansion)

        """
        prefix = self.get_ipv4_network()
        old_prefix = ipaddress.ip_network(self._original_ipv4_prefix)

        if prefix != old_prefix:
            #  If it's an expansion, just create new addresses without changing
            # services address
            expansion = prefix.overlaps(old_prefix) and prefix < old_prefix

            if expansion:
                self.create_ipv4()
            else:
                mlpa_v4_services = MLPAv4.objects.filter(
                    mlpav4_address__ix=self)
                monitor_services = Monitorv4.objects.filter(
                    monitor_address__ix=self)

                old_addresses = list(IPv4Address.objects.filter(ix=self))

                self.create_ipv4(old_addresses)
                self.map_new_address_ipv4(*mlpa_v4_services, *monitor_services)

                for old_address in old_addresses:
                    old_address.delete()

        prefix = self.get_ipv6_network()
        old_prefix = ipaddress.ip_network(self._original_ipv6_prefix)

        if prefix != old_prefix:
            mlpa_v6_services = MLPAv6.objects.filter(
                    mlpav6_address__ix=self)

            old_addresses = list(IPv6Address.objects.filter(ix=self))

            self.map_new_address_ipv4(*mlpa_v6_services)

        self.prefix_update = False

    def get_all_customer_channels(self):
        """ Function to return List of CIX"""
        channel_list = []
        for pix in PIX.objects.filter(ix=self):
            channels = pix.get_customer_channels()
            for channel in channels:
                channel_list.append(channel)

        return list(set(channel_list))

    def get_all_cix(self):
        """ Function to return List of CIX"""
        channel_list = self.get_all_customer_channels()

        return [channel for channel in channel_list if channel.cix_type != 0]

    def get_cix_info(self):
        cix_set_info = {}
        i = 0
        for value in self.get_all_cix():
            cix_set_info[str(i)] = {}
            cix_set_info[str(i)]['uuid'] = value.uuid
            cix_set_info[str(i)]['number'] = value.asn.number
            cix_set_info[str(i)]['is_lag'] = value.is_lag
            cix_set_info[str(i)]['is_mclag'] = value.is_mclag
            cix_set_info[str(i)]['pix'] = Port.objects.filter(
                channel_port=value.channel_port).first().switch.pix

            i += 1

        return cix_set_info

    def get_total_available_ports(self):
        total_port = 0

        for pix in PIX.objects.filter(ix=self):
            switch_set = Switch.objects.filter(pix=pix)
            for switch in switch_set:
                total_port += len(
                    Port.objects.filter(switch=switch, status='AVAILABLE'))

        return total_port


class MACAddress(HistoricalTimeStampedModel):
    """MAC address related to a service."""
    uuid = None
    address = models.CharField(primary_key=True, max_length=17, validators=[
                               validate_mac_address])

    class Meta:
        ordering = ('address',)
        verbose_name = _('MACAddress')
        verbose_name_plural = _('MACAddresses')

    def __str__(self):
        return "[%s]" % (self.address,)

    def is_in_any_service(self):
        return self.mlpav4_set.count() > 0 or \
               self.mlpav6_set.count() > 0 or \
               self.bilateralpeer_set.count() > 0 or \
               self.monitorv4_set.count() > 0

    def clean(self):
        self.address = MACAddressConverterToSystemPattern(self.address). \
            mac_address_converter()
        self.block_update_pk()

    def get_service_of_mac(self):
        service_mac = list()
        service_mac.extend(self.mlpav4_set.all())
        service_mac.extend(self.mlpav6_set.all())
        service_mac.extend(self.bilateralpeer_set.all())
        return service_mac[0] if len(service_mac) > 0 else None


class Organization(HistoricalTimeStampedModel):
    """Organization representation."""
    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=255, blank=True,
                            null=False, editable=False,
                            validators=[validate_cnpj])
    url = models.CharField(max_length=255, validators=[validate_url_format])
    address = models.CharField(max_length=255)

    class Meta:
        ordering = ('shortname',)
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __str__(self):
        return "[%s: %s]" % (self.shortname, self.name)

    def clean(self):
        self.block_update_fields('cnpj')
        self.clean_cnpj()

    def clean_cnpj(self):
        self.cnpj = self.cnpj. \
            replace('.', '').replace('/', '').replace('-', '')


class PIX(HistoricalTimeStampedModel):
    """PIX site representation."""
    code = models.CharField(max_length=30,
                            validators=[MinLengthValidator(2),
                                        MaxLengthValidator(30),
                                        validate_pix_code])
    ix = models.ForeignKey('IX', models.PROTECT, null=False)

    class Meta:
        ordering = ('ix', 'code',)
        verbose_name = _('PIX')
        verbose_name_plural = _('PIXs')

    def __str__(self):
        return "[IX %s: PIX %s]" % (self.ix.code, self.code,)

    def clean(self):
        self.block_update_fields('ix_id')

    def get_customer_channels(self):
        ports_in_ix_pix = Port.objects.filter(switch__pix=self)
        channels = CustomerChannel.objects.filter(
            channel_port__in=ports_in_ix_pix.values_list('channel_port',
                                                         flat=True))
        return channels

    def get_asns(self):

        channels = self.get_customer_channels()

        asn_list = []
        asn_list.extend(channels.values_list('asn', flat=True))
        mlpav4 = MLPAv4.objects.filter(customer_channel__in=channels)
        asn_list.extend(list(mlpav4.values_list('asn', flat=True)))

        mlpav6 = MLPAv6.objects.filter(customer_channel__in=channels)
        asn_list.extend(list(mlpav6.values_list('asn', flat=True)))

        bilateralpeer = BilateralPeer.objects.filter(
            customer_channel__in=channels)
        asn_list.extend(list(bilateralpeer.values_list('asn', flat=True)))

        monitorv4 = Monitorv4.objects.filter(customer_channel__in=channels)
        asn_list.extend(list(monitorv4.values_list('asn', flat=True)))

        return list(set(asn_list))

    def get_stats_amount(self):
        channels = self.get_customer_channels()
        asn_amount = list()

        for contact_map in self.ix.contactsmap_set.all():
            asn_amount.append(contact_map.asn.number)

        mlpav4 = MLPAv4.objects.filter(customer_channel__in=channels)

        mlpav6 = MLPAv6.objects.filter(customer_channel__in=channels)

        bilateralpeer = BilateralPeer.objects.filter(
            customer_channel__in=channels)

        monitorv4 = Monitorv4.objects.filter(customer_channel__in=channels)

        stats_infos = {'asn_amount': len(set(asn_amount)),
                       'mlpav4_amount': len(mlpav4),
                       'mlpav6_amount': len(mlpav6),
                       'monitorv4': len(monitorv4),
                       'bilateral_amount': len(bilateralpeer),
                       'cix_amount': len(channels.exclude(cix_type=0))}

        return stats_infos

    def get_switch_infos_by_pix(self):
        pix_switch_set = PIX.objects.get(uuid=self.uuid).switch_set.all()
        switch_set = {}
        i = 0

        for switch in pix_switch_set:
            switch_set[str(i)] = {}
            switch_set[str(i)]['model'] = switch.model.model
            switch_set[str(i)]['management_ip'] = switch.management_ip
            switch_set[str(i)]['uuid'] = switch.uuid
            switch_set[str(i)]['available_ports'] = \
                Port.objects.filter(status='AVAILABLE',
                                    switch=switch).count()

            ports = Port.objects.filter(switch=switch)
            switch_set[str(i)]['percent_available_ports'] = \
                calculate_percent_use_of_switch_ports(
                    ports,
                    switch_set[str(i)]['available_ports'])

            i += 1

        return switch_set

    def has_dio(self):
        return DIO.objects.filter(pix=self).count() > 0


class PhysicalInterface(HistoricalTimeStampedModel):
    """Physical interface instance representation."""
    serial_number = models.CharField(max_length=255, blank=True, null=False)
    connector_type = models.CharField(
        max_length=8, choices=CONNECTOR_TYPES, default='SFP')

    port_type = models.CharField(
        max_length=8, choices=PORT_TYPES, default='UTP')

    class Meta:
        ordering = ('connector_type', 'port_type',)
        verbose_name = _('PhysicalInterface')
        verbose_name_plural = _('PhysicalInterfaces')

    def __str__(self):
        return "[%s: %s: %s]" % (self.serial_number,
                                 self.connector_type,
                                 self.port_type, )

    def validate_serial_number(self):
        if self.port_type == 'UTP':
            if self.serial_number == '':
                raise ValidationError(_('UTP serial number cannot be blank'))

    def validate_connector_type_port_type(self):
        if self.port_type not in PORT_TYPE_CONNECTOR_TYPE[self.connector_type]:
            raise ValidationError(
                _('port_type not compatible with connector_type'))

    def clean(self):
        self.block_update_fields('serial_number')
        self.block_update_fields('connector_type')
        self.block_update_fields('port_type')
        self.validate_serial_number()
        self.validate_connector_type_port_type()

    @staticmethod
    def get_free_physical_interfaces():
        return PhysicalInterface.objects.exclude(
            uuid__in=Port.objects
            .filter(physical_interface__isnull=False)
            .values_list('physical_interface__uuid', flat=True)
        )


class Port(HistoricalTimeStampedModel, ReservableModel):
    """Network switch physical port representation."""

    objects = PortQuerySet.as_manager()
    name = models.CharField(max_length=255)
    capacity = models.IntegerField(choices=CAPACITIES_MAX, default=1000)
    configured_capacity = models.IntegerField(choices=CAPACITIES_CONF, default=1000)

    connector_type = models.CharField(max_length=8,
                                      choices=CONNECTOR_TYPES,
                                      default='SFP')
    STATUSES = (('AVAILABLE', 'Available'),
                ('RESERVED_CUSTOMER', 'Reserved for customer'),
                ('RESERVED_INFRA', 'Reserved for uplinks or dl'),
                ('CUSTOMER', 'Allocated for customer'),
                ('INFRASTRUCTURE', 'Uplink or downlink'),
                ('UNAVAILABLE', 'unavailable'), )
    status = models.CharField(
        max_length=32, choices=STATUSES, default='AVAILABLE')
    physical_interface = models.OneToOneField(
        'PhysicalInterface', models.SET_NULL, blank=True, null=True,
        related_name='port_related')
    switch = models.ForeignKey('Switch', models.CASCADE, blank=True, null=True)
    switch_module = models.ForeignKey('SwitchModule', models.CASCADE, blank=True, null=True)
    route = models.ForeignKey('Route', models.SET_NULL, blank=True, null=True)
    channel_port = models.ForeignKey(
        'ChannelPort', models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ('switch', 'name',)
        unique_together = (('switch', 'name',),)
        verbose_name = _('Port')
        verbose_name_plural = _('Ports')
    #Criar validator Switch e Module NUll
    def validate_connector_type_capacity(self):
        if(self.capacity not in
           PORT_CAPACITY_CONNECTOR_TYPE[self.connector_type]):
            raise ValidationError(
                _('port_capacity not compatible with connector_type'))

    def validate_configured_capacity(self):
        if self.configured_capacity > self.capacity:
            raise ValidationError(_('Configured capacity must be the same or '
                                    'lower than capacity'))

    def validate_connector_type_physical_interface_connector_type(self):
        if self.physical_interface:
            if(self.physical_interface.connector_type not in
               PHYSICAL_INTERFACE_PORT_CONNECTOR_TYPE[self.connector_type]):
                raise ValidationError(
                    _('port_connector_type not compatible with '
                      'physical_interface connector_type'))

    def validate_status_channel_port(self):
        if self.channel_port:
            if self.status == 'AVAILABLE':
                raise ValidationError(
                    _('Change Status if associated a Channel port.'))

            is_customer = CustomerChannel.objects.filter(
                channel_port=self.channel_port)

            if self.status == 'RESERVED_CUSTOMER' and not is_customer:
                raise ValidationError(
                    _('RESERVED_CUSTOMER only allowed if Channel port has a '
                      'CustomerChannel'))
            if self.status == 'CUSTOMER' and not is_customer:
                raise ValidationError(
                    _('CUSTOMER only allowed if Channel port has a '
                      'CustomerChannel'))
            if self.status == 'RESERVED_INFRA' and is_customer:
                if(CustomerChannel.objects.get(channel_port=self.channel_port)\
                        .asn.number != 26162):
                    raise ValidationError(
                        _('RESERVED_INFRA not allowed if Channel port has a '
                          'CustomerChannel'))
            if self.status == 'INFRASTRUCTURE' and is_customer:
                if(CustomerChannel.objects.get(channel_port=self.channel_port)\
                        .asn.number != 26162):
                    raise ValidationError(
                        _('INFRASTRUCTURE not allowed if Channel port has a '
                          'CustomerChannel'))
        else:
            if self.status != 'AVAILABLE':
                raise ValidationError(
                    _('Change Channel port if Status is not "Available".'))

    def getDioPorts(self):
        return self.dioport_set.all()

    def clean(self):
        self.block_update_fields('name')
        self.block_update_fields('capacity')
        self.validate_status_channel_port()
        self.validate_connector_type_capacity()
        self.validate_configured_capacity()
        self.validate_connector_type_physical_interface_connector_type()
        if self.route:
            Route.clean(self.route, self)

    def __str__(self):
        if self.switch:
            return "[%s: %s]" % (self.switch.management_ip, self.name)
        else:
            return "[%s: %s]" % (self.switch_module, self.name)

    @property
    def capacity_translated(self):
        return dict(CAPACITIES_MAX)[self.capacity]


class Route(HistoricalTimeStampedModel):
    """Physical route representation."""

    class Meta:
        verbose_name = _('Route')
        verbose_name_plural = _('Routes')

    def __str__(self):
        return "[%s]" % (self.description)

    def clean(self, *args):
        ix = None
        switches = []
        port_list = [port for port in self.port_set.iterator()]

        if args:
            new_port = args[0]
            if new_port.pk not in [p.pk for p in port_list]:
                port_list.append(args[0])

        for port in port_list:
            if not ix:
                ix = port.switch.pix.ix
            else:
                if port.switch.pix.ix != ix:
                    raise ValidationError(_("Route can't be in different IX."))
            if port.switch not in switches:
                switches.append(port.switch)
                if len(switches) > 2:
                    raise ValidationError(_("Only permitted 2 Switches per "
                                            "Route."))


class Service(HistoricalTimeStampedModel):
    """Service representation."""
    tag = models.ForeignKey('Tag', models.PROTECT, null=True)
    inner = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)],
        blank=True,
        null=True)
    customer_channel = models.ForeignKey('CustomerChannel', models.PROTECT)
    shortname = models.CharField(max_length=255)
    asn = models.ForeignKey('ASN', models.PROTECT)
    mac_addresses = models.ManyToManyField('MACAddress')
    STATUSES = (('ALLOCATED', 'Allocated for customer but not in use'),
                ('INTERNAL', 'Internal servers in production'),
                ('PRODUCTION', 'Customer in production'),
                ('QUARANTINE', 'Customer in test/quarantine'), )
    status = models.CharField(
        max_length=32, choices=STATUSES, default='ALLOCATED')

    class Meta:
        abstract = True
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        # Remember to put this line in derived classes
        # ordering = ('asn', 'tag', 'inner',)
        # unique_together = (('asn', 'tag', 'inner'),)

    def __str__(self):
        return "%s [%s AS%s %s:%s]" % (self.uuid,
                                       self.shortname,
                                       self.asn.number,
                                       self.tag,
                                       self.inner)

    @staticmethod
    def get_objects_all():
        objects_list = []
        objects_list.extend(list(MLPAv4.objects.all()))
        objects_list.extend(list(MLPAv6.objects.all()))
        objects_list.extend(list(Monitorv4.objects.all()))
        objects_list.extend(list(BilateralPeer.objects.all()))
        return objects_list

    def get_service_type(self):
        return self.__class__.__name__

    def get_objects_filter(kwarg, arg):
        objects = list()
        objects.extend(list(MLPAv4.objects.filter(**{kwarg: arg})))
        objects.extend(list(MLPAv6.objects.filter(**{kwarg: arg})))
        objects.extend(list(Monitorv4.objects.filter(**{kwarg: arg})))
        objects.extend(list(BilateralPeer.objects.filter(**{kwarg: arg})))
        return objects

    def validate_asn_ix(self):
        if(Port.objects.filter(
           channel_port=self.customer_channel.channel_port)):
            if not ContactsMap.objects.filter(ix=Port.objects.filter(
                    channel_port=self.customer_channel.channel_port)[0].
                        switch.pix.ix, asn=self.asn):
                raise ValidationError(_("This ASN doesn't belong to the same "
                                        "IX from customer channel."))
        else:
            raise ValidationError(_("Customer Channel associated MUST have in "
                                    "a least one port."))

    def validate_mac(self):
        macs = set()
        macs_mlpav4 = set([mac for mac in MLPAv4.objects.filter(
            asn=self.asn, customer_channel=self.customer_channel).values_list(
                'mac_addresses', flat=True) if mac])
        macs_mlpav6 = set([mac for mac in MLPAv6.objects.filter(
            asn=self.asn, customer_channel=self.customer_channel).values_list(
                'mac_addresses', flat=True) if mac])
        macs_bilateralpeer = set([mac for mac in BilateralPeer.objects.filter(
            asn=self.asn, customer_channel=self.customer_channel).values_list(
                'mac_addresses', flat=True) if mac])
        macs_monitorv4 = set([mac for mac in Monitorv4.objects.filter(
            asn=self.asn, customer_channel=self.customer_channel).values_list(
                'mac_addresses', flat=True) if mac])
        macs = macs.union(
            macs_mlpav4, macs_mlpav6, macs_bilateralpeer, macs_monitorv4)
        if len(macs) > 4:
            raise ValidationError(_('Only 4 MACs by AS by Channel is allowed'))
        if len(self.mac_addresses.all()) >= 3:
            raise ValidationError(_('Only 2 MAC/Service are allowed'))

    def validate_cix_type(self):
        if self.customer_channel.asn != self.asn:
            if self.customer_channel.cix_type == 0:  # individual port
                raise ValidationError(_("Respective Customer Channel is a "
                                        "individual port and doesn't accept "
                                        "participants."))

    def get_ports(self):
        return self.customer_channel.get_ports()

    @property
    def get_master_pix(self):
        return self.customer_channel.get_master_port().switch.pix

    def get_all_pix(self):
        return set(
            [port.switch.pix for port in self.customer_channel.get_ports()])

    def clean(self):
        self.validate_asn_ix()
        self.validate_mac()
        self.validate_cix_type()


class Switch(HistoricalTimeStampedModel):
    """Network switch representation."""
    pix = models.ForeignKey('PIX', models.PROTECT)
    management_ip = models.GenericIPAddressField(
        'Management IP', blank=True, null=True)
    translation = models.BooleanField(default=False)
    model = models.ForeignKey('SwitchModel', models.PROTECT)
    is_pe = models.BooleanField(default=False)
    create_ports = models.BooleanField(default=True)

    class Meta:
        ordering = ('pix', 'management_ip',)
        verbose_name = _('Switch')
        verbose_name_plural = _('Switches')

    def __str__(self):
        return "[%s: %s]" % (self.pix, self.management_ip, )

    def get_channel(channel_port):
        try:
            return channel_port.corechannel
        except Exception:
            try:
                return channel_port.customerchannel
            except Exception:
                try:
                    return channel_port.downlinkchannel
                except Exception:
                    try:
                        return channel_port.translationchannel
                    except Exception:
                        try:
                            return channel_port.uplinkchannel
                        except Exception:
                            return None

    def get_unavailable_ports(self):
        return self.port_set.exclude(status='AVAILABLE')

    def validate_managment_ip(self):
        if not self.management_ip:
            return
        if(ipaddress.ip_address(self.management_ip) not in
           ipaddress.ip_network(self.pix.ix.management_prefix)):
            raise ValidationError(
                _("{} doesn't belong to network management IX: {}"
                  .format(self.management_ip, self.pix.ix.management_prefix)))
        for pix in PIX.objects.filter(ix=self.pix.ix):
            for switch in Switch.objects.filter(pix=pix):
                if switch.uuid == self.uuid:
                    continue
                if switch.management_ip == self.management_ip:
                    raise ValidationError(_("This IP {} already exist"
                                            .format(self.management_ip)))

    def validate_model(self):
        port_ranges = SwitchPortRange.objects.filter(switch_model=self.model)
        if not port_ranges:
            raise ValidationError(_("This model must be associated with "
                                    "at least one SwitchPortRange"))

    def full_clean(self):
        self.block_update_fields('pix_id')
        self.validate_managment_ip()
        self.validate_model()

    def ordered_ports(self, descendent=False):
        port_dict = dict()
        for port in self.port_set.all():
            port_dict[port.name] = port
        return port_sorting(port_dict, descendent)

    def create_additional_ports(self, quantity, last_ticket):
        """Creates aditional port(s) to switch, from the end of SwitchPortRange
        or from last Port name/number. Assuming all port range have same
        capacity, configured capacity and connector_type

        Args:
            quantity (int): quantity of ports to create
            last_ticket (int): ticket number about this requisition
        """
        match = SequenceMatcher(
            None,
            self.model.switchportrange_set.first().name_format,
            self.ordered_ports().popitem()[0]
            ).find_longest_match(
                0,
                len(self.model.switchportrange_set.first().name_format),
                0,
                len(self.ordered_ports().popitem()[0]))
        last_created_port = int(self.ordered_ports().popitem()[0][match.size:])

        if self.model.switchportrange_set.last().end > self.port_set.count():
            last_port_number = self.model.switchportrange_set.last().end + 1
            if last_created_port >= last_port_number:
                last_port_number = last_created_port + 1
        else:
            last_port_number = self.port_set.count() + 1

        for qty in range(quantity):
            Port.objects.create(
                name=self.model.switchportrange_set.first().name_format.format(
                    last_port_number + qty),
                capacity=self.model.switchportrange_set.first().capacity,
                configured_capacity=self.model.switchportrange_set.first(
                    ).capacity,
                connector_type=self.model.switchportrange_set.first(
                    ).connector_type,
                status='AVAILABLE',
                switch=self,
                last_ticket=last_ticket)


class SwitchModel(HistoricalTimeStampedModel):
    """Network switch model representation."""
    model = models.CharField(max_length=255, unique=True)
    vendor = models.CharField(max_length=255, choices=VENDORS)

    class Meta:
        ordering = ('model',)
        verbose_name = _('SwitchModel')
        verbose_name_plural = _('SwitchModels')

    def __str__(self):
        return "[%s]" % (self.model, )

    def validate_model_vendor(self):
        validate_switch_model(self)

    def clean(self):
        self.validate_model_vendor()
        self.block_update_fields('model')


class SwitchPortRange(HistoricalTimeStampedModel):
    """Switch model ports template representation."""
    capacity = models.IntegerField(choices=CAPACITIES_MAX)
    connector_type = models.CharField(max_length=8, choices=CONNECTOR_TYPES)
    name_format = models.CharField(max_length=255,
                                   validators=[validate_name_format])
    begin = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    switch_model = models.ForeignKey('SwitchModel', models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('switch_model',)
        verbose_name = ('SwitchPortRange')
        verbose_name_plural = ('SwitchPortRanges')

    def __str__(self):
        if self.switch_model:
            return "[%s: %s-%s]" % (
                self.switch_model.model, self.begin, self.end, )
        else:
            return "[%s: %s-%s]" % (
                self.switch_model, self.begin, self.end, )

    @staticmethod
    def get_number_of_ports(model):
        """
        Arguments:
            model {SwitchModel} -- SwitchModel instance

        Returns:
            int -- quantity of ports in SwitchPortRange of specified model.
        """

        list_port_ranges = SwitchPortRange.objects.filter(
            switch_model=model)
        number_of_ports = map((lambda range: range.end - range.begin + 1),
                              list_port_ranges)
        return sum(number_of_ports)

    def validate_begin_le_end(self):
        if self.begin > self.end:
            raise ValidationError(_('begin field must be less or equal than '
                                    'end field'))

    def validate_range_ports(self):
        if SwitchPortRange.objects.all():
            query_similars = SwitchPortRange.objects.filter(
                switch_model=self.switch_model,
                name_format=self.name_format).exclude(pk=self.pk)
            if query_similars:
                port_intervals = [range(instance.begin, instance.end + 1)
                                  for instance in query_similars]
                current_range = range(self.begin, self.end + 1)
                for port_interval in port_intervals:
                    for port_number in current_range:
                        if port_number in port_interval:
                            raise ValidationError(
                                _("This interval of range conflits with "
                                  "another existent"))

    def clean(self):
        self.block_update_fields('capacity')
        self.block_update_fields('connector_type')
        self.block_update_fields('name_format')
        self.block_update_fields('begin')
        self.block_update_fields('end')
        self.block_update_fields('switch_model_id')
        self.validate_begin_le_end()
        self.validate_range_ports()


class SwitchModule(HistoricalTimeStampedModel):
    """ Modular port circuit for switches """
    model = models.CharField(max_length=255)
    vendor = models.CharField(max_length=255, choices=VENDORS)
    port_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        default=1)
    capacity = models.IntegerField(choices=CAPACITIES_MAX, default=1000)
    connector_type = models.CharField(
        max_length=8, choices=CONNECTOR_TYPES, default='SFP')
    name_format = models.CharField(
        max_length=255,
        validators=[validate_name_format],
        default='{0}')

    class Meta:
        ordering = ('model',)
        verbose_name = _('SwitchModule')
        verbose_name_plural = _('SwitchModules')

    def __str__(self):
        return "[module-%s-%s ports]" % (self.model,
                                         self.port_quantity)

    def clean(self):
        self.block_update_fields('model')


class Tag(HistoricalTimeStampedModel, ReservableModel):

    objects = IXAPIQuerySet.as_manager()
    tag = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_TAG_NUMBER),
                    MaxValueValidator(MAX_TAG_NUMBER)])
    ix = models.ForeignKey('IX', models.PROTECT)
    tag_domain = models.ForeignKey(
        'ChannelPort', models.PROTECT, null=True, blank=True)

    STATUSES = (('AVAILABLE', 'available'),
                ('ALLOCATED', 'allocated'),
                ('PRODUCTION', 'production'),)
    status = models.CharField(choices=STATUSES,
                              max_length=10,
                              default='AVAILABLE')

    class Meta:
        unique_together = (('tag', 'ix', 'tag_domain'), )
        ordering = ('ix', 'tag', )
        verbose_name = ('Tag')
        verbose_name_plural = ('Tags')

    def __str__(self):
        return "[%s-%s:%s]" % (self.ix, self.tag, self.tag_domain, )

    def update_status(self, new_status):
        if self.status != new_status:
            self.status = new_status
            self.save()
        else:
            raise ValueError(_("Can't update to the same status"))

    def validate_ix_tag_domain(self):
        if self.tag_domain:
            ports = Port.objects.filter(channel_port=self.tag_domain)
            if ports:
                for port in ports:
                    if self.ix != port.switch.pix.ix:
                        raise ValidationError(_('tag_domain.ix and ix must be '
                                                'the same'))

    def validate_tag_status(self):
        mlpav4 = MLPAv4.objects.filter(tag=self)
        mlpav6 = MLPAv6.objects.filter(tag=self)
        monitorv4 = Monitorv4.objects.filter(tag=self)
        bilateralpeer = BilateralPeer.objects.filter(tag=self)

        if mlpav4 or mlpav6 or monitorv4 or bilateralpeer:
            if self.status == 'AVAILABLE':
                raise ValidationError(_('An used Tag can not be AVAILABLE'))

    def get_services_info(self):
        if hasattr(self.mlpav4_set.first(), 'tag'):
            return [self.mlpav4_set.first().asn, ]
        if hasattr(self.mlpav6_set.first(), 'tag'):
            return [self.mlpav6_set.first().asn]
        if hasattr(self.bilateralpeer_set.first(), 'tag'):
            contacts = []
            contacts.append(self.bilateralpeer_set.first().asn)
            contacts.append(self.bilateralpeer_set.last().asn)
            return contacts
        if hasattr(self.monitorv4_set.first(), 'tag'):
            return [self.monitorv4_set.first().asn]
        return None

    def get_services(self):
        services = []
        mlpav4 = [("MLPAv4", mlpav4) for mlpav4 in MLPAv4.objects.filter(
            tag=self)]
        mlpav6 = [("MLPAv6", mlpav6) for mlpav6 in MLPAv6.objects.filter(
            tag=self)]
        bilateralpeer = [("Bilateralpeer", bilateral) for bilateral in
                         BilateralPeer.objects.filter(tag=self)]
        monitorv4 = [("Monitorv4",  monitor) for monitor in
                     Monitorv4.objects.filter(tag=self)]
        services = services + mlpav4 + mlpav6 + bilateralpeer + monitorv4
        return services

    def clean(self):
        self.block_update_fields('tag')
        self.block_update_fields('ix_id')
        self.validate_ix_tag_domain()
        self.validate_tag_status()


class CoreChannel(Channel):
    """Core port channel representation."""

    other_core_channel = models.OneToOneField(
        'CoreChannel', models.PROTECT, null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('CoreChannel')
        verbose_name_plural = _('CoreChannels')


class CustomerChannel(Channel):
    """Customer port channel representation."""

    CIX_TYPES = ((0, 'individual port'),
                 (1, 'CIX type 1'),
                 (2, 'CIX type 2'),
                 (3, 'CIX type 3'), )
    cix_type = models.PositiveIntegerField(choices=CIX_TYPES,
                                           validators=[MinValueValidator(0),
                                                       MaxValueValidator(3)])
    asn = models.ForeignKey('ASN', models.PROTECT)

    class Meta:
        ordering = ('name',)
        verbose_name = _('CustomerChannel')
        verbose_name_plural = _('CustomerChannels')

    def __str__(self):
        lag = 'L' if self.is_lag else ''
        return "%s [%s%s]" % (self.uuid, self.name, lag, )

    def has_qinq(self):
        return self.cix_type == 3

    def get_stats_amount(self):
        asn_amount = [self.asn.number]

        mlpav4 = MLPAv4.objects.filter(customer_channel=self)
        asn_amount.extend(list(mlpav4.values_list('asn', flat=True)))

        mlpav6 = MLPAv6.objects.filter(customer_channel=self)
        asn_amount.extend(list(mlpav6.values_list('asn', flat=True)))

        bilateralpeer = BilateralPeer.objects.filter(
            customer_channel=self)

        asn_amount.extend(
            list(bilateralpeer.values_list('asn', flat=True)))

        monitorv4 = Monitorv4.objects.filter(customer_channel=self)
        asn_amount.extend(list(monitorv4.values_list('asn', flat=True)))

        stats_infos = {'asn_amount': list(set(asn_amount)),
                       'mlpav4_amount': len(mlpav4),
                       'mlpav6_amount': len(mlpav6),
                       'monitorv4': len(monitorv4),
                       'bilateral_amount': len(bilateralpeer)}

        return stats_infos

    def get_switch_infos_by_port(self):
        switch_set = {}
        ports = Port.objects.filter(channel_port=self.channel_port).all()

        switchs = Switch.objects.filter(pk__in=ports.values_list('switch',
                                                                 flat=True))
        available_ports = Port.objects.filter(
            switch__in=switchs.values_list('pk', flat=True),
            status='AVAILABLE')

        i = 0
        for switch in switchs:
            switch_set[str(i)] = {}

            # Here you need str (), because without str () it returns an instance and
            # gives error at the time of converting to a json
            switch_set[str(i)]['model'] = str(switch.model)
            switch_set[str(i)]['management_ip'] = switch.management_ip
            # Here you need str () because without str ()
            # returns UUID ('o uuid')
            switch_set[str(i)]['uuid'] = str(
                switch.uuid)
            switch_set[str(i)]['available_ports'] = len(available_ports)

            i += 1

        return switch_set

    def validate_asn_in_ix(self):
        ix_by_asn = IX.objects.filter(contactsmap__asn=self.asn)
        ix_through_switch = self.channel_port.port_set.first().\
            switch.pix.ix
        if ix_through_switch not in ix_by_asn:
            raise ValidationError(
                _("Asn: {0} is not registered in the IX: {1}".format(
                    self.asn, ix_through_switch)))

    def clean(self):
        super().clean()
        self.validate_asn_in_ix()


class DownlinkChannel(Channel):
    """Downlink port channel representation."""

    class Meta:
        ordering = ('name',)
        verbose_name = _('DownlinkChannel')
        verbose_name_plural = _('DownlinkChannels')


class TranslationChannel(Channel):
    """Translation port channel representation."""
    customer_channel = models.OneToOneField(
        'CustomerChannel', models.PROTECT)

    class Meta:
        ordering = ('name',)
        verbose_name = _('TranslationChannel')
        verbose_name_plural = _('TranslationChannels')


class UplinkChannel(Channel):
    """Uplink port channel representation."""
    downlink_channel = models.OneToOneField('DownlinkChannel', models.PROTECT)

    class Meta:
        ordering = ('name',)
        verbose_name = _('UplinkChannel')
        verbose_name_plural = _('UplinkChannels')


class BilateralPeer(Service):
    """Bilateral peering service."""
    # pe = models.CharField(max_length=15, blank=True)
    objects = IXAPIQuerySet.as_manager()

    class Meta:
        ordering = ('asn', 'tag', 'inner',)
        verbose_name = _('BilateralPeer')
        verbose_name_plural = _('BilateralPeers')
        unique_together = (('asn', 'tag', 'inner'),)

    def clean(self):
        super(BilateralPeer, self).clean()
        for mac in self.mac_addresses.all():
            self.services_by_mac = []
            for bilateral in BilateralPeer.objects.filter(
                    mac_addresses__in=[mac]):
                self.services_by_mac.append(bilateral)
            if len(self.services_by_mac) >= 1:
                for service in self.services_by_mac:
                    if self.tag.ix == service.tag.ix:
                        if service.asn != self.asn:
                            raise ValidationError(
                                _('MAC address must be unique for ASN in a '
                                  'Service'))


class MLPAv4(Service):
    """IPv4 Multilateral Peering Agreement service."""
    mlpav4_address = models.OneToOneField('IPv4Address', models.PROTECT)
    prefix_limit = models.PositiveIntegerField(default=100)
    objects = IXAPIQuerySet.as_manager()

    class Meta:
        ordering = ('asn', 'tag', 'inner',)
        verbose_name = _('MLPAv4')
        verbose_name_plural = _('MLPAsv4')
        unique_together = (('asn', 'tag', 'inner'),)

    def get_related_service(self):
        try:
            pix = self.customer_channel.channel_port.port_set.first().switch.pix
            asn = self.asn
            mlpav4_ip_last_group = self.mlpav4_address.last_group()

            mlpav6_list = MLPAv6.objects.filter(
                customer_channel__channel_port__port__switch__pix=pix,
                asn=asn)

            for mlpav6 in mlpav6_list:
                if(mlpav4_ip_last_group == mlpav6.mlpav6_address.last_group()):
                    return mlpav6
        except Exception:
            return None

    def get_address(self):
        return self.mlpav4_address

    def set_address(self, address):
        self.mlpav4_address = address

    def clean(self):
        if self.mlpav4_address.is_reserved:
            raise ValidationError(RESERVED_IP.format(self.mlpav4_address))
        super(MLPAv4, self).clean()
        for mac in self.mac_addresses.all():
            self.services_by_mac = []
            for mlpav4 in MLPAv4.objects.filter(mac_addresses__in=[mac]):
                self.services_by_mac.append(mlpav4)
            if len(self.services_by_mac) >= 1:
                for service in self.services_by_mac:
                    if self.mlpav4_address.ix == service.mlpav4_address.ix:
                        if self.uuid != service.uuid:
                            raise ValidationError(
                                _('Only a MAC/MLPAv4/IX is allowed'))
                        if service.asn != self.asn:
                            raise ValidationError(
                                _('MAC address must be unique for ASN in a '
                                  'Service'))


class MLPAv6(Service):
    """IPv6 Multilateral Peering Agreement service."""
    mlpav6_address = models.OneToOneField('IPv6Address', models.PROTECT)
    prefix_limit = models.PositiveIntegerField(default=100)
    objects = IXAPIQuerySet.as_manager()

    class Meta:
        ordering = ('asn', 'tag', 'inner',)
        verbose_name = _('MLPAv6')
        verbose_name_plural = _('MLPAsv6')
        unique_together = (('asn', 'tag', 'inner'),)

    def get_related_service(self):
        try:
            pix = self.customer_channel.channel_port.port_set.first().switch.pix
            asn = self.asn
            mlpav6_ip_last_group = self.mlpav6_address.last_group()

            mlpav4_list = MLPAv4.objects.filter(
                customer_channel__channel_port__port__switch__pix=pix,
                asn=asn)

            for mlpav4 in mlpav4_list:
                if(mlpav6_ip_last_group == mlpav4.mlpav4_address.last_group()):
                    return mlpav4
        except Exception:
            return None

    def get_address(self):
        return self.mlpav6_address

    def set_address(self, address):
        self.mlpav6_address = address

    def clean(self):
        super(MLPAv6, self).clean()
        if self.mlpav6_address.is_reserved:
            raise ValidationError(RESERVED_IP.format(self.mlpav6_address))
        for mac in self.mac_addresses.all():
            self.services_by_mac = []
            for mlpav6 in MLPAv6.objects.filter(mac_addresses__in=[mac]):
                self.services_by_mac.append(mlpav6)
            if len(self.services_by_mac) >= 1:
                for service in self.services_by_mac:
                    if self.mlpav6_address.ix == service.mlpav6_address.ix:
                        if self.uuid != service.uuid:
                            raise ValidationError(
                                _('Only a MAC/MLPAv6/IX is allowed'))
                        if service.asn != self.asn:
                            raise ValidationError(
                                _('MAC address must be unique for ASN in a '
                                  'Service'))


class Monitorv4(Service):
    """Channel availability monitor service."""
    monitor_address = models.OneToOneField('IPv4Address', models.PROTECT)
    objects = IXAPIQuerySet.as_manager()

    class Meta:
        ordering = ('asn', 'tag', 'inner',)
        verbose_name = _('Monitorv4')
        verbose_name_plural = _('Monitorsv4')
        unique_together = (('asn', 'tag', 'inner'),)

    def get_address(self):
        return self.monitor_address

    def set_address(self, address):
        self.monitor_address = address

    def clean(self):
        super(Monitorv4, self).clean()
        if self.monitor_address.is_reserved:
            raise ValidationError(RESERVED_IP.format(self.monitor_address))
        for mac in self.mac_addresses.all():
            self.services_by_mac = []
            for monitor in Monitorv4.objects.filter(mac_addresses__in=[mac]):
                self.services_by_mac.append(monitor)
            if len(self.services_by_mac) >= 1:
                for service in self.services_by_mac:
                    if self.monitor_address.ix == service.monitor_address.ix:
                        if self.uuid != service.uuid:
                            raise ValidationError(
                                _('Only a MAC/Monitor/IX is allowed'))
                        if service.asn != self.asn:
                            raise ValidationError(
                                _('MAC address must be unique for ASN in a '
                                  'Service'))


class Phone(HistoricalTimeStampedModel):
    """ Phone representation """
    number = models.CharField(max_length=100,
                              null=False,
                              blank=False)
    CATEGORIES = (('Landline', "Landline"),
                  ('Mobile', "Mobile"),
                  ('Business', "Business"),
                  ('INOC-DBA', "INOC-DBA"),)
    category = models.CharField(
        max_length=10, choices=CATEGORIES, default='Landline')
    contact = models.ForeignKey('Contact', models.PROTECT)

    class Meta:
        ordering = ('contact', 'number',)
        verbose_name = _('Phone')
        verbose_name_plural = _('Phones')

    def __str__(self):
        return "[Contact: %s : Phone %s]" % (self.contact.email, self.number,)

    def clean(self):
        self.block_update_fields('number')
        self.block_update_fields('contact_id')


###############################################################################
###############################################################################
########################## BUSINESS RULES FUNCTIONS ###########################
###############################################################################
###############################################################################


def create_all_ips(instance):
    # Get the first subnetwork /24 in the ipv4_prefix field
    first_sub_network_v4 = list(ipaddress.ip_network(instance.ipv4_prefix).
                                subnets(new_prefix=24))[0]
    ip_v6 = None

    for ip in ipaddress.ip_network(instance.ipv4_prefix).hosts():
        # For each IPv4 in ipv4_prefix create the respective IP.
        IPv4Address.objects.create(
            ix=instance, last_ticket=instance.last_ticket,
            modified_by=instance.modified_by, address=str(ip), in_lg=False)

        # For each IPv4 create a respective IPv6 with the same final visual
        # number. (IPv4 v.w.y.x IPv6 final ::0.x)
        ip_v6 = ipaddress.ip_network(instance.ipv6_prefix)[0] + \
            int(str(ip).split('.')[-1], 16)

        # If IPv4 is in the first block /24 create IPv6
        # with final ::y.x IPv4 v.w.y.x
        if ip not in first_sub_network_v4:
            ip_v6 += 65536*int(str(ip).split('.')[-2], 16)

        IPv6Address.objects.create(
            ix=instance,
            last_ticket=instance.last_ticket,
            modified_by=instance.modified_by,
            address=str(ip_v6),
            in_lg=False)


def create_tag_by_channel_port(channel_port, initial, limit):
    """

    Function to create tags from a given channel_port

    Args:
        channel_port: ChannelPort instance
        initial: Bool -> True = Initial approach, create from tag 0
        False = Starts from the last tag in the database
        limit: Integer -> Quantity of instances to create

    """
    if Port.objects.filter(channel_port=channel_port):
        ix = Port.objects.filter(channel_port=channel_port)[0].switch.pix.ix
    else:
        raise ValidationError(_('For create all Tags, ChannelPort MUST have '
                                'in a least one port.'))

    if initial:
        tag_numbers_to_create_start = MIN_TAG_NUMBER
        tag_numbers_to_create_limit = MIN_TAG_NUMBER + limit

    else:
        last_tag = Tag.objects.filter(tag_domain=channel_port).last()
        tag_numbers_to_create_start = last_tag.tag + 1
        tag_numbers_to_create_limit = tag_numbers_to_create_start + limit

    for n_tag in range(tag_numbers_to_create_start,
                       tag_numbers_to_create_limit):
        if n_tag == 0 or n_tag == 1:
            status = 'ALLOCATED'
        else:
            status = Tag._meta.get_field('status').get_default()
        Tag.objects.create(
            tag=n_tag, last_ticket=channel_port.last_ticket,
            modified_by=channel_port.modified_by, ix=ix,
            tag_domain=channel_port, status=status)


def create_all_tags_by_ix(instance, limit):
    for n_tag in range(0, limit):
        if n_tag == 0 or n_tag == 1:
            status = 'ALLOCATED'
        else:
            status = Tag._meta.get_field('status').get_default()
        Tag.objects.create(
            tag=n_tag, last_ticket=instance.last_ticket,
            modified_by=instance.modified_by, ix=instance, status=status)


def create_all_ports(instance):
    list_port_ranges = SwitchPortRange.objects.filter(
        switch_model=instance.model)
    switch = instance

    for ranges in list_port_ranges:
        if ranges.begin > 0 and ranges.end > 0:
            for i in range(ranges.begin, ranges.end + 1):
                port = Port.objects.create(
                    name=ranges.name_format.format(i),
                    capacity=ranges.capacity,
                    configured_capacity=ranges.capacity,
                    connector_type=ranges.connector_type,
                    status='AVAILABLE',
                    switch=switch,
                    switch_module=None,
                    modified_by=instance.modified_by,
                    last_ticket=instance.last_ticket)
                port.save()


def delete_orphan_organization(instance):
    if len(instance.organization.contactsmap_set.all()) <= 0:
        Organization.objects.get(pk=instance.organization.pk).delete()


def delete_orphan_asn(instance):
    if len(instance.asn.contactsmap_set.all()) < 1:
        ASN.objects.get(pk=instance.asn.pk).delete()


def delete_orphan_contactsmap(instance):

    ix = instance.asn.contactsmap_set.first().ix.pk
    services = []
    services = services + list(MLPAv4.objects.filter(asn=instance.asn))
    services = services + list(MLPAv6.objects.filter(asn=instance.asn))
    services = services + list(BilateralPeer.objects.filter(asn=instance.asn))
    services = services + list(Monitorv4.objects.filter(asn=instance.asn))
    channels = list(CustomerChannel.objects.filter(asn=instance.asn))

    ports = []
    for service in services:
        ports.append(Port.objects.filter(
            channel_port=service.customer_channel.channel_port,
            switch__pix__ix__pk=ix))

    for channel in channels:
        ports.append(Port.objects.filter(
            channel_port=channel.channel_port,
            switch__pix__ix__pk=ix))

    if len(ports) < 1:
        for contact in ContactsMap.objects.filter(asn=instance.asn, ix__pk=ix):
            contact.delete()

# After a object is save, for some models it's necessary
# create others objects, this could be done by using a
# post_save decorator that listen some model.


# This post_save for the IX model, call a method for
# create all ips (v4 and v6) following some rules.
@receiver(post_save, sender=IX)
def create_ips(sender, instance, **kwargs):
    if kwargs['created'] and not kwargs['raw']:
        if instance.create_ips:
            create_all_ips(instance)


# This post_save for the IX model, call a method for
# update ips following some rules.
@receiver(post_save, sender=IX)
def update_ips(sender, instance, update_fields, **kwargs):
    if not kwargs['created'] and not kwargs['raw']:
        if instance and instance.prefix_update:
            instance.update_ips()


# This post_save for the ChannelPort, call a method for
# create all tags possible (0 - 4095).
@receiver(post_save, sender=ChannelPort)
def create_tags_channel_port(sender, instance, **kwargs):
    if instance.create_tags and instance.tags_type == 'Direct-Bundle-Ether' and not kwargs['raw']:
        create_tag_by_channel_port(instance,
                                   True,
                                   MAX_TAG_NUMBER-MIN_TAG_NUMBER+1)


# This post_save for the IX model, call a method for
# create all tags possible (0 - 4095).
@receiver(post_save, sender=IX)
def create_tags_ix(sender, instance, **kwargs):
    if kwargs['created'] and not kwargs['raw']:
        if instance.create_tags and instance.tags_policy == 'ix_managed':
            create_all_tags_by_ix(instance,
                                  MAX_TAG_NUMBER-MIN_TAG_NUMBER+1)


# This post_save for the Switch model, call a method for
# create all ports possible using SwitchModels and
# respectives SwitchPortRanges.
@receiver(post_save, sender=Switch)
def create_ports(sender, instance, **kwargs):
    if kwargs['created'] and not kwargs['raw']:
        if instance.create_ports:
            create_all_ports(instance)


# This post_delete for ContactsMap, calls a method to
# delete his Organization in case that Organization
# hasn't any other ContacsMap
# @receiver(post_delete, sender=ContactsMap)
# def delete_contactsmap_related_models(sender, instance, **kwargs):
#     delete_orphan_organization(instance)
#     delete_orphan_asn(instance)


@receiver(post_delete, sender=CustomerChannel)
def delete_customerchannel_related_models(sender, instance, **kwargs):
    delete_orphan_contactsmap(instance)


@receiver(post_delete, sender=MLPAv4)
def delete_mlpav4_related_models(sender, instance, **kwargs):
    delete_orphan_contactsmap(instance)


@receiver(post_delete, sender=MLPAv6)
def delete_mlpav6_related_models(sender, instance, **kwargs):
    delete_orphan_contactsmap(instance)


@receiver(post_delete, sender=Monitorv4)
def delete_monitor_related_models(sender, instance, **kwargs):
    delete_orphan_contactsmap(instance)


@receiver(post_delete, sender=BilateralPeer)
def delete_bilatealpeer_related_models(sender, instance, **kwargs):
    delete_orphan_contactsmap(instance)


###############################################################################
###############################################################################
############################# UTILITY FUNCTIONS ###############################
###############################################################################
###############################################################################


def get_used_ipv4_by_ix(**kwargs):
    """ gets the used IPv4Address

    Args:
        ix: kwarg -> the owner IX

    Returns:
        Queryset<IPv4Address>: Queryset conataining used v4 addresses

    """
    ix = kwargs.pop('ix')
    used_v4_addresses = IPv4Address.objects.filter(
        Q(address__in=MLPAv4.objects.all().values_list('mlpav4_address',
                                                       flat=True))
        | Q(address__in=Monitorv4.objects.all().values_list('monitor_address',
                                                            flat=True))
        | Q(reserved=True),
        ix=ix,
    ).distinct()
    return used_v4_addresses


def get_used_ipv6_by_ix(**kwargs):
    """ gets the used IPv6Address

    Args:
        ix: kwarg -> the owner IX

    Returns:
        Queryset<IPv6Address>: Queryset conataining used v6 addresses

    """
    ix = kwargs.pop('ix')
    used_v6_addresses = IPv6Address.objects.filter(
        Q(address__in=MLPAv6.objects.all().values_list('mlpav6_address',
                                                       flat=True))
        | Q(reserved=True),
        ix=ix,
    ).distinct()
    return used_v6_addresses


def get_free_ipv4_by_ix(**kwargs):
    """ gets the free IPv4Address

    Args:
        ix: kwarg -> the owner IX

    Returns:
        Queryset<IPv4Address>: Queryset conataining free v4 addresses

    This funciton is dependent of the following functions:
        get_used_ipv4_by_ix

    """
    ix = kwargs.pop('ix')
    used_v4_addresses = get_used_ipv4_by_ix(ix=ix)
    V4_QUERY = IPv4Address.objects.filter(ix=ix).exclude(
        pk__in=used_v4_addresses.values_list('pk', flat=True))
    return V4_QUERY


def get_free_ipv6_by_ix(**kwargs):
    """ gets the free IPv6Address

    Args:
        ix: kwarg -> the owner IX

    Returns:
        Queryset<IPv6Address>: Queryset conataining free v6 addresses

    This funciton is dependent of the following functions:
        get_used_ipv6_by_ix

    """
    ix = kwargs.pop('ix')
    used_v6_addresses = get_used_ipv6_by_ix(ix=ix)
    V6_QUERY = IPv6Address.objects.filter(ix=ix).exclude(
        pk__in=used_v6_addresses.values_list('pk', flat=True))
    return V6_QUERY
