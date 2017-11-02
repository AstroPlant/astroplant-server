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
            url(r'^configure/$', views.kit, name='kit_configure'),
        ])),
    ])),
    url(r'^sensors/', include([
        url(r'^add/$', views.sensor_definition_add, name='sensor_definition_add'),
        url(r'^(?P<sensor_definition_id>[0-9]+)/', include([
            url(r'^configure/$', views.sensor_definition_configure, name='sensor_definition_configure'),
        ])),
    ])),
]
