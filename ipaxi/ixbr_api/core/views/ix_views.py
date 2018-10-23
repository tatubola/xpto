from re import search

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.generic import ListView, View
from ..models import (ASN, DIO, IX, PIX, BilateralPeer, CustomerChannel,
                      IPv4Address, IPv6Address, MACAddress, MLPAv4,
                      MLPAv6, Monitorv4, Port, Tag,)
from ..utils.consulta import MAC
from ..use_cases.mac_address_converter_to_system_pattern import (
    MACAddressConverterToSystemPattern
)


class IXDetailView(LoginRequiredMixin, ListView):
    """List the resume of a IX

    Attributes:
        context (dic): Dictionary that return a set of informations
            to be printed.
        self.total_production_tags (int): Total of tag in production
            from a specified IX.
        self.total_available_tags (int): Total of tag in avaialable
            from a specified IX.
        self.pixs (<class 'django.db.models.query.QuerySet'>): Get queryset
            with filtered PIXs from a specified IX.
        self.asn_total (int): Total of asn from a specified IX.
        self.mlpav4_total (int): Total of MLPAv4 from a specified IX.
        self.mlpav6_total (int): Total of MLPAv6 from a specified IX.
        self.bilateral_total (int): Total of bilateral from a specified IX.
        cixs (int): Total of bilateral from a specified IX.
        template_name (str): core/ix_detail.html
    returns:
        A dict context with all informations about a IX. For example:
        {
            'ix' : [sp]
        },
        {
            'pixs':
                <QuerySet [
                    <PIX: [IX sp: PIX Davis]>,
                    <PIX: [IX sp: PIX Hansen]>
                ]>
        }
    """
    template_name = 'core/ix_detail.html'
    model = IX

    def get_queryset(self):
        self.ix = get_object_or_404(IX, code=self.kwargs['code'])
        self.total_production_tags = Tag.objects.filter(
            ix=self.kwargs['code'],
            status='PRODUCTION').count()
        self.total_available_tags = Tag.objects.filter(
            ix=self.kwargs['code'],
            status='AVAILABLE').count()
        self.total_reserved_tags = Tag.objects.filter(
            ix=self.kwargs['code'],
            status='ALLOCATED').count()
        self.pixs = PIX.objects.filter(ix=self.kwargs['code'])
        self.asn_total = 0
        self.mlpav4_total = 0
        self.mlpav6_total = 0
        self.bilateral_total = 0
        for value in self.pixs:
            self.asn_total += value.get_stats_amount()['asn_amount']
            self.mlpav4_total += value.get_stats_amount()['mlpav4_amount']
            self.mlpav6_total += value.get_stats_amount()['mlpav6_amount']
            self.bilateral_total += value.\
                get_stats_amount()['bilateral_amount']
        if self.ix.tags_policy == 'ix_managed':
            self.is_managed = True
        else:
            self.is_managed = False

        return self.ix

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # Add in the ix
        context = {}
        context['ix'] = self.ix
        context['total_production_tags'] = self.total_production_tags
        context['total_available_tags'] = self.total_available_tags
        context['total_reserved_tags'] = self.total_reserved_tags
        context['pixs'] = self.pixs
        context['cixs'] = self.ix.get_cix_info()
        context['asn_total'] = self.asn_total
        context['mlpav4_total'] = self.mlpav4_total
        context['mlpav6_total'] = self.mlpav6_total
        context['bilateral_total'] = self.bilateral_total
        context['total_available_ports'] = self.ix.get_total_available_ports()
        context['is_managed'] = self.is_managed

        return context

    def get_channel(self, pix_uuid):
        pix = PIX.objects.get(uuid=pix_uuid)
        ports_in_ix_pix = Port.objects.filter(switch__pix=pix)
        channel = CustomerChannel.objects.filter(
            channel_port__in=ports_in_ix_pix.values_list('channel_port',
                                                         flat=True))

        return channel


class IXStatsView(LoginRequiredMixin, View):
    """Stats of a IX
    Attributes:
        ix: (<class 'ixbr_api.core.models.IX'>): Get the ix from IX models or
            return a 404.
    returns:
        A dict context with all information about IX. For example:
        {'ix' : [sp]}
    """

    def get(self, request, code, asn):
        ix = get_object_or_404(IX, code=code)

        get_object_or_404(ASN, contactsmap__ix=ix, number=asn)

        context = {'ix': ix}
        return render(request, 'ix/stats.html', context=context)


class IPSearchView(LoginRequiredMixin, View):
    def get(self, request, code):
        ip_number = request.GET.get('ip')
        ix = get_object_or_404(IX, code=code)
        context = {}
        dic = {}
        ip_query = ''
        try:
            ip_query = IPv4Address.objects.get(pk=ip_number, ix=ix)
            mlpav4 = MLPAv4.objects.filter(mlpav4_address=ip_query.address)
            dic['ip'] = []
            dic['ip'].append(ip_query.address)
            if mlpav4.count():
                dic['ip'].append('ALLOCATED')
                dic['ip'].append(ip_query.mlpav4.asn.number)
                dic['ip'].append(ip_query.mlpav4.asn.contactsmap_set.first().
                                 organization.name)
                for pix in mlpav4.first().get_all_pix():
                    if pix.code not in dic['ip']:
                        dic['ip'].append(pix.code)
                for switch in mlpav4.first().customer_channel.get_switches():
                    if switch.management_ip not in dic['ip']:
                        dic['ip'].append(switch)

            else:
                dic['ip'].append('FREE')
                dic['ip'].append(None)
                dic['ip'].append(None)
                dic['ip'].append(None)
                dic['ip'].append(None)

        except IPv4Address.DoesNotExist:
            try:
                ip_query = IPv6Address.objects.get(pk=ip_number, ix=ix)
                mlpav6 = MLPAv6.objects.filter(mlpav6_address=ip_query.address)
                dic['ip'] = []
                dic['ip'].append(ip_query.address)
                if mlpav6.count():
                    dic['ip'].append('ALLOCATED')
                    dic['ip'].append(ip_query.mlpav6.asn.number)
                    dic['ip'].append(ip_query.mlpav6.asn.contactsmap_set.
                                     first().organization.name)

                    for pix in mlpav6.first().get_all_pix():
                        if pix.code not in dic['ip']:
                            dic['ip'].append(pix.code)
                    for switch in (mlpav6.first().customer_channel.
                                   get_switches()):
                        if switch.management_ip not in dic['ip']:
                            dic['ip'].append(switch)
                else:
                    dic['ip'].append('FREE')
                    dic['ip'].append(None)
                    dic['ip'].append(None)
                    dic['ip'].append(None)
                    dic['ip'].append(None)
            except IPv6Address.DoesNotExist:
                pass

        if ip_query:
            context = {
                'ix': ix,
                'ip_dic': dic,
                'ip': ip_query
            }
            return render(request, 'core/ip_search_result.html', context)
        else:
            messages.error(self.request, (str(ip_number) +
                                          " not found in IX " + str(code)),
                           extra_tags='search_not_found')
            return redirect(self.request.META.get('HTTP_REFERER'))


class TagSearchView(LoginRequiredMixin, View):
    """Search a Tag

    Attributes:
        tag (int): tag number
        code :  the code of the tag's ix
    returns:
        If the search was successful, returns to the tag detail with Tag number
    """

    def get(self, request, code):
        tag_number = request.GET.get('tag')
        tag_queryset = Tag.objects.filter(tag=tag_number, ix__pk=code)
        context = {}
        ix = get_object_or_404(IX, code=code)

        if tag_queryset.count():
            context = {'ix': ix,
                       'tag_number': tag_number,
                       'tag_queryset': tag_queryset}

            return render(request, 'core/tag_search_result.html', context)

        else:
            messages.error(self.request, _(str(tag_number) +
                                           " not found in IX " + str(code)),
                           extra_tags='search_not_found')
            return redirect(self.request.META.get('HTTP_REFERER'))


class MacSearchView(LoginRequiredMixin, View):
    """Search for a MAC Address inside an IX or AS

    Attributes:
        mac : mac address
        code :  the code of the mac's ix
    returns:
        If the search was successful, returns to the mac detail with Mac
        Address.
    """

    def get(self, request, code):
        try:
            ix = get_object_or_404(IX, code=code)
            mac_address = request.GET.get('mac')
            mac_converter = MACAddressConverterToSystemPattern(mac_address)
            sanitized_mac = mac_converter.mac_address_converter()
            mac = MACAddress.objects.filter(address=sanitized_mac).first()
            vendor = MAC('macvendors1.db').get_vendor(mac_address)

            if vendor is None:
                messages.warning(
                    request, _("Vendor not found"),
                    extra_tags='search_not_found')
                return redirect(self.request.META.get('HTTP_REFERER'))

            if mac:
                mlpav4_queryset = MLPAv4.objects.filter(
                    mac_addresses=mac, tag__ix=ix).first()
                mlpav6_queryset = MLPAv6.objects.filter(
                    mac_addresses=mac, tag__ix=ix).first()
                monitorv4_queryset = Monitorv4.objects.filter(
                    mac_addresses=mac, tag__ix=ix).first()
                bilateralpeer_queryset = BilateralPeer.objects.filter(
                    mac_addresses=mac, tag__ix=ix)

                context = {'ix': ix,
                           'mac': mac,
                           'services': list(),
                           'bilateral': dict(),
                           'vendor': vendor}

                if mlpav4_queryset:
                    context['services'].append(mlpav4_queryset)
                if mlpav6_queryset:
                    context['services'].append(mlpav6_queryset)
                if monitorv4_queryset:
                    context['services'].append(monitorv4_queryset)
                if bilateralpeer_queryset:
                    context['bilateral']['owner'] = bilateralpeer_queryset.\
                        first().asn.pk
                    context['bilateral']['service_type'] = \
                        bilateralpeer_queryset.first().get_service_type()
                    context['bilateral']['pix'] = bilateralpeer_queryset.\
                        first().get_master_pix.code
                    context['bilateral'][
                        'switch_uuid'] = bilateralpeer_queryset.\
                        first().customer_channel.get_master_port().switch.pk
                    context['bilateral'][
                        'port'] = bilateralpeer_queryset.\
                        first().customer_channel.get_master_port().__str__()
                    context['bilateral']['tags'] = list()
                    for bilateral in bilateralpeer_queryset:
                        context['bilateral']['tags'].append(bilateral.tag.tag)

                if context['services'] or context['bilateral']:
                    return render(
                        request, 'core/mac_search_result.html', context)

            messages.error(self.request, _(
                "{} not found in IX {}".format(
                    mac_address, code)), extra_tags='search_not_found')
            messages.warning(self.request, _(
                "Vendor name: {}".format(vendor)),
                extra_tags='search_not_found')
            return redirect(self.request.META.get('HTTP_REFERER'))

        except Exception:
            messages.error(self.request, _(str(mac_address) +
                                           " is not a valid MAC Address " +
                                           str(code)),
                           extra_tags='search_not_found')
            return redirect(self.request.META.get('HTTP_REFERER'))


class DIOListView(LoginRequiredMixin, ListView):
    """List the DIOs of a PIX specified

    Attributes:
        pix (<class 'ixbr_api.core.models.PIX'>): Get the pix from PIX models
    returns:
        A dict context with informations about the DIOs of a PIX specified.
        For example:
        {
            'pix' : <PIX: [IX sp: PIX Davis]>,
        },
        {
            'dio_list':
                <QuerySet [
                    <DIO: [PIX Davis: DIO example]>,
                ]>
        }
    """

    template_name = 'ix/dio_list.html'
    model = DIO

    def get_queryset(self):
        self.pix = PIX.objects.get(uuid=self.kwargs['pix'])
        return DIO.objects.filter(pix=self.pix)

    def get_context_data(self, **kwargs):
        context = super(DIOListView, self).get_context_data(**kwargs)
        context['pix'] = self.pix

        return context


class DIOView(LoginRequiredMixin, View):

    def get(self, request, dio):
        template_name = 'ix/dio_detail.html'
        dio_object = DIO.objects.get(pk=dio)
        context = {'dio': dio_object}
        return render(request, template_name, context)
