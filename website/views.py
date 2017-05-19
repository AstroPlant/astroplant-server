from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from braces.views import AnonymousRequiredMixin, LoginRequiredMixin
from registration import views as registration_views

def index(request):
    context = {}
    return render(request, 'website/index.html', context)
    
def map(request):
    # Todo: programmatically add the markers of the AstroPlant kits.
    # Note that we don't use GeoDjango; it requires a heavy gdal setup. All
    # we need is a simple map, and a full gdal setup would just make deployment
    # more difficult
    context = {}
    messages.add_message(request, messages.ERROR, 'The map has not been implemented yet.')
    return render(request,'website/map.html', context)
        
def dashboard(request):
    pass

class LoginView(AnonymousRequiredMixin, auth_views.LoginView):
    authenticated_redirect_url = reverse_lazy(u'website:dashboard')

class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    login_url = reverse_lazy(u'website:login')
    redirect_field_name = 'redirect_to'
