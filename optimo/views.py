from django.views.generic import TemplateView, View
from django.http import JsonResponse


class Home(TemplateView):
    template_name = 'optimo/home.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(Home, self).get_context_data(*args, **kwargs)
        return ctx


class Airport(View):
    def post(self, request, *args, **kwargs):
        print request
        pass


class Aircraft(View):
    def post(self, request, *args, **kwargs):
        pass
