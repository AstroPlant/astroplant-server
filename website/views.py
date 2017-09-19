from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.core import exceptions
from django.contrib.auth import login, decorators
from django.contrib.auth import views as auth_views
from braces.views import AnonymousRequiredMixin, LoginRequiredMixin
from registration.backends.hmac import views as registration_views

import backend.models

def index(request):
    context = {}
    return render(request, 'website/index.html', context)
    
def map(request):
    # Note that we don't use GeoDjango; it requires a heavy gdal setup. All
    # we need is a simple map, and a full gdal setup would just make deployment
    # more difficult
    context = {'kits': backend.models.Kit.objects.all()}

    return render(request,'website/map.html', context)
       
@decorators.login_required
def dashboard(request):
    context = {'kits': backend.models.Kit.objects.filter(users=request.user)}

    return render(request,'website/dashboard.html', context)

def kit(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    try:
        membership = backend.models.KitMembership.objects.get(user=request.user, kit=kit)
    except exceptions.ObjectDoesNotExist:
        membership = None

    context = {'kit': kit, 'membership': membership}

    return render(request,'website/kit.html', context)

class LoginView(AnonymousRequiredMixin, auth_views.LoginView):
    authenticated_redirect_url = reverse_lazy(u'website:dashboard')

class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    login_url = reverse_lazy(u'auth_login')
    redirect_field_name = 'redirect_to'
    
class ActivationView(registration_views.ActivationView):
    def get_success_url(self, user):
        # Log the user in
        login(self.request, user)

        # Set a message
        messages.add_message(self.request, messages.SUCCESS, 'Your account has been activated!')
        return ('website:dashboard', (), {})
