from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/$', views.map, name='map'),
    url(r'^dashboard/', include([
        url(r'^$', views.dashboard, name='dashboard'),
        url(r'^add/$', views.kit_add, name='kit_add'),
        url(r'^(?P<kit_id>[0-9]+)/', include([
            url(r'^$', views.kit, name='kit'),
            url(r'^configure/', include([
                 url(r'^profile/$', views.kit_configure_profile, name='kit_configure_profile'),
                 url(r'^members/$', views.kit_configure_members, name='kit_configure_members'),
            ])),
        ])),
    ])),
    url(r'^sensors/', include([
        url(r'^$', views.sensor_definition_list, name='sensor_definition_list'),
        url(r'^add/$', views.sensor_definition_add, name='sensor_definition_add'),
        url(r'^(?P<sensor_definition_id>[0-9]+)/', include([
            url(r'^configure/$', views.sensor_definition_configure, name='sensor_definition_configure'),
        ])),
    ])),
]
