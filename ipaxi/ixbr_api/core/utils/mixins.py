import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect


class LogsMixin(object):
    logr = logging.getLogger('root')
    def makeLog(self, classes, args):
        log = "User: %s Modified model(s) %s on fields %s "%(str(self.request.user), classes, args)

        self.logr.info(log)


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            messages.error(self.request, form.errors)
            return redirect(self.request.META.get('PATH_INFO'))
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response
