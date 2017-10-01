from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.core import exceptions
from django.contrib.auth import login, decorators
from django.contrib.auth import views as auth_views
import django.http
import django.urls.base
from braces.views import AnonymousRequiredMixin, LoginRequiredMixin
from registration.backends.hmac import views as registration_views

import backend.models
import website.forms

def index(request):
    context = {}
    return render(request, 'website/index.html', context)
    
def map(request):
    # Note that we don't use GeoDjango; it requires a heavy gdal setup. All
    # we need is a simple map, and a full gdal setup would just make deployment
    # more difficult
    context = {'kits': backend.models.Kit.objects.filter(privacy_show_on_map=True)}

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

@decorators.login_required
def kit_add(request):
    #: The length of the kit identifier to be generated
    RANDOM_KIT_IDENTIFIER_LENGTH = 8

    if request.method == 'POST':
        form = website.forms.AddKitForm(request.POST)

        if form.is_valid():
            # Get the kit object
            kit = form.save(commit=False)

            # Generate a unique kit identifier (username/serial)
            import random
            while True:
                # Generate a unique identifier without vowels to minimize the chance 
                # of generating bad words :)
                # also 0, (o), 1, l, 2, z, 5, s are removed, as they look similar
                # Identifiers look like: "k.6g77mnyp"
                identifier = 'k.%s' % ''.join(random.choice('346789bcdfghjkmnpqrtvwxy') for i in range(RANDOM_KIT_IDENTIFIER_LENGTH))
                
                # Test if the random identifier already exists
                if len(backend.models.Kit.objects.filter(username=identifier)) == 0:
                    # If not, break the loop (generally happens immediately)
                    break

            kit.username = identifier
            kit.save()
            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit', kwargs={'kit_id': kit.pk}))
    else:
        form = website.forms.AddKitForm()
        return render(request,'website/kit_add.html', {'form': form})

class LoginView(AnonymousRequiredMixin, auth_views.LoginView):
    authenticated_redirect_url = reverse_lazy(u'website:dashboard')

class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    login_url = reverse_lazy(u'auth_login')
    redirect_field_name = 'redirect_to'
    
class ActivationView(registration_views.ActivationView):
    def get_success_url(self, user):
        # Log the user in
        login(self.request, user, backend='backend.auth.PersonOrKitBackend')

        # Set a message
        messages.add_message(self.request, messages.SUCCESS, 'Your account has been activated!')
        return ('website:dashboard', (), {})
