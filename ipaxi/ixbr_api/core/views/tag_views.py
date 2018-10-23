from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from ..models import IX, DownlinkChannel, Port, Tag


class TAGsListView(LoginRequiredMixin, ListView):
    """List tags of a specified bundle into a table.

    List tags into a table and marked by AVAILABLE and PRODUCTION status.
    And show stats of tag status.

    Attributes:
        bundle_pk (str): Get bundle pk to search tags into this bundle
            from kwargs at url regex: "(?P<bundle_pk>[0-9a-f]{8}-[0-9a-f]
                {4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})".
        bundle_name (str): Get the name of bundle in question.
        context (dict): Dictionary that return a set of informations
            to be printed.
        ix (<class 'ixbr_api.core.models.IX'>): Get the ix from IX
            models or return a 404.
        ix_code (str): Get ix code from kwargs at url regex:
            "(?P<code>[a-z]{2,4})".
        switch_model (<class 'ixbr_api.core.models.SwitchModel'>): Get the
            model of switch.
        tags (<class 'ixbr_api.core.models.IXAPIQuerySet'>): List of all
            tags in this bundle.
        template_name (str): core/tag_list.html.

    Returns:
        A dict context with all information about a collection of tags into a
        bundle-ether. For example:

        {'bundle': <DownlinkChannel: [sw155-dl]>,'
        switch': <SwitchModel: [ASR9922]>,
        'object_list':
            <QuerySet [<Tag: [[sp]-2:[sw15-dl]]>,'...
                (remaining elements truncated)...']>,
        'page_obj': None,
        'is_paginated': False}
    """

    template_name = 'core/tag_list.html'
    model = Tag

    def get_queryset(self):
        ix_code = self.kwargs['code']
        self.status = self.kwargs['status'] \
            if 'status' in self.kwargs else None
        self.ix = get_object_or_404(IX, code=ix_code)
        try:
            bundle_pk = self.kwargs['bundle_pk']
            self.bundle_name = DownlinkChannel.objects.get(pk=bundle_pk)
            self.switch_model = Port.objects.filter(
                channel_port=self.bundle_name.channel_port).\
                first().switch.model
            self.tags = DownlinkChannel.objects.get(
                pk=bundle_pk).channel_port.tag_set.all()
            self.available_amount = len(self.tags.filter(status='AVAILABLE'))
            self.production_amount = len(self.tags.filter(status='PRODUCTION'))
        except Exception:
            self.bundle_name = ''
            self.switch_model = ''
            self.tags = IX.objects.get(pk=ix_code).tag_set.all()
            self.available_amount = len(self.tags.filter(status='AVAILABLE'))
            self.production_amount = len(self.tags.filter(status='PRODUCTION'))

        return self.tags

    def get_context_data(self, **kwargs):
        """Call the base implementation first to get a context"""
        context = super(TAGsListView, self).get_context_data(**kwargs)
        context['tag_status'] = self.status
        context['ix'] = self.ix
        context['tags'] = self.tags
        context['bundle'] = self.bundle_name
        context['switch'] = self.switch_model
        context['available_amount'] = self.available_amount
        context['production_amount'] = self.production_amount

        return context
