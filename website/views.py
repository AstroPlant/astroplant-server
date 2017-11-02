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

    context = {'kit': kit, 'can_view_kit_dashboard': request.user.has_perm('backend.view_kit_dashboard', kit)}

    return render(request, 'website/kit.html', context)

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

@decorators.login_required
def sensor_definition_add(request):
    Form = django.forms.modelform_factory(backend.models.SensorDefinition,
                                          fields = ('name', 'description', 'public', 'brand', 'type', 'class_name',),
                                          help_texts = {
                                              'public': 'Should the sensor definition be available publicly?',
                                              'class_name': 'The Python class name of the sensor implementation.'
                                            })

    if request.method == 'POST':
        form = Form(request.POST)

        if not form.is_valid():
            return render(request,'website/sensor_definition_add.html', {'form': form})

        # Get the sensor definition object
        sensor_definition = form.save(commit=False)

        # Set the current user as the owner
        sensor_definition.owner = request.user

        sensor_definition.save()
        return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:sensor_definition_configure', kwargs={'sensor_definition_id': sensor_definition.pk}))
    else:
        form = Form()
        return render(request,'website/sensor_definition_add.html', {'form': form})

@decorators.login_required
def sensor_definition_configure(request, sensor_definition_id):
    """
    View to configure a Django sensor definition.
    """
    sensor_definition_query = backend.models.SensorDefinition.objects.filter(pk = sensor_definition_id, owner = request.user)

    if not sensor_definition_query:
        return render(request, 'website/sensor_definition_configure_not_found.html', {})

    sensor_definition = sensor_definition_query.first()

    SensorDefinitionForm = django.forms.modelform_factory(backend.models.SensorDefinition,
                                          fields = ('description', 'public', 'brand', 'type', 'class_name',),
                                          help_texts = {
                                              'public': 'Should the sensor definition be available publicly?',
                                              'class_name': 'The Python class name of the sensor implementation.'
                                            })
    SensorConfigurationDefinitionFormSet = django.forms.inlineformset_factory(backend.models.SensorDefinition, backend.models.SensorConfigurationDefinition, exclude=[])

    if request.method == 'POST':
        form = SensorDefinitionForm(request.POST, instance=sensor_definition)
        form_set = SensorConfigurationDefinitionFormSet(request.POST, instance=sensor_definition)

        if not form.is_valid() or not form_set.is_valid():
            return render(request,'website/sensor_definition_configure.html', {'sensor_definition': sensor_definition, 'form': form, 'form_set': form_set})

        # Save the sensor definition
        form.save()

        # Save the sensor configuration definitions
        form_set.save()

        # Generate a new form set
        form_set = SensorConfigurationDefinitionFormSet(instance=sensor_definition)
        return render(request, 'website/sensor_definition_configure.html', {'sensor_definition': sensor_definition, 'form': form, 'form_set': form_set})
    else:
        form = SensorDefinitionForm(instance=sensor_definition)
        form_set = SensorConfigurationDefinitionFormSet(instance=sensor_definition)
        return render(request, 'website/sensor_definition_configure.html', {'sensor_definition': sensor_definition, 'form': form, 'form_set': form_set})

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
