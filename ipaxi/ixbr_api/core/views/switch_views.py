
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from ..models import IX, Switch, SwitchModule


class SwitchListView(LoginRequiredMixin, View):
    """List the summary of a switch

    Attributes:
        ix (<class 'ixbr_api.core.models.IX'>): Get the ix from IX models or
            return a 404.
        switch (<class 'django.db.models.query.QuerySet'>): Get queryset of a
            given switch.
    returns:
        A dict context with a Switch object and IX object specified.
    """

    def get(self, request, *args, **kwargs):
        template_name = 'core/switch_detail.html'

        ix_code = kwargs['code']
        switch_uuid = kwargs['switch_uuid']

        self.ix = get_object_or_404(IX, code=ix_code)
        self.switch = Switch.objects.get(pk=switch_uuid)

        context = {
            'ix': self.ix,
            'switch': self.switch,
            }
        return render(request, template_name, context)

class SwitchModuleDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        template_name = 'core/switch_module_detail.html'

        module_id = kwargs['module']

        self.switch_module = get_object_or_404(SwitchModule, pk=module_id)

        context = {
            'module': self.switch_module
        }

        return render(request, template_name, context)
