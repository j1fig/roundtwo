from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^airport/$', views.Airport.as_view(), name='airport'),
    url(r'^aircraft/$', views.Aircraft.as_view(), name='aircraft'),
)
