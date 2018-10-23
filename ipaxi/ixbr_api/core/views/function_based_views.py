"""Collections of Function Based Views (FBV)"""

import json

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from requests import get

from ..models import (ASN, IX, PIX, BilateralPeer, ContactsMap,
                      CustomerChannel, IPv4Address, IPv6Address, MLPAv4,
                      MLPAv6, Monitorv4, Port, Switch, Tag)
from ..use_cases.bilateral_use_case import define_bilateral_case
from ..use_cases.get_free_ips_by_ix import get_free_ips_by_ix
from ..use_cases.service_use_case import delete_service_use_case
from ..use_cases.switch_module_use_cases import delete_switch_module_use_case
from ..use_cases.tags_use_cases import (check_inner_tag_availability,
                                        get_available_inner_tag,
                                        get_tag_without_all_service,
                                        get_tag_without_bilateral)
from ..use_cases.mac_address_converter_to_system_pattern import (
    MACAddressConverterToSystemPattern,)
from ..use_cases.search_use_cases import(
    search_customer_channel_by_mac_address)
from ..utils import external_api_urls, port_utils
from ..utils.constants import SWITCH_MODEL_CHANNEL_PREFIX


"""****************************************
************** IP_LIST AJAX ***************
****************************************"""


def get_match_ips_by_asn_search__ip_views(request, **kwargs):
    """Find IPv4 and, or, IPv6 that match with ASN searched by user.

    Args:
        request (WSGIRequest): GET
            "/core/sp/get-match-ips-by-asn-search/?asn='asn'">
        **kwargs: A dictionaty with the parameters of this ix.
            Example:
                kwargs['code'] = 'sp'

    Attributes:
        asn (int): The number of AS searched, gotten via AJAX GET request.
        data (dict): Dictionary that return a set of ips found with this ASN.
        ml4s (<class 'ixbr_api.core.models.IXAPIQuerySet'>): IPv4 which match
            with this ASN.
        ml6s (<class 'ixbr_api.core.models.IXAPIQuerySet'>): IPv6 which match
            with this ASN.

    Returns:
        A JsonResponse data set with IPv4 and, or, IPv6 which match with
        ASN searched for.

        For example:

        {
            'ipv4': ['10.0.3.253'],
            'ipv6': ['2001:12f0::3:253']
        }
    """
    asn = int(request.GET['asn'])
    try:
        ml4s = MLPAv4.objects.filter(asn=asn)
    except ASN.DoesNotExist:
        pass
    try:
        ml6s = MLPAv6.objects.filter(asn=asn)
    except ASN.DoesNotExist:
        pass

    data = {
        'ipv4': list(value.mlpav4_address.address for value in ml4s),
        'ipv6': list(value.mlpav6_address.address for value in ml6s)
    }

    return JsonResponse(data)


def get_ip_informations_by_click__ip_views(request, **kwargs):
    """Display informations about IP clicked.

    Args:
        request (WSGIRequest): GET
            "/core/sp/get-ip-informations-by-click/?ipv4='ipv4'
                &ipv6='ipv6'&ip_opened='ip_opened'">
        **kwargs: A dictionaty with the parameters of this ix.
            Example:
                kwargs['code'] = 'sp'

    Attributes:
        asn_ipv4 (str): ASN owner of IPv4, if exist.
        asn_ipv6 (str): ASN owner of IPv6, if exist.
        ip_opened (int): The number of position opened by click,
            gotten via AJAX GET request.
        ipv4 (str): The number of IPv4 clicked, gotten via AJAX GET request.
        ipv4_info (<class 'ixbr_api.core.models.MLPAv4'>): IPv4 model
            informations.
        ipv4_name (str): Name of AS IPv4 owner.
        ipv6 (str): The number of IPv6 clicked, gotten via AJAX GET request.
        ipv6_info (<class 'ixbr_api.core.models.MLPAv6'>): IPv6 model
            informations.
        ipv6_name (str): Name of AS IPv6 owner.

    Returns:
        A data set with distinct information about IPv4 and IPv6.

        For example:

        {
            'asn_ipv4': 61860,
            'ipv4_name': 'Murillo-Weeks',
            'asn_ipv6': 28630,
            'ipv6_name': 'Velazquez Group'
            'ip_opened': 1011,
        }
    """
    ipv4 = request.GET['ipv4']
    ipv6 = request.GET['ipv6']
    ip_opened = int(request.GET['ip_opened'])
    asn_ipv4 = ''
    asn_ipv6 = ''
    ipv4_name = ''
    ipv6_name = ''

    try:
        ipv4 = IPv4Address.objects.get(address=ipv4)
        try:
            ipv4_info = MLPAv4.objects.get(mlpav4_address=ipv4.address)
            ipv4_name = ipv4_info.asn.contactsmap_set.first().organization.name
            asn_ipv4 = ipv4_info.asn.number
        except MLPAv4.DoesNotExist:
            pass
    except IPv4Address.DoesNotExist:
        pass
    try:
        ipv6 = IPv6Address.objects.get(address=ipv6)
        try:
            ipv6_info = MLPAv6.objects.get(mlpav6_address=ipv6.address)
            ipv6_name = ipv6_info.asn.contactsmap_set.first().organization.name
            asn_ipv6 = ipv6_info.asn.number
        except MLPAv6.DoesNotExist:
            pass
    except IPv6Address.DoesNotExist:
        pass

    data = {
        'ipv4_name': ipv4_name,
        'asn_ipv4': asn_ipv4,
        'ipv6_name': ipv6_name,
        'asn_ipv6': asn_ipv6,
        'ip_opened': ip_opened
    }

    return JsonResponse(data)


"""****************************************
************** TAG_LIST AJAX **************
****************************************"""


def get_match_tags_by_asn_search__tag_views(request, **kwargs):
    """Find Tags that match with ASN searched by user.

    Args:
        request (WSGIRequest): GET
            "/core/sp/get-match-tags-by-asn-search/?asn='asn'">
        **kwargs: A dictionaty with the parameters of this ix.
            Example:
                kwargs['code'] = 'sp'

    Attributes:
        asn (str): The number of AS searched, gotten via AJAX GET request.
        bilateralpeer (<class 'ixbr_api.core.models.IXAPIQuerySet'>): Tags
            that match with this ASN in BilateralPeer Service, if exist.
        data (dict): Dictionary that return a set of tags and organizations
            found with this ASN.
        ix_code (str): IX code of the bundle where this tag is localized,
            gotten via AJAX GET request.
        mlpav4 (<class 'ixbr_api.core.models.IXAPIQuerySet'>): Tags
            that match with this ASN in MLPAv4 Service, if exist.
        mlpav6 (<class 'ixbr_api.core.models.IXAPIQuerySet'>):Tags
            that match with this ASN in MLPAv6 Service, if exist.
        monitorv4 (<class 'ixbr_api.core.models.IXAPIQuerySet'>):Tags
            that match with this ASN in Monitorv4 Service, if exist.
        service (dict): a set of all services tried (bilateralpeer, MLPAv4,
            MLPAv6, monitorv4)

    Returns:
        A JsonResponse data set dictionary with Organization name and
        Tags matched.

        For Example:

        {
        'organization': 'Chaney-Medina',
        'tag': [4092, 4091]
        }
    """
    ix_code = kwargs['code']
    asn = int(request.GET['asn'])
    data = {}
    try:
        service = []
        asn = ASN.objects.get(pk=asn)
        try:
            mlpav4 = Tag.objects.filter(Q(uuid__in=MLPAv4.objects.filter(
                asn_id=asn.number).values_list('tag', flat=True)))

            for value in mlpav4:
                service.append(value)

        except MLPAv4.DoesNotExist:
            pass

        try:
            mlpav6 = Tag.objects.filter(Q(uuid__in=MLPAv6.objects.filter(
                asn_id=asn.number).values_list('tag', flat=True)))

            for value in mlpav6:
                service.append(value)

        except MLPAv6.DoesNotExist:
            pass

        try:
            monitorv4 = Tag.objects.filter(Q(uuid__in=Monitorv4.objects.filter(
                asn_id=asn.number).values_list('tag', flat=True)))

            for value in monitorv4:
                service.append(value)

        except Monitorv4.DoesNotExist:
            pass

        try:
            bilateralpeer = Tag.objects.filter(
                Q(
                    uuid__in=BilateralPeer.objects.filter(
                        asn_id=asn.number).values_list('tag', flat=True)))
            for value in bilateralpeer:
                service.append(value)

        except BilateralPeer.DoesNotExist:
            pass

        if service:
            data = {
                'tag': list(value.tag for value in service)
            }

        if data:
            try:
                data['organization'] = ContactsMap.objects.get(
                    asn=asn.number, ix=ix_code).organization.name
            except ContactsMap.DoesNotExist:
                data = {}

    except ASN.DoesNotExist:
        data = {}

    return JsonResponse(data)


def get_tag_informations_by_click__tag_views(request, **kwargs):
    """Display informations about TAG clicked.

    Args:
        request (WSGIRequest): GET
            "/core/sp/get-match-tags-by-asn-search/?asn='asn'">
        **kwargs: A dictionaty with the parameters of this ix.
            Example:
                kwargs['code'] = 'sp'

    Attributes:
        ix_code (str): IX code of the bundle where this tag is localized,
            gotten via AJAX GET request.
        service (dict): Service where the TAG is localized.
        tag (int): Tag uuid clicked by user, gotten via AJAX GET request.

    Returns:
        A JsonResponse data set dictionary with Organization name and
        Tags matched.

        For example:

        {
            'organization': 'Chaney-Medina',
            'asn': 15000
        }
    """
    ix_code = kwargs['code']
    tag_uuid = request.GET['tag']
    data = dict()
    try:
        tag_request = Tag.objects.get(uuid=tag_uuid, ix=ix_code)
        data = {
            'tag': str(tag_request.tag),
        }

        service = list()
        service.extend(MLPAv4.objects.filter(tag__pk=tag_request.uuid))
        service.extend(MLPAv6.objects.filter(tag__pk=tag_request.uuid))
        service.extend(Monitorv4.objects.filter(tag__pk=tag_request.uuid))
        service.extend(BilateralPeer.objects.filter(tag__pk=tag_request.uuid))
        if service:
            service = service[0]

            data = {
                'asn': service.asn.number
            }
            try:
                data['organization'] = ContactsMap.objects.get(
                    asn=service.asn.number,
                    ix=ix_code).organization.name
            except ContactsMap.DoesNotExist:
                data = {}
        else:
            data = {}
    except Tag.DoesNotExist:
        data = {}

    return JsonResponse(data)


"""****************************************
************** IX_DETAIL AJAX *************
****************************************"""


def ix_detail_cix_ajax__ix_views(request, *args, **kwargs):
    """Show CIX informations and stats on click to see more about CIX in that IX.

    Args:
        request (WSGIRequest): GET "/core/sp/cix-detail/?uuid='cix_uuid'">
        **kwargs(dict): A dictionaty with the parameters of this ix.
            Example:
                kwargs['code'] = 'sp'

    Attributes:
        cix_uuid (str): The uuid of CIX clicked, gotten via AJAX GET request.
        channel (<class 'ixbr_api.core.models.CustomerChannel'>): Customer
            Channel with cix_uuid
        cix_infos (dict): A dictionary with stats of this cix.
            Example:
                Amount of ASNs linked in this CIX;
                Amount of MLPAv4 in this CIX;
                Amount of MLPAv6 in this CIX;
                Amount of Bilateal in this CIX;

    Returns:
        Return data set a dictionary in JsonResponse format, with a set
        of informations and stats of CIX, like: ASNs, bilateral, MLPAv6
        and MLPAv4 amounts, Switch set (with model and management ip)
        and the Customer Channel uuid.

        For example:
        {
            'asn_amount': 1,
            'switch_set': {
                '0': {
                    'model': '[ASR9922]',
                    'management_ip': '192.168.0.236'
                }
            },
            'mlpav6_amount': 1,
            'channel': 'd3524944-31af-483d-b56c-f7807e68c8b1',
            'mlpav4_amount': 1,
            'bilateral_amount': 0
            'port_master': '192.168.28.2: 1',
            'lag': {
                '192.168.28.3': ['1', '2']
            }
        }
    """
    cix_uuid = request.GET['uuid']
    channel = CustomerChannel.objects.get(uuid=cix_uuid)

    data = dict()
    cix_infos = channel.get_stats_amount()
    port_master = channel.get_master_port()
    lag_dict = dict()
    if channel.is_mclag or channel.is_lag:
        for port in channel.get_ports():
            if port.switch.management_ip in lag_dict.keys():
                lag_dict[port.switch.management_ip].append(port.name)
            else:
                lag_dict[port.switch.management_ip] = [port.name]

    data['channel'] = cix_uuid
    data['asn_amount'] = cix_infos['asn_amount']
    data['mlpav4_amount'] = cix_infos['mlpav4_amount']
    data['mlpav6_amount'] = cix_infos['mlpav6_amount']
    data['bilateral_amount'] = cix_infos['bilateral_amount']
    data['switch_set'] = channel.get_switch_infos_by_port()
    data['port_master'] = "%s: %s" % (
        port_master.switch.management_ip, port_master.name)
    data['lag'] = lag_dict

    return JsonResponse(data)


def ix_detail_pix_ajax__ix_views(request, *args, **kwargs):
    """Show PIX informations and stats on click to see more about PIX in that IX.

    Args:
        request (WSGIRequest): GET "/core/sp/pix-detail/?pix='pix_uuid'"
        **kwargs(dict): A dictionaty with the parameters of this ix.
            Example:
                kwargs['code'] = 'sp'

    Attributes:
        pix_uuid (str): The uuid of PIX clicked, gotten via AJAX GET request.
        pix (<class 'ixbr_api.core.models.PIX'>): Get the cix wit that pix_uuid
        pix_infos (dict): A dictionary with stats of this pix.
                Amount of ASNs in this PIX;
                Amount of CIX in this PIX;
                Amount of MLPAv4 in this PIX;
                Amount of MLPAv6 in this PIX;
                Amount of Bilateal in this PIX;

    Returns:
        A data set dictionary in JsonResponse format, with a set
        of informations and stats of PIX, like: ASNs, CIXs, bilateral, MLPAv6
        and MLPAv4 amounts, Switch set (with model and management ip, amount of
        available ports and uuid).

        For example:
        {
            'bilateral_amount': 0,
            'cix_amount': 6,
            'switch_set': {
                '1': {
                    'available_ports': '23',
                    'uuid': '72f18dcb-ee61-42e3-8f31-b9e3391e6bb6',
                    'management_ip': '192.168.0.241',
                    'model': '[ASR9922]'}, '
                0': {
                    'available_ports': '22',
                    'uuid': '13518db0-fffe-4a03-8929-73bc8fc08e16',
                    'management_ip': '192.168.0.103',
                    'model': '[ASR9922]'}
            },
            'mlpav4_amount': 6,
            'asn_amount': 6,
            'mlpav6_amount': 6
        }
    """
    pix_uuid = request.GET['pix']
    data = {}
    pix = PIX.objects.get(uuid=pix_uuid)
    pix_infos = pix.get_stats_amount()

    data['asn_amount'] = pix_infos['asn_amount']
    data['mlpav4_amount'] = pix_infos['mlpav4_amount']
    data['mlpav6_amount'] = pix_infos['mlpav6_amount']
    data['bilateral_amount'] = pix_infos['bilateral_amount']
    data['switch_set'] = pix.get_switch_infos_by_pix()
    data['cix_amount'] = pix_infos['cix_amount']

    return JsonResponse(data)


"""****************************************
************** AS Contact *****************
****************************************"""


def get_ticket_add_add_ajax__as_view(request):
    """Gets the ticket data to creates a new AS.

    This FBV is used to query a ticket and gather all necessary data to
    populate the AS Contact Form. It receives a ticket, and query from meu_ix.
    This function is used by:
        - ix-api/ixbr_api/core/urls.py (directly)
    Args:
        request: http request

    Returns: a json with all necessary fields to populate a AS Contact Form
    """

    ticket = request.POST['ticket_id']
    # 'http://hercules.ix.br:9090/api/tickets/' + ticket
    url = external_api_urls.get_ticket_api_url() + ticket
    ticket_api_get = get(url)

    if ticket_api_get.status_code > 299:
        return JsonResponse({
            'message': ticket_api_get.reason,
            'status': ticket_api_get.status_code,
        })

    ticket_to_poputate = ticket_api_get.json()

    data_to_populate = {
        'ticket': int(ticket),
        'asn': ticket_to_poputate['asn'],
        'ix': ticket_to_poputate['ix'],
        'org_name': ticket_to_poputate['Nome da Entidade']['Nome da Entidade'],
        'org_shortname': ticket_to_poputate['Nome da Entidade']['Nome curto'],
        'org_cnpj': ticket_to_poputate['Nome da Entidade']['CNPJ'],
        'org_url': ticket_to_poputate['Nome da Entidade']['Site'],
        'org_addr': ticket_to_poputate['Endereco da Entidade']['Logradouro'],

        'contact_name_noc':
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']['Nome'],
        'contact_email_noc':
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']['Email'],
        'contact_phone_noc':
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']
            ['Telefone'],

        'contact_name_adm':
            ticket_to_poputate['Contatos do ASN']['Contato Administrativo']
            ['Nome'],
        'contact_email_adm':
            ticket_to_poputate['Contatos do ASN']['Contato Administrativo']
            ['Email'],
        'contact_phone_adm':
            ticket_to_poputate['Contatos do ASN']['Contato Administrativo']
            ['Telefone'],

        'contact_name_peer':
            ticket_to_poputate['Contatos do ASN'][
                'Contato de Peering']['Nome'],
        'contact_email_peer':
            ticket_to_poputate['Contatos do ASN']['Contato de Peering']
            ['Email'],
        'contact_phone_peer':
            ticket_to_poputate['Contatos do ASN']['Contato de Peering']
            ['Telefone'],

        'contact_name_com':
            ticket_to_poputate['Contatos do ASN']['Contato Comercial']['Nome'],
        'contact_email_com':
            ticket_to_poputate['Contatos do ASN'][
                'Contato Comercial']['Email'],
        'contact_phone_com':
            ticket_to_poputate['Contatos do ASN']['Contato Comercial']
            ['Telefone'],
        'contact_name_org': (
            ticket_to_poputate['Nome da Entidade']['Nome da Entidade'] if
            ticket_to_poputate['Contatos do ASN']['Organizacao']['Nome']
            is "None"
            else ticket_to_poputate['Nome da Entidade']['Nome da Entidade']
        ),
        'contact_email_org': (
            ticket_to_poputate['Contatos do ASN']['Organizacao']['Email'] if
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']['Email']
            is "None" else
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']['Email']
        ),
        'contact_phone_org': (
            ticket_to_poputate['Contatos do ASN']['Organizacao']['Telefone'] if
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']
            ['Telefone']
            is "None" else
            ticket_to_poputate['Contatos do ASN']['Contatos do NOC']
            ['Telefone']
        ),
    }

    response = HttpResponse(json.dumps(data_to_populate),
                            content_type='application/json')
    return response


"""****************************************
*********** Customer Channel **************
****************************************"""


def get_ports_by_switch_search__as_detail(request):
    """Find Ports that match with Switch.

    Args:
        request (WSGIRequest): GET
            "/core/get-ports-by-switch/?switch='switch'">
        **kwargs: A dictionaty with the parameters of this ix.
            Example:
                kwargs['switch_uuid'] = 'uuid'

    Attributes:
        swtich (uuid): UUID from swtich, gotten via AJAX GET request.
        data (dict): Dictionary that return a set of ports from given switch.

    Returns:
        A JsonResponse data set with Ports which match with
        Switch searched for.

        For example:

        {
            'ports': {
                'port_uuid': 'port_number',
                'port_uuid': 'port_number',
                ...
            }
        }
    """
    switch_uuid = request.GET['switch_uuid']

    switch = Switch.objects.get(pk=switch_uuid)

    port_set = switch.port_set.filter(status='AVAILABLE')

    port_list = {}
    for port in port_set:
        port_list[str(port.name)] = str(port.uuid)

    ordered_ports = port_utils.port_sorting(port_list)

    channel_name_prefix = SWITCH_MODEL_CHANNEL_PREFIX[switch.model.vendor]

    data = {
        'ports': ordered_ports,
        'name_prefix': channel_name_prefix,
    }
    return JsonResponse(data)


def get_switchs_by_pix_search__as_detail(request):
    """Find Ports that match with Switch.

    Args:
        request (WSGIRequest): GET
            "/core/get-switchs-by-pix/?pix_pk='pix_pk'">
        **kwargs: A dictionaty with the parameters of this ix.
            Example:
                kwargs['pix_pk'] = 'uuid'

    Attributes:
        swtich (uuid): UUID from swtich, gotten via AJAX GET request.
        data (dict): Dictionary that return a set of ports from given switch.

    Returns:
        A JsonResponse data set with switchs which match with
        PIX searched for.

        For example:

        {
            'switchs': {
                'switch_uuid': 'management_ip',
                'switch_uuid': 'management_ip',
                ...
            }
        }
    """

    pix_pk = request.GET['pix_pk']

    switch_list = dict((str(switch.uuid), switch.management_ip)
                       for switch in Switch.objects.filter(pix__pk=pix_pk))

    data = {
        'switchs': switch_list,
    }
    return JsonResponse(data)


"""******************************************
******** FORM LIST IPs AND TAGs AJAX ********
******************************************"""


def get_ips_and_tags_by_ix(request):
    option = request.GET['option']
    ix = request.GET['ix']
    channel = request.GET['channel']
    channel_object = CustomerChannel.objects.get(pk=channel)

    tag_list = []
    data = {}

    ips = get_free_ips_by_ix(option, ix)
    ipv4 = ips['ipv4']
    ipv6 = ips['ipv6']

    tags_free = get_tag_without_bilateral(ix=ix, channel=channel_object)[:2]
    for tag in tags_free:
        tag_list.append(int(tag.tag))

    if option == 'only_v4':
        data = {
            'ipv4': __ip_list(ipv4),
            'tag': tag_list
        }

    elif option == 'only_v6':
        data = {
            'ipv6': __ip_list(ipv6),
            'tag': tag_list
        }

    elif option == 'v4_and_v6':
        data = {
            'ipv4': __ip_list(ipv4),
            'ipv6': __ip_list(ipv6),
            'tag': tag_list,
            'cix_type': channel_object.cix_type
        }
    return JsonResponse(data)


def __ip_list(ip):
    ip_list = []
    ip_list.append(str(ip.address))
    return ip_list


def get_tags_by_port(request):
    port_pk = request.GET['port_pk']
    ix_pk = request.GET['ix']

    port = Port.objects.get(pk=port_pk)
    ix = IX.objects.get(pk=ix_pk)

    tag = dict()

    cur_port = port.channel_port.customerchannel
    try:
        asn = ASN.objects.filter(
            Q(pk__in=cur_port.mlpav4_set.all().values_list(
                'asn', flat=True)))
        for as_number in asn:
            if as_number.number not in tag:
                tag[as_number.number] = []
            tags = Tag.objects.filter(
                Q(pk__in=as_number.mlpav4_set.filter(
                    customer_channel=cur_port.pk).values_list(
                    'tag', flat=True))).filter(ix=ix.pk)
            if tags:
                tag[as_number.number].append(
                    list(value.tag for value in tags))
                tag[as_number.number] = sorted(
                    tag[as_number.number], reverse=False)

    except MLPAv4.DoesNotExist:
        pass
    try:
        asn = ASN.objects.filter(
            Q(pk__in=cur_port.mlpav6_set.all().values_list(
                'asn', flat=True)))
        for as_number in asn:
            if as_number.number not in tag:
                tag[as_number.number] = []
            tags = Tag.objects.filter(
                Q(pk__in=as_number.mlpav6_set.filter(
                    customer_channel=cur_port.pk).values_list(
                    'tag', flat=True))).filter(ix=ix.pk)
            if tags:
                tag[as_number.number].append(
                    list(value.tag for value in tags))
                tag[as_number.number] = sorted(
                    tag[as_number.number], reverse=False)
    except MLPAv6.DoesNotExist:
        pass
    try:
        asn = ASN.objects.filter(
            Q(pk__in=cur_port.bilateralpeer_set.all().values_list(
                'asn', flat=True)))
        for as_number in asn:
            if as_number.number not in tag:
                tag[as_number.number] = []
            tags = Tag.objects.filter(
                Q(pk__in=as_number.bilateralpeer_set.filter(
                    customer_channel=cur_port.pk).values_list(
                    'tag', flat=True))).filter(ix=ix.pk)
            if tags:
                tag[as_number.number].append(
                    list(value.tag for value in tags))
                tag[as_number.number] = sorted(
                    tag[as_number.number], reverse=False)
    except BilateralPeer.DoesNotExist:
        pass
    try:
        asn = ASN.objects.filter(
            Q(pk__in=cur_port.monitorv4_set.all().values_list(
                'asn', flat=True)))
        for as_number in asn:
            if as_number.number not in tag:
                tag[as_number.number] = []
            tags = Tag.objects.filter(
                Q(pk__in=as_number.monitorv4_set.filter(
                    customer_channel=cur_port.pk).values_list(
                    'tag', flat=True))).filter(ix=ix.pk)
            if tags:
                tag[as_number.number].append(
                    list(value.tag for value in tags))
                tag[as_number.number] = sorted(
                    tag[as_number.number], reverse=False)
    except Monitorv4.DoesNotExist:
        pass
    return JsonResponse(tag)


def get_new_customer_channels_by_switch(request):
    """
        This function returns a Queryset of CustomerChannels in a given Switch
        where a given ASN has no Service in a given Switch.
        Args:
            switch: request GET parameter
            asn: request GET parameter
        Returns:
            JsonResponse: dict list of [channel.name - channel.asn_id]
    """
    switch = request.GET['switch']
    asn = request.GET['asn']

    used_channels = CustomerChannel.objects.filter(
        Q(mlpav4__asn__pk=asn) |
        Q(mlpav6__asn__pk=asn) |
        Q(monitorv4__asn__pk=asn) |
        Q(bilateralpeer__asn__pk=asn))

    cix_rules_free_channels = CustomerChannel.objects.filter(
        Q(asn__pk=asn) |
        Q(cix_type__gt=0)
    )

    channels_query = cix_rules_free_channels.filter(
        channel_port__port__switch=Switch.objects.get(
            pk=switch)).exclude(pk__in=used_channels)

    return JsonResponse(_build_channel_data(channels_query))


def get_customer_channels_by_switch_and_asn(request):
    """
        This function returns a Queryset of CustomerChannels in a given Switch
        where a given ASN is the owner or has a service.
        Args:
            switch: request GET parameter
            asn: request GET parameter
        Returns:
            JsonResponse: dict list of [channel.name - channel.asn_id]
    """
    switch = request.GET['switch']
    asn = request.GET['asn']

    channels_query = CustomerChannel.objects.filter(
        Q(mlpav4__asn__pk=asn) |
        Q(mlpav6__asn__pk=asn) |
        Q(monitorv4__asn__pk=asn) |
        Q(bilateralpeer__asn__pk=asn))

    own_channels = CustomerChannel.objects.filter(asn__pk=asn)

    channels_query = channels_query | own_channels

    channels_query = channels_query.filter(
        channel_port__port__switch=Switch.objects.get(
            pk=switch))

    return JsonResponse(_build_channel_data(channels_query))


def _build_channel_data(channels):
    """Given channels to build a dict to return as JSON response

    Args:
        channels (QuerySet): Channels to list

    Returns:
        Dict: JSON-ready listing channels
    """
    return {'channels_list': {
        str(channel.pk): "{0} - AS {1}".format(channel.name, channel.asn_id)
        for channel in channels}}


def get_cix_type_by_customer_channel(request):
    """
        This function returns the cix type of a given channel
        Args:
            channel: CustomerChannel request GET parameter
        Returns:
            cix_type: Int cix type number
    """
    channel = request.GET['channel']
    cix_type = CustomerChannel.objects.get(pk=channel).cix_type
    data = {'cix_type': cix_type}

    return JsonResponse(data)


def get_bilateral_type(request):
    """
        This function returns the bilateral type between channels
        Args:
            channel_a: CustomerChannel request GET parameter
            channel_b: CustomerChannel request GET parameter
        Returns:
            bilateral_type
            tags and inner tags
    """
    channel_a = CustomerChannel.objects.get(pk=request.GET['channel_a'])
    channel_b = CustomerChannel.objects.get(pk=request.GET['channel_b'])
    ix = IX.objects.get(pk=request.GET['ix'])
    bilateral_type = define_bilateral_case(
        channel_a=channel_a,
        channel_b=channel_b)
    if bilateral_type == 3:
        tag_a = get_tag_without_bilateral(ix=ix, channel=channel_a)[0]
        tag_a_number = tag_a.tag
        tag_b = get_tag_without_bilateral(ix=ix, channel=channel_b)[0]
        tag_b_number = tag_b.tag
        inner_a = get_available_inner_tag(tag=tag_a)
        inner_b = 0
        for i in range(inner_a, 4097):
            if not check_inner_tag_availability(tag=tag_b, inner=i):
                continue
            else:
                if not check_inner_tag_availability(tag=tag_a, inner=i):
                    continue
                else:
                    inner_a = i
                    inner_b = i
                    break

        data = {'bilateral_type': bilateral_type,
                'tag_a': tag_a_number, 'tag_b': tag_b_number,
                'inner_a': inner_a, 'inner_b': inner_b}
    elif bilateral_type == 1:
        tag_a = get_tag_without_all_service(ix=ix, channel=channel_a)[0].tag
        tag_b = get_tag_without_bilateral(ix=ix, channel=channel_b)[0].tag
        data = {
            'bilateral_type': bilateral_type, 'tag_b': tag_b, 'tag_a': tag_a}
    elif bilateral_type == 2:
        tag_a = get_tag_without_bilateral(ix=ix, channel=channel_a)[0].tag
        tag_b = get_tag_without_all_service(ix=ix, channel=channel_a)[0].tag
        data = {
            'bilateral_type': bilateral_type, 'tag_a': tag_a, 'tag_b': tag_b}
    elif bilateral_type == 0:
        tag_a = get_tag_without_all_service(ix=ix, channel=channel_a)[0].tag
        tag_b = tag_a
        data = {
            'bilateral_type': bilateral_type, 'tag_a': tag_a, 'tag_b': tag_b}
    else:
        data = {'bilateral_type': bilateral_type}

    return JsonResponse(data)


def get_lag_port(request):
    port_pk = request.GET['port_pk']
    port_object = Port.objects.get(pk=port_pk)

    cur_port = port_object.channel_port.customerchannel

    list_ports = []
    if cur_port.is_lag is False:
        list_ports.append(None)
    else:
        for port in port_object.channel_port.port_set.all():
            customer = CustomerChannel.objects.filter(
                channel_port=port.channel_port)

            if customer.first().name == port.name:
                html = "<span style='color:red;'>" + \
                    str(port.name) + " (master)</span>"
                list_ports.append(html)
            else:
                list_ports.append(port.name)

    data = {'ports': list_ports}
    return JsonResponse(data)


def get_used_customer_channels_by_switch(request):
    """
        This function returns a Queryset of CustomerChannels in a given Switch
        where a given ASN has a Service in a given Switch.
        Args:
            switch: request GET parameter
            asn: request GET parameter
        Returns:
            channels_list: dict list of [channel.name-channel.pk]

    """
    switch = request.GET['switch']
    asn = request.GET['asn']
    channels_list = {}

    used_channels = CustomerChannel.objects.filter(
        Q(mlpav4__asn__pk=asn) |
        Q(mlpav6__asn__pk=asn) |
        Q(monitorv4__asn__pk=asn) |
        Q(bilateralpeer__asn__pk=asn))

    channels_query = used_channels.filter(
        channel_port__port__switch=Switch.objects.get(pk=switch))
    for channel in channels_query:
        channels_list = {str(channel.uuid): channel.name + " - " +
                         str(channel.uuid)}
    data = {'channels_list': channels_list}
    return JsonResponse(data)


def remove_switch_module(request):
    """
        This function get the SwitchModule's pk and delete it
        Args:
            pk: request GET parameter
        Returns:
            deleted: True if succeded
    """
    pk = request.GET['pk']

    delete_switch_module_use_case(pk=pk)

    data = {'': ""}

    return JsonResponse(data)


def delete_service(request, service_pk):
    """
        This function receive the Service's pk and delete it
        Args:
            service_pk: request GET parameter
        Returns:
            Response: If removes the resource, must return an empty response,
            otherwise must return a HttpResponse status 400
    """
    try:
        if request.method == 'POST':
            delete_service_use_case(pk=service_pk)
            return JsonResponse({'': ""})
    except ValidationError as e:
        return JsonResponse({'message': e.messages}, status=400)
    return HttpResponse(status=400)


def search_customer_channel_by_mac(request):
    mac = request.GET['mac']
    address = MACAddressConverterToSystemPattern(
        mac).mac_address_converter()

    channels_query = search_customer_channel_by_mac_address(
        address=address)

    channels_list = dict()
    for channel in channels_query:
        channels_list = {str(channel.uuid): channel.name + " - " +
                         str(channel.uuid)}
    data = {'channels_list': channels_list}
    return JsonResponse(data)
