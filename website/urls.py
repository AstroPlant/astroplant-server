from django.conf.urls import include, url
from . import views
from . import autocomplete

import backend

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/$', views.map, name='map'),
    url(r'^dashboard/', include([
        url(r'^$', views.dashboard, name='dashboard'),
        url(r'^add/$', views.kit_add, name='kit_add'),
        url(r'^(?P<kit_id>[0-9]+)/', include([
            url(r'^$', views.kit, name='kit'),
            url(r'^download/$', views.kit_download, name='kit_download'),
            url(r'^configure/', include([
                 url(r'^profile/$', views.kit_configure_profile, name='kit_configure_profile'),
                 url(r'^members/$', views.kit_configure_members, name='kit_configure_members'),
                 url(r'^location/$', views.kit_configure_location, name='kit_configure_location'),
                 url(r'^peripherals/$', views.kit_configure_peripherals, name='kit_configure_peripherals'),
                 url(r'^peripherals/add/$', views.kit_configure_peripherals_add, name='kit_configure_peripherals_add'),
                 url(r'^peripherals/add/(?P<peripheral_definition_id>[0-9]+)/$', views.kit_configure_peripherals_add_step2, name='kit_configure_peripherals_add_step2'),
                 url(r'^access/$', views.kit_configure_access, name='kit_configure_access'),
                 url(r'^danger/$', views.kit_configure_danger_zone, name='kit_configure_danger_zone'),
            ])),
        ])),
    ])),
    url(r'^peripherals/', include([
        url(r'^$', views.peripheral_definition_list, name='peripheral_definition_list'),
        url(r'^add/$', views.peripheral_definition_add, name='peripheral_definition_add'),
        url(r'^(?P<peripheral_definition_id>[0-9]+)/', include([
            url(r'^configure/$', views.peripheral_definition_configure, name='peripheral_definition_configure'),
        ])),
    ])),
    url(r'^autocomplete/', include([
        url(r'^users/$', autocomplete.PersonUserAutocomplete.as_view(), name='autocomplete-users'),
    ])),
]
