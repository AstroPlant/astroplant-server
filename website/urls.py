from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/$', views.map, name='map'),
    url(r'^login/$', views.login.as_view(), name='login'),
    url(r'^logout/$', views.logout.as_view(template_name='registration/logout.html'), name='logout'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
]
