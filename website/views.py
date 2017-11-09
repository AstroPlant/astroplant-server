import datetime
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.core import exceptions
from django.contrib.auth import login, decorators
from django.contrib.auth import views as auth_views
from django.db.models import Q
import django.http
import django.urls.base
from braces.views import AnonymousRequiredMixin, LoginRequiredMixin
from registration.backends.hmac import views as registration_views
from dal import autocomplete

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
def kit_configure_profile(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')
   
    Form = django.forms.modelform_factory(backend.models.Kit,
                                          fields = ('name', 'description', 'privacy_show_on_map', 'privacy_public_dashboard',),
                                          help_texts = {
                                              'privacy_show_on_map': 'May the kit be displayed on the public map?',
                                              'privacy_public_dashboard': 'Should the kit\'s dashboard be public?',
                                          },
                                          labels = {
                                              'privacy_show_on_map': 'Show on map',
                                              'privacy_public_dashboard': 'Public dashboard',
                                          })

    if request.method == 'POST':
        form = Form(request.POST, instance=kit)

        if form.is_valid():
            form.save()
    else:
        form = Form(instance=kit)

    return render(request,'website/kit_configure_profile.html', {'kit': kit, 'form': form})

@decorators.login_required
def kit_configure_members(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    Form = django.forms.modelform_factory(backend.models.KitMembership,
                                        fields = ('user',),
                                        labels = {'user': 'Add another user to %s' % kit.name},
                                        widgets = {'user': autocomplete.Select2(url='website:autocomplete-users', attrs={'data-html': True})})

    if request.method == 'POST':
        if request.POST.get('remove_user'):
            user_to_remove = request.POST.get('remove_user')
            membership = kit.memberships.filter(user=user_to_remove).first()
            if membership:
                membership.delete()
                messages.add_message(request, messages.SUCCESS, 'The user has been removed.')
            else: 
                messages.add_message(request, messages.ERROR, 'The user could not be found.')
        elif request.POST.get('add_user'):
            form = Form(request.POST)
            
            if form.is_valid():
                membership = form.save(commit = False)

                existing_membership = kit.memberships.filter(user=membership.user)
                if existing_membership:
                    messages.add_message(request, messages.ERROR, 'That user already is a member.')
                else:
                    membership.kit = kit
                    membership.save()
                    messages.add_message(request, messages.SUCCESS, 'The user has been added.')

    form = Form()
    
    memberships = kit.memberships.all()
    context = {'kit': kit, 'memberships': memberships, 'form': form}
    return render(request, 'website/kit_configure_members.html', context)

@decorators.login_required
def kit_configure_location(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    Form = django.forms.modelform_factory(backend.models.Kit,
                                          fields = ('latitude', 'longitude',))

    form = Form(instance=kit)

    if request.method == 'POST':
        form = Form(request.POST, instance=kit)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'The kit\'s location has been saved.')
        else:
            messages.add_message(request, messages.ERROR, 'An error occurred while attempting to save the kit\'s location.')


    context = {'kit': kit, 'form': form}
    return render(request, 'website/kit_configure_location.html', context)

@decorators.login_required
def kit_configure_sensors(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    if request.method == 'POST':
        sensor_to_remove = request.POST.get('remove_sensor')
        sensor = kit.sensors.filter(id=sensor_to_remove).first()
        if sensor:
            sensor.active = False;
            sensor.date_time_removed = datetime.datetime.now()
            sensor.save()
            messages.add_message(request, messages.SUCCESS, 'The sensor has been removed.')
        else: 
            messages.add_message(request, messages.ERROR, 'The sensor could not be found.')

    context = {'kit': kit,
               'active_sensors': kit.sensors.filter(active=True),
               'inactive_sensors': kit.sensors.filter(active=False),
    }

    return render(request, 'website/kit_configure_sensors.html', context)

@decorators.login_required
def kit_configure_sensors_add(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    Form = django.forms.modelform_factory(backend.models.Sensor,
                                          fields = ('sensor_definition',),)

    if request.method == 'POST':
        form = Form(request.POST)

        if form.is_valid():
            sensor = form.save(commit=False)
            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_sensors_add_step2', kwargs={
                                                                                 'kit_id': kit.pk,
                                                                                 'sensor_definition_id': sensor.sensor_definition.pk,
                                                                             }))
    else:
        form = Form()

    context = {'kit': kit, 'form': form}

    return render(request, 'website/kit_configure_sensors_add.html', context)

@decorators.login_required
def kit_configure_sensors_add_step2(request, kit_id, sensor_definition_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    

    try:
        sensor_definition = backend.models.SensorDefinition.objects.get(pk=sensor_definition_id)
    except exceptions.ObjectDoesNotExist:
        sensor_definition = None

    if not sensor_definition or not request.user.has_perm('backend.assign_sensor_definition', sensor_definition):
        messages.add_message(request, messages.ERROR, 'That sensor was not found or you do not have permission to access it.')
        return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_sensors_add', kwargs={
                                                                                 'kit_id': kit.pk,
                                                                             }))

    # Form definition for the sensor instantiation itself
    SensorForm = django.forms.modelform_factory(backend.models.Sensor,
                                          fields = ('name',),
                                          help_texts = {'name': 'The sensor name'})

    # Form definition for a configuration parameter of the sensor
    SensorConfigurationForm = django.forms.modelform_factory(backend.models.SensorConfiguration,
                                          fields = ('value',),
                                          help_texts = {'value': 'Leave blank for default'})

    # Form set definition for the configuration parameters of the sensor
    sensor_configuration_definitions = sensor_definition.sensor_configuration_definitions.all()

    SensorConfigurationFormSet = django.forms.formset_factory(SensorConfigurationForm, extra = 0)

    if request.method == 'POST':
        sensor_form = SensorForm(request.POST)
        sensor_configuration_form_set = SensorConfigurationFormSet(request.POST, initial = [{} for sensor_configuration_definition in sensor_configuration_definitions])

        if sensor_form.is_valid() and sensor_configuration_form_set.is_valid():
            sensor = sensor_form.save(commit=False)
            sensor.kit = kit
            sensor.sensor_definition = sensor_definition
            sensor.save()

            # Save all sensor configurations with a non-blank value
            for sensor_configuration_definition, sensor_configuration_form in zip(sensor_configuration_definitions, sensor_configuration_form_set.forms):
                sensor_configuration = sensor_configuration_form.save(commit=False)
                sensor_configuration.sensor = sensor
                sensor_configuration.sensor_configuration_definition = sensor_configuration_definition
                if sensor_configuration.value:
                    sensor_configuration.save()

            messages.add_message(request, messages.SUCCESS, 'The sensor has been added.')
            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_sensors', kwargs={
                                                                                 'kit_id': kit.pk,
                                                                             }))
    else:
        sensor_form = SensorForm()
        sensor_configuration_form_set = SensorConfigurationFormSet(initial = [{'sensor_configuration_definition': sensor_configuration_definition} for sensor_configuration_definition in sensor_configuration_definitions])

    context = {
        'kit': kit,
        'sensor_definition': sensor_definition,
        'sensor_form': sensor_form,
        'sensor_configuration_form_set': sensor_configuration_form_set
    }
    return render(request, 'website/kit_configure_sensors_add_step2.html', context)

@decorators.login_required
def kit_configure_access(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    if request.method == 'POST':
        secret = backend.models.Kit.generate_password()

        kit.set_password(secret)
        kit.save()

        messages.add_message(request, messages.SUCCESS, 'A new secret has been generated: %s' % secret)
    else:
        secret = None

    return render(request, 'website/kit_configure_access.html', {'kit': kit, 'secret': secret})

@decorators.login_required
def kit_configure_danger_zone(request, kit_id):
    try:
        kit = backend.models.Kit.objects.get(pk=kit_id)
    except exceptions.ObjectDoesNotExist:
        kit = None

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    Form = django.forms.modelform_factory(backend.models.Kit,
                                          fields = ('name',),
                                          help_texts = {'name': 'Write the name of the kit ("%s") to confirm.' % kit.name},
                                          widgets = {'name': django.forms.TextInput(attrs={'autocomplete': 'off'})},)
    if request.method == 'POST':
        form = Form(request.POST)

        if form.is_valid():
            kit_ = form.save(commit=False)
            if kit_.name == kit.name:
                if request.POST.get('action') == "remove_measurements":
                    kit.measurement_set.all().delete()
                    messages.add_message(request, messages.SUCCESS, 'All measurements have been removed from the kit.')
                elif request.POST.get('action') == "remove_kit":
                    kit.delete()
                    messages.add_message(request, messages.SUCCESS, 'The kit has been removed.')
                    return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:dashboard'))
                else: 
                    messages.add_message(request, messages.ERROR, 'An error occured. Please try again.')
            else:
                messages.add_message(request, messages.ERROR, 'The kit name entered is incorrect. Note that the name is case sensitive.')
                                         
    form = Form()
    
    return render(request, 'website/kit_configure_danger_zone.html', {'kit': kit, 'form': form})

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
            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_access', kwargs={'kit_id': kit.pk}))
    else:
        form = website.forms.AddKitForm()
        return render(request,'website/kit_add.html', {'form': form})

def sensor_definition_list(request):
    sensor_definitions = backend.models.SensorDefinition.objects.all()
    return render(request,'website/sensor_definition_list.html', {'sensor_definitions': sensor_definitions})

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
    sensor_definition_query = backend.models.SensorDefinition.objects.filter(pk = sensor_definition_id)

    if not sensor_definition_query:
        return render(request, 'website/sensor_definition_configure_not_found.html', {})

    sensor_definition = sensor_definition_query.first()

    if not request.user.has_perm('backend.edit_sensor_definition', sensor_definition):
        return render(request, 'website/sensor_definition_configure_not_found.html', {})

    SensorDefinitionForm = django.forms.modelform_factory(backend.models.SensorDefinition,
                                          fields = ('description', 'public', 'brand', 'type', 'class_name', 'measurement_types',),
                                          help_texts = {
                                              'public': 'Should the sensor definition be available publicly?',
                                              'class_name': 'The Python class name of the sensor implementation.',
                                              'measurement_types': 'The measurement types to plot on the dashboard (other measurement types are supported, but will not be plotted).'
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
