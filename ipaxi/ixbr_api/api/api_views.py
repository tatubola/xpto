from django.db.models import Q
from rest_framework import mixins, viewsets

from ..core.models import (ASN, DIO, IX, PIX, Bilateral, BilateralPeer,
                           ChannelPort, Contact, ContactsMap, CoreChannel,
                           CustomerChannel, DIOPort, DownlinkChannel,
                           IPv4Address, IPv6Address, MACAddress, MLPAv4, MLPAv6,
                           Monitorv4, Organization, Phone, PhysicalInterface,
                           Port, Route, Switch, SwitchModel, SwitchPortRange,
                           Tag, TranslationChannel, UplinkChannel,)
from .serializers import (ASNSerializer, BilateralPeerSerializer,
                          BilateralSerializer, ChannelPortSerializer,
                          ContactSerializer, ContactsMapSerializer,
                          CoreChannelSerializer,
                          CustomerChannelSerializer, DIOPortSerializer,
                          DIOSerializer, DownlinkChannelSerializer,
                          IPv4AddressSerializer, IPv6AddressSerializer,
                          IXSerializer, MACAddressSerializer,
                          MLPAv4Serializer, MLPAv6Serializer,
                          Monitorv4Serializer, OrganizationSerializer,
                          PhoneSerializer, PhysicalInterfaceSerializer,
                          PIXSerializer, PortSerializer,
                          RouteSerializer, SwitchModelSerializer,
                          SwitchPortRangeSerializer, SwitchSerializer,
                          TagSerializer, TranslationChannelSerializer,
                          UplinkChannelSerializer,)


class IXViewSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    queryset = IX.objects.all()
    serializer_class = IXSerializer
    lookup_field = 'code'
    lookup_value_regex = '[a-z]{2,4}'


class ContactViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class BilateralViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):

    serializer_class = BilateralSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')

    def get_queryset(self):
        search = self.request.GET.get('search')

        ix_code = self.kwargs['code']
        asn_number = self.kwargs['asn']

        qs = Bilateral.objects.all()

        if ix_code:
            qs = qs.filter(Q(peer_a__tag__ix__code=ix_code) |
                           Q(peer_b__tag__ix__code=ix_code))

        if asn_number:
            qs = qs.filter(Q(peer_a__asn__number=asn_number) |
                           Q(peer_b__asn__number=asn_number))

        if search:
            qs = qs.filter(
                Q(peer_a__asn__number__icontains=search) |
                Q(peer_b__asn__number__icontains=search) |
                Q(peer_a__pk__in=MACAddress.objects.filter(
                        address__icontains=search)
                    .values_list('bilateralpeer', flat=True)) |
                Q(peer_b__pk__in=MACAddress.objects.filter(
                        address__icontains=search)
                    .values_list('bilateralpeer', flat=True)) |
                Q(peer_a__tag__tag__icontains=search) |
                Q(peer_b__tag__tag__icontains=search))
        return qs


class BilateralPeerViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = BilateralPeer.objects.all()
    serializer_class = BilateralPeerSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class ASNViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = ASN.objects.all()
    serializer_class = ASNSerializer
    lookup_field = 'number'
    lookup_value_regex = '[1-9][0-9]*'


class ChannelPortViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = ChannelPort.objects.all()
    serializer_class = ChannelPortSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class ContactsMapViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = ContactsMap.objects.all()
    serializer_class = ContactsMapSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class DIOViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = DIO.objects.all()
    serializer_class = DIOSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class DIOPortViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = DIOPort.objects.all()
    serializer_class = DIOPortSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class IPv4AddressViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = IPv4Address.objects.all()
    serializer_class = IPv4AddressSerializer
    lookup_field = 'address'
    lookup_value_regex = ('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                          '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')


class IPv6AddressViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = IPv6Address.objects.all()
    serializer_class = IPv6AddressSerializer
    lookup_field = 'address'
    lookup_value_regex = \
        ('((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|'
         '(([0-9A-Fa-f]{1,4}:){1,7}:)|'
         '(([0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4})|'
         '(([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2})|'
         '(([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3})|'
         '(([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4})|'
         '(([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5})|'
         '([0-9A-Fa-f]{1,4}:(:[0-9A-Fa-f]{1,4}){1,6})|'
         '(:(:[0-9A-Fa-f]{1,4}){1,7}))')


class MACAddressViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = MACAddress.objects.all()
    serializer_class = MACAddressSerializer
    lookup_field = 'address'
    lookup_value_regex = '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'


class OrganizationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class PIXViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = PIX.objects.all()
    serializer_class = PIXSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class PhoneViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Phone.objects.all()
    serializer_class = PhoneSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class PhysicalInterfaceViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    queryset = PhysicalInterface.objects.all()
    serializer_class = PhysicalInterfaceSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class PortViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Port.objects.all()
    serializer_class = PortSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class RouteViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class SwitchViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = Switch.objects.all()
    serializer_class = SwitchSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class SwitchModelViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = SwitchModel.objects.all()
    serializer_class = SwitchModelSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class SwitchPortRangeViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = SwitchPortRange.objects.all()
    serializer_class = SwitchPortRangeSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class CoreChannelViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = CoreChannel.objects.all()
    serializer_class = CoreChannelSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class CustomerChannelViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = CustomerChannel.objects.all()
    serializer_class = CustomerChannelSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class DownlinkChannelViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = DownlinkChannel.objects.all()
    serializer_class = DownlinkChannelSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class TranslationChannelViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = TranslationChannel.objects.all()
    serializer_class = TranslationChannelSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class UplinkChannelViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = UplinkChannel.objects.all()
    serializer_class = UplinkChannelSerializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class MLPAv4ViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = MLPAv4.objects.all()
    serializer_class = MLPAv4Serializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class MLPAv6ViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = MLPAv6.objects.all()
    serializer_class = MLPAv6Serializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class Monitorv4ViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    queryset = Monitorv4.objects.all()
    serializer_class = Monitorv4Serializer
    lookup_field = 'uuid'
    lookup_value_regex = ('[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-'
                          '[89ab][0-9a-f]{3}-[0-9a-f]{12}')
