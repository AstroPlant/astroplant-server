from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/$', views.map, name='map'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^kit/', include([
        url(r'(?P<kit_id>[0-9]+)/', include([
            url(r'$', views.kit, name='kit'),
            url(r'configure/$', views.kit),
        ])),
        url(r'add/$', views.kit_add, name='kit_add'),
    ])),
]
