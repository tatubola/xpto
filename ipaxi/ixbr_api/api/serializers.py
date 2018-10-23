from rest_framework import serializers

from ..core.models import (ASN, DIO, IX, PIX, Bilateral, BilateralPeer,
                           ChannelPort, Contact, ContactsMap, CoreChannel,
                           CustomerChannel, DIOPort, DownlinkChannel,
                           IPv4Address, IPv6Address, MACAddress, MLPAv4, MLPAv6,
                           Monitorv4, Organization, Phone, PhysicalInterface,
                           Port, Route, Switch, SwitchModel, SwitchPortRange,
                           Tag, TranslationChannel, UplinkChannel,)


class IXSerializer(serializers.ModelSerializer):
    class Meta:
        model = IX
        fields = ('created', 'modified', 'code', 'shortname',
                  'fullname', 'ipv4_prefix', 'ipv6_prefix',
                  'management_prefix', 'description', 'tags_policy')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('created', 'modified', 'last_ticket',
                  'email', 'name', 'description')


class TagSerializer(serializers.ModelSerializer):
    ix_fullname = serializers.CharField(source='ix.fullname')

    class Meta:
        model = Tag
        fields = ('created', 'modified', 'last_ticket', 'uuid',
                  'tag', 'ix', 'ix_fullname', 'tag_domain', 'description')


class BilateralPeerSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = BilateralPeer
        fields = ('created', 'modified', 'last_ticket',
                  'uuid', 'tag', 'inner', 'customer_channel',
                  'shortname', 'asn', 'mac_addresses', 'description')


class BilateralSerializer(serializers.ModelSerializer):
    peer_a = BilateralPeerSerializer()
    peer_b = BilateralPeerSerializer()

    class Meta:
        model = Bilateral
        fields = ('uuid', 'created', 'modified', 'last_ticket',
                  'label', 'bilateral_type', 'peer_a', 'peer_b', 'description')


class ChannelPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelPort
        fields = ('created', 'modified', 'last_ticket',
                  'description', 'tags_type')


class CustomerChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerChannel
        fields = ('created', 'modified', 'last_ticket',
                  'name', 'is_lag', 'is_mclag', 'channel_port', 'cix_type',
                  'asn', 'description')


class CoreChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreChannel
        fields = ('created', 'modified', 'last_ticket',
                  'name', 'is_lag', 'is_mclag', 'channel_port',
                  'other_core_channel', 'description')


class DownlinkChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownlinkChannel
        fields = ('created', 'modified', 'last_ticket', 'description',
                  'name', 'is_lag', 'is_mclag', 'channel_port')


class UplinkChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UplinkChannel
        fields = ('created', 'modified', 'last_ticket',
                  'name', 'is_lag', 'is_mclag', 'channel_port',
                  'downlink_channel', 'description')


class TranslationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationChannel
        fields = ('created', 'modified', 'last_ticket', 'description',
                  'name', 'is_lag', 'is_mclag', 'customer_channel')


class ASNSerializer(serializers.ModelSerializer):
    class Meta:
        model = ASN
        fields = ('created', 'modified', 'last_ticket',
                  'number', 'description')


class ContactsMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsMap
        fields = ('created', 'modified', 'last_ticket', 'description',
                  'uuid', 'ix', 'asn', 'organization', 'noc_contact',
                  'adm_contact', 'peer_contact', 'com_contact', 'peering_url')


class DIOSerializer(serializers.ModelSerializer):
    class Meta:
        model = DIO
        fields = ('created', 'modified', 'last_ticket',
                  'uuid', 'pix', 'name', 'description')


class DIOPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = DIOPort
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'dio',
                  'ix_position', 'datacenter_position', 'switch_port',
                  'description')


class IPv4AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPv4Address
        fields = ('created', 'modified', 'last_ticket', 'description',
                  'ix', 'address', 'reverse_dns', 'in_lg')


class IPv6AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPv6Address
        fields = ('created', 'modified', 'last_ticket', 'description',
                  'ix', 'address', 'reverse_dns', 'in_lg')


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'description',
                  'name', 'shortname', 'cnpj', 'url', 'address')


class MACAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MACAddress
        fields = ('created', 'modified', 'last_ticket', 'address',
                  'description')


class PIXSerializer(serializers.ModelSerializer):
    class Meta:
        model = PIX
        fields = ('created', 'modified', 'last_ticket',
                  'code', 'ix', 'description')


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('created', 'modified', 'last_ticket', 'uuid',
                  'number', 'category', 'contact', 'description')


class PhysicalInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalInterface
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'description',
                  'serial_number', 'connector_type', 'port_type')


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'name',
                  'description', 'capacity', 'connector_type', 'status',
                  'physical_interface', 'switch', 'route', 'channel_port')


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'description')


class SwitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Switch
        fields = ('created', 'modified', 'last_ticket', 'description',
                  'is_pe', 'uuid', 'pix', 'management_ip', 'model')


class SwitchModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwitchModel
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'model',
                  'translation', 'description')


class SwitchPortRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwitchPortRange
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'capacity',
                  'connector_type', 'name_format', 'begin', 'end',
                  'switch_model', 'description')


class MLPAv4Serializer(serializers.ModelSerializer):
    class Meta:
        model = MLPAv4
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'tag', 'inner',
                  'customer_channel', 'asn', 'mac_addresses', 'mlpav4_address',
                  'prefix_limit', 'description')


class MLPAv6Serializer(serializers.ModelSerializer):
    class Meta:
        model = MLPAv6
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'tag', 'inner',
                  'customer_channel', 'asn', 'mac_addresses', 'mlpav6_address',
                  'prefix_limit', 'description')


class Monitorv4Serializer(serializers.ModelSerializer):
    class Meta:
        model = Monitorv4
        fields = ('created', 'modified', 'last_ticket', 'uuid', 'tag', 'inner',
                  'description', 'customer_channel', 'asn', 'mac_addresses',
                  'monitor_address')
