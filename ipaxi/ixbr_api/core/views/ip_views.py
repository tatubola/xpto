from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from ..models import IX, IPv4Address, IPv6Address, MLPAv4, MLPAv6, Monitorv4


class IPListView(LoginRequiredMixin, View):
    """List IPs of a specific location.

    List ips into a table marked by ALLOCATED or FREE status.
    And show stats of IPs.

    Attributes:
        context (dict): Dictionary that return a set of informations
            to be printed.
        dict_ips (dict): Dictionary with IP address and its status
            (ALLOCATED or FREE).
        allocated_ipv4 (QuerySet): cached information of allocated ip v4
        allocated_ipv6 (QuerySet): cached information of allocated ip v6
        ipv4s (<class 'django.db.models.query.QuerySet'>): Get queryset with
            filtered IPv4s from a specified IX.
        ipv6s (<class 'django.db.models.query.QuerySet'>): Get queryset with
            filtered IPv6s from a specified IX.
        ix (<class 'ixbr_api.core.models.IX'>): Get the ix from IX models or
            return a 404.
        template_name (str): core/ip_list.html'

    Returns:
        A dict context with all information about a collection of IPs into a
        IX. For example:
        {
          'ix': <IX: [jpa]>,
          'ips': {
            1: {
              'v4': <IPv4Address: [187.16.193.1]>,
              'v4_status': "ALLOCATED"
              'v6': <IPv6Address: [2001:12f8:0:16::1]>
              'v6_status': "ALLOCATED"
            },
            2: {
              'v4': <IPv4Address: [187.16.193.2]>,
              'v4_status': "FREE"
              'v6': <IPv6Address: [2001:12f8:0:16::2]>
              'v6_status': "FREE"
            },
            3: {
              'v4': <IPv4Address: [187.16.193.3]>,
              'v4_status': "FREE"
              'v6': <IPv6Address: [2001:12f8:0:16::3]>
              'v6_status': "FREE"
            }
          }
        }
    """

    def get(self, request, code):
        template_name = 'core/ip_list.html'
        ix = get_object_or_404(IX, code=code)
        ipv4s = IPv4Address.objects.filter(ix=code)
        ipv6s = IPv6Address.objects.filter(ix=code)

        allocated_ipv4 = IPv4Address.objects.filter(
            Q(address__in=MLPAv4.objects.filter(
                mlpav4_address__ix=code).values_list(
                'mlpav4_address', flat=True))
            | Q(address__in=Monitorv4.objects.filter(
                monitor_address__ix=code).values_list(
                'monitor_address', flat=True)))

        allocated_ipv6 = IPv6Address.objects.filter(
            Q(address__in=MLPAv6.objects.filter(
                mlpav6_address__ix=code).values_list(
                'mlpav6_address', flat=True)))

        dict_ips = dict()
        for index, ipv4 in enumerate(ipv4s):
            # index+1 because IPs start at 1
            dict_ips[index+1] = {
                "v4": ipv4,
                "v4_status": "ALLOCATED" if ipv4 in allocated_ipv4 else "FREE",
                "v6": ipv6s[index],
                "v6_status": "ALLOCATED" if ipv6s[index] in allocated_ipv6
                             else "FREE"
            }

        context = {'ips': dict_ips, 'ix': ix}
        return render(request, template_name, context)
