from django.conf.urls import include, url

urlpatterns = [
    url(r'^channels-api/', include('channels_api.urls'))
]
