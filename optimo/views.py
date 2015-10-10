from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'optimo/home.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(Home, self).get_context_data(*args, **kwargs)
        return ctx
