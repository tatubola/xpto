from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View
from django.db.models import Q
from ..models import (IX, CustomerChannel,
                      DownlinkChannel, Port, Organization, ASN, MLPAv4,
                      MLPAv6, Bilateral, Tag, MACAddress, ChannelPort,
                      Switch)


class BundleEtherListView(LoginRequiredMixin, ListView):
    """List the Bundle of a IX specified

    Attributes:
        downlink_channel (<class 'django.db.models.query.QuerySet'>):
        Get all the downlink channel of a IX specified.
        ix (<class 'ixbr_api.core.models.IX'>): Get the ix from IX models or
        return a 404.
        paginate_by (int): Amount of Bundle that will be listed.
        template_name (str): core/bundle_list.html
    returns:
        A dict context with all the Bundle of a IX specified. For example:
            {'bundle': <QuerySet [<DownlinkChannel: [sw226-dl]>]>,},
            {'ix': [sp],}

    """
    template_name = 'core/bundle_list.html'
    model = DownlinkChannel

    def get_queryset(self):
        ix_code = self.kwargs['code']
        self.ix = get_object_or_404(IX, code=ix_code)
        if self.ix.tags_policy == 'distributed':
            self.downlink_channel = DownlinkChannel.objects.filter(
                channel_port__tags_type='Direct-Bundle-Ether',
                channel_port__in=Port.objects.filter(
                    switch__pix__ix__pk=self.ix.code).values_list(
                    'channel_port', flat=True))
            self.customer_channel = CustomerChannel.objects.filter(
                channel_port__tags_type='Direct-Bundle-Ether',
                channel_port__in=Port.objects.filter(
                    switch__pix__ix__pk=self.ix.code).values_list(
                    'channel_port', flat=True))
            return self.downlink_channel
        else:
            self.downlink_channel = ''

    def get_context_data(self, **kwargs):
        """Call the base implemetnation first to get a context"""
        context = super(BundleEtherListView, self).get_context_data(**kwargs)
        context['bundle'] = self.downlink_channel
        context['ix'] = self.ix

        return context


class HomeView(LoginRequiredMixin, ListView):
    """List all IX at /core/home

    Attributes:
        context (dic): Dictionary that return a set of informations
        to be printed.
        template_name (str): core/home.html.
    returns:
        A dict context with all the IXs. For example:
        {'ix_list' : <QuerySet [<IX: [cpv]>, <IX: [rj]>, <IX: [sp]>]>}

    """

    template_name = 'core/home.html'
    model = IX

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ix_list'] = context['object_list']

        return context


class SearchASNByNameView(LoginRequiredMixin, View):
    def get(self, request):
        name = request.GET.get('name')
        prev_path = request.GET.get('prev_path')
        organizations = Organization.objects.filter(name__icontains=name)

        if not organizations:
            messages.error(self.request, (name + " not found "),
                           extra_tags='search_not_found')
            return redirect(prev_path)

        organizations_dict = dict()
        for organization in organizations:
            organizations_dict[organization.name] = list(ASN.objects.filter(
                Q(pk__in=organization.contactsmap_set.all().values_list(
                    'asn', flat=True))).values_list('number', flat=True))
        context = {
            'name': name,
            'organizations': organizations_dict
        }
        return render(request, 'core/as_list.html', context)


class SearchUUIDView(LoginRequiredMixin, View):
    def get(self, request):
        uuid = request.GET.get('uuid')
        prev_path = request.GET.get('prev_path')
        search_data = list()

        where_to_look_list = ['MLPAv4', 'MLPAv6', 'Tag',
                              'MacAddress', 'ChannelPort', 'Port', 'Switch']

        for service in where_to_look_list:
            if service == 'MLPAv4':
                service_uuid = MLPAv4.objects.filter(uuid__icontains=uuid)
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))
                continue

            elif service == 'MLPAv6':
                service_uuid = MLPAv6.objects.filter(uuid__icontains=uuid)
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))
                continue

            elif service == 'Bilateral':
                service_uuid = Bilateral.objects.filter(uuid__icontains=uuid)
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))

            elif service == 'Tag':
                service_uuid = Tag.objects.filter(Q(Q(status='PRODUCTION') |
                                                  Q(status='ALLOCATED')) &
                                                  Q(uuid__icontains=uuid))
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))
                continue

            elif service == 'ChannelPort':
                service_uuid = ChannelPort.objects.filter(uuid__icontains=uuid)
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))
                continue

            elif service == 'Port':
                service_uuid = Port.objects.filter(uuid__icontains=uuid)
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))
                continue

            elif service == 'Switch':
                service_uuid = Switch.objects.filter(uuid__icontains=uuid)
                if len(service_uuid) > 0:
                    search_data.extend(self.__build_dict(service_uuid, service))
                continue

        if len(search_data) == 0:
            messages.error(self.request, (uuid + " not found"),
                           extra_tags='search_not_found')
            return redirect(prev_path)

        context = {
            'uuid': uuid,
            'search_res': search_data,
        }
        return render(request, 'core/uuid_list.html', context)

    def __build_dict(self, query_set, item_type):
        info =list()

        for item in query_set:
            item_dict = dict()
            item_dict["type"] = item_type
            item_dict["desc"] = str(item)
            info.append(item_dict)

        return info
