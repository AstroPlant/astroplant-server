"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from website.views import LoginView, LogoutView, ActivationView

urlpatterns = [
    url(r'^', include('website.urls', namespace='website')),
    url(r'^admin/', admin.site.urls),
    # Overwrite some views defined by the registration plugin; 
    # e.g. logged in users should not be able to log in again
    url(r'^accounts/login/', LoginView.as_view()),
    url(r'^accounts/logout/', LogoutView.as_view()),
    url(r'^accounts/activate/(?P<activation_key>[-:\w]+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
