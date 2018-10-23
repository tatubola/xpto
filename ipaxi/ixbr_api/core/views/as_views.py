from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import View

from ..models import (ASN, IX, PIX, BilateralPeer, ContactsMap,
                      CustomerChannel, MLPAv4, MLPAv6, Port,)
from ..utils import external_api_urls
from ..utils.whoisutils import get_parsed_whois
from ..validators import validate_as_number

NOT_FOUND = 'ASN not found'


class ASSearchView(LoginRequiredMixin, View):
    """Search a ASN

    Attributes:
        asn (int): ASN desired passed by parameter
        as_object (<class 'ixbr_api.core.models.ASN'>): Get the asn from ASN
        models or ask to add the AS.
    returns:
        If the search was successful, returns to the as detail with ASN number,
        else ask to add the AS.
    """

    def get(self, request, **kwargs):
        asn = request.GET.get('asn')
        prev_path = request.GET.get('prev_path')
        try:
            validate_as_number(int(asn))
            return redirect('core:as_detail', asn=asn)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(prev_path)
        except Exception:
            messages.error(self.request, 'ASNs are only compound by numbers.')
            return redirect(prev_path)


class ASDetailView(LoginRequiredMixin, View):
    """Detail of a ASN

    Attributes:
        context (dic): Dictionary that return a set of informations
        to be printed.
        as_object (<class 'ixbr_api.core.models.ASN'>): Get the asn from ASN
        models or return a 404.
        ix_list (<class 'django.db.models.query.QuerySet'>): Get queryset with
        filtered IXs from a specified ASN.
    returns:
        A dict context with all the IXs from ASN number and all informations
        about ASN specified. For example:
        {'object' : [AS62000: [wolfe-morrison: Wolfe-Morrison]]},
        {'ix_list', <QuerySet [<IX: [sp]>]>}

    """

    def get(self, request, asn):
        try:
            as_object = ASN.objects.get(number=asn)
        except Exception:
            as_object = None

        ix_list = IX.objects.filter(contactsmap__asn__number=asn) \
            .order_by('fullname')

        return render(
            request,
            'as/as_detail.html',
            context={'as_object': as_object, 'ix_list': ix_list, 'asn': asn}
        )


class ASAddView(LoginRequiredMixin, View):

    def get(self, request, asn):
        as_to_add = asn

        try:
            get_parsed_whois(int(asn))
        except ValidationError:
            return render(
                request,
                "../templates/as_does_not_exist.html",
                {"ASN": asn}
            )

        return render(
            request,
            'as/as_add.html',
            context={'asn': as_to_add, }
        )


class ASWhoisView(LoginRequiredMixin, View):

    def get(self, request, asn):
        asn = int(asn)
        try:
            info = get_parsed_whois(asn)
        except ValidationError:
            return render(
                request,
                "../templates/as_does_not_exist.html",
                {"ASN": asn}
            )

        context = {'info': info}

        return render(request, 'as/whois.html', context)


class ASIXDetailView(LoginRequiredMixin, View):
    """Detail of a ASN from a IX

    Attributes:
        context (dic): Dictionary that return a set of informations
        to be printed.
        ports_in_ix (<class 'django.db.models.query.QuerySet'>): Get the ports
        of the switches in the given ix.
        customer_channels (<class 'django.db.models.query.QuerySet'>): Get the
        customer channels of the given ix based on the ports.
        customer_channels (<class 'django.db.models.query.QuerySet'>): Filter
        to get the customer channels that have some service vinculated to
        the given asn.
        channel_services (list): Services from a PIX.
        ix (<class 'django.db.models.query.QuerySet'>): Get the IX of the
        in the given ix.
        current_asn (<class 'django.db.models.query.QuerySet'>): Get the ASN
        of the in the given ASN.
        asn_stats (dict): All services stats about this asn.
        asn_pix_channels (dic): DIctionary that contains a set of informations
        of PIXs from a IX specified.
        contacts_map_list (<class 'django.db.models.query.QuerySet'>): Get the
        contacts of a IX specified and a ASN specified.
    returns:
        A dict context with all the IXs from ASN number and all informations
        about ASN specified. For example:
        {'asn' : [AS62000: [wolfe-morrison: Wolfe-Morrison]] }, {'ix', [sp]},
        {'channel_services' : {'Mcbride': {<CustomerChannel: 89504f27-3cd2-4d90-bd9d-5c1376edd798 [AS62000 15]>:
        [[<MLPAv4: a9ce8743-d37a-4143-873d-d113a1d2f778 [as62000-mlpav4 AS62000 [[sp]-4072:
        [sw226-dl]]:988]>], <QuerySet []>, <QuerySet []>]}}}
        {'asn_pix_channels' : {<PIX: [IX sp: PIX Mcbride]>: <QuerySet [<CustomerChannel: 89504f27-3cd2-4d90-bd9d-5c1376edd798 [AS62000 15]>]>}}
        {'mlpav4_total': 3},
        {'mlpav6_total':2},
        {'bilateral_total': 1},
        {'organization_contacts' : [AS[AS62000: [wolfe-morrison: Wolfe-Morrison]]: [sp]: [cgomez@bennett.biz: Laura Bell]]}

    """

    def get(self, request, code, asn):

        # Get the ports of the switches in the given ix
        ports_in_ix = Port.objects.filter(switch__pix__ix__pk=code)

        # Get the customer channels of the given ix based on the ports
        customer_channels = CustomerChannel.objects.filter(
            channel_port__in=ports_in_ix.values_list(
                'channel_port', flat=True))
        # Filter to get the customer channels that have some service vinculated
        # to the given asn

        customer_channels = customer_channels.filter(
            Q(mlpav4__asn__pk=asn) |
            Q(mlpav6__asn__pk=asn) |
            Q(bilateralpeer__asn__pk=asn))

        channel_services = {}

        for channel in customer_channels:
            if(channel.get_ports()[0].switch.pix.code not in
                    channel_services.keys()):
                channel_id = channel.get_ports()[0].switch.pix.code
                channel_services[channel_id] = {}

            channel_services[channel_id][channel] = []

            mlpav4 = list(MLPAv4.objects.filter(asn__pk=asn,
                                                customer_channel=channel))
            channel_services[channel_id][channel].append(mlpav4)

            mlpav6 = (MLPAv6.objects.filter(asn__pk=asn,
                                            customer_channel=channel))
            channel_services[channel_id][channel].append(mlpav6)

            bilateral = (BilateralPeer.objects.filter(
                asn__pk=asn, customer_channel=channel))
            channel_services[channel_id][channel].append(bilateral)

        ix = IX.objects.get(pk=code)
        current_asn = ASN.objects.get(pk=asn)
        asn_stats = current_asn.get_stats_amount(ix=ix)

        asn_pix_channels = {}
        for pix in PIX.objects.filter(ix__pk=code):

            ports_in_ix_pix = Port.objects.filter(switch__pix=pix)
            asn_customer_channels = CustomerChannel.objects.filter(
                asn__pk=asn,
                channel_port__in=ports_in_ix_pix.values_list('channel_port',
                                                             flat=True))
            if len(asn_customer_channels) > 0:
                asn_pix_channels[pix] = asn_customer_channels
        contacts_map_list = ContactsMap.objects.get(ix__pk=code, asn__pk=asn)
        url_ticket_meuix = external_api_urls.get_ticker_meuix_url()
        context = {'asn': current_asn,
                   'ix': ix,
                   'channel_services': channel_services,
                   'mlpav4_total': asn_stats['mlpav4_amount'],
                   'mlpav6_total': asn_stats['mlpav6_amount'],
                   'bilateral_total': asn_stats['bilateral_amount'],
                   'asn_pix_channels': asn_pix_channels,
                   'organization_contacts': contacts_map_list,
                   'url_ticket_meuix': url_ticket_meuix}
        return render(request, 'as/ix_as_detail.html', context)
