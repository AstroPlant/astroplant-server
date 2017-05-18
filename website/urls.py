from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map$', views.map, name='map'),
    url(r'^accounts/', include('registration.backends.hmac.urls', namespace='accounts')),
]
