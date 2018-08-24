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
    context = {'kits': backend.models.Kit.kits.shown_on_map()}

    return render(request,'website/map.html', context)


@decorators.login_required
def dashboard(request):
    context = {'kits': backend.models.Kit.kits.owned_by(user=request.user)}

    return render(request,'website/dashboard.html', context)


def kit(request, kit_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

    context = {
        'kit': kit,
        'can_view_kit_dashboard': request.user.has_perm('backend.view_kit_dashboard', kit)
    }
    # Catch for kit not existing at all
    if kit:
       context['recent_measurements'] = kit.recent_measurements(max_measurements=50)

    return render(request, 'website/kit.html', context)


def kit_download(request, kit_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

    context = {'kit': kit,
               'can_view_kit_dashboard': request.user.has_perm('backend.view_kit_dashboard', kit),
               'recent_measurements': kit.recent_measurements(max_measurements=50)}
    
    if context['can_view_kit_dashboard']:
        import zipfile
        import csv
        from io import StringIO
        
        response = django.http.HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="kit_' + str(kit.pk) + '.zip"'
        
        def write_to_csv(zip, filename, queryset):
            buffer = StringIO()
            n = 0
            for model_values in queryset:
                if n == 0:
                    writer = csv.DictWriter(buffer, model_values.keys())
                    writer.writeheader()
                    writer.writerow(model_values)
                else:
                    writer.writerow(model_values)
                
                n += 1
            
            zip.writestr(filename, buffer.getvalue())
        
        with zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED) as zip:
            
            buffer = StringIO()
            writer = csv.writer(buffer)
            writer.writerow(['name', 'value'])
            for (key, val) in kit.__dict__.items():
                if key not in ['type', 'longitude', 'latitude', 'name', 'description', 'id']:
                    continue
                    
                writer.writerow([key, val])
            zip.writestr("kit.csv", buffer.getvalue())
            
            write_to_csv(zip, "measurements.csv", kit.measurements.all().values())
            write_to_csv(zip, "peripherals.csv", kit.peripherals.all().values())
            write_to_csv(zip, "peripheral_definitions.csv", backend.models.PeripheralDefinition.objects.filter(peripheral__in=kit.peripherals.all()).all().values())
            
            peripheral_definitions = []
            for peripheral in kit.peripherals.all():
            
                # Write peripheral definition
                peripheral_definition = peripheral.peripheral_definition
                if peripheral_definition.pk not in peripheral_definitions:
                    peripheral_definitions.append(peripheral_definition.pk)
                    
                    # Write peripheral definition configuration
                    write_to_csv(zip, "peripheral_definition_%s_configuration.csv" % peripheral_definition.pk, peripheral_definition.peripheral_configuration_definitions.all().values())
                
                # Write peripheral configuration
                write_to_csv(zip, "peripheral_%s_configuration.csv" % peripheral.pk, peripheral.peripheral_configurations.all().values())
            
        return response
    else:
        return django.http.HttpResponseForbidden("No access")
    
    
    
@decorators.login_required
def kit_configure_profile(request, kit_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

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
    kit = backend.models.Kit.kits.safe_get(kit_id)

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
    kit = backend.models.Kit.kits.safe_get(kit_id)

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
def kit_configure_peripherals(request, kit_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    if request.method == 'POST':
        if request.POST.get('deactivate_peripheral'):
            peripheral_id = request.POST.get('deactivate_peripheral')
            peripheral = kit.peripherals.filter(id=peripheral_id, active=True).first()
            if peripheral:
                peripheral.active = False;
                peripheral.save()
                messages.add_message(request, messages.SUCCESS, 'The peripheral has been deactivated.')
            else: 
                messages.add_message(request, messages.ERROR, 'The peripheral could not be found.')
        elif request.POST.get('activate_peripheral'):
            peripheral_id = request.POST.get('activate_peripheral')
            peripheral = kit.peripherals.filter(id=peripheral_id, active=False).first()
            if peripheral:
                peripheral.active = True;
                peripheral.save()
                messages.add_message(request, messages.SUCCESS, 'The peripheral has been activated.')
            else: 
                messages.add_message(request, messages.ERROR, 'The peripheral could not be found.')
        elif request.POST.get('permanently_remove_peripheral'):
            peripheral_id = request.POST.get('permanently_remove_peripheral')
            peripheral = kit.peripherals.filter(id=peripheral_id, active=False).first()
            if peripheral:
                peripheral.delete()
                messages.add_message(request, messages.SUCCESS, 'The peripheral has been removed.')
            else: 
                messages.add_message(request, messages.ERROR, 'The peripheral could not be found.')

    context = {'kit': kit,
               'active_peripherals': kit.peripherals.filter(active=True),
               'inactive_peripherals': kit.peripherals.filter(active=False),
    }

    return render(request, 'website/kit_configure_peripherals.html', context)

@decorators.login_required
def kit_configure_peripherals_add(request, kit_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    Form = django.forms.modelform_factory(backend.models.Peripheral,
                                          fields = ('peripheral_definition',),
                                          labels = {'peripheral_definition': 'Peripheral device definition',})

    if request.method == 'POST':
        form = Form(request.POST)

        if form.is_valid():
            peripheral = form.save(commit=False)
            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_peripherals_add_step2', kwargs={
                                                                                 'kit_id': kit.pk,
                                                                                 'peripheral_definition_id': peripheral.peripheral_definition.pk,
                                                                             }))
    else:
        form = Form()

    context = {'kit': kit, 'form': form}

    return render(request, 'website/kit_configure_peripherals_add.html', context)

@decorators.login_required
def kit_configure_peripherals_add_step2(request, kit_id, peripheral_definition_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

    if not kit or not request.user.has_perm('backend.configure_kit', kit):
        return render(request, 'website/kit_configure_not_found.html')

    

    try:
        peripheral_definition = backend.models.PeripheralDefinition.objects.get(pk=peripheral_definition_id)
    except exceptions.ObjectDoesNotExist:
        peripheral_definition = None

    if not peripheral_definition or not request.user.has_perm('backend.assign_peripheral_definition', peripheral_definition):
        messages.add_message(request, messages.ERROR, 'That peripheral device was not found or you do not have permission to access it.')
        return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_peripherals_add', kwargs={
                                                                                 'kit_id': kit.pk,
                                                                             }))

    # Form definition for the peripheral device instantiation itself
    PeripheralForm = django.forms.modelform_factory(backend.models.Peripheral,
                                          fields = ('name',),
                                          help_texts = {'name': 'The peripheral device name'})

    # Form definition for a configuration parameter of the peripheral device
    PeripheralConfigurationForm = django.forms.modelform_factory(backend.models.PeripheralConfiguration,
                                          fields = ('value',),
                                          help_texts = {'value': 'Leave blank for default'})

    # Form set definition for the configuration parameters of the peripheral device
    peripheral_configuration_definitions = peripheral_definition.peripheral_configuration_definitions.all()

    PeripheralConfigurationFormSet = django.forms.formset_factory(PeripheralConfigurationForm, extra = 0)

    if request.method == 'POST':
        peripheral_form = PeripheralForm(request.POST)
        peripheral_configuration_form_set = PeripheralConfigurationFormSet(request.POST, initial = [{} for peripheral_configuration_definition in peripheral_configuration_definitions])

        if peripheral_form.is_valid() and peripheral_configuration_form_set.is_valid():
            peripheral = peripheral_form.save(commit=False)
            peripheral.kit = kit
            peripheral.peripheral_definition = peripheral_definition
            peripheral.save()

            # Save all peripheral device configurations with a non-blank value
            for peripheral_configuration_definition, peripheral_configuration_form in zip(peripheral_configuration_definitions, peripheral_configuration_form_set.forms):
                peripheral_configuration = peripheral_configuration_form.save(commit=False)
                peripheral_configuration.peripheral = peripheral
                peripheral_configuration.peripheral_configuration_definition = peripheral_configuration_definition
                if peripheral_configuration.value:
                    peripheral_configuration.save()

            messages.add_message(request, messages.SUCCESS, 'The peripheral device has been added.')
            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_peripherals', kwargs={
                                                                                 'kit_id': kit.pk,
                                                                             }))
    else:
        peripheral_form = PeripheralForm()
        peripheral_configuration_form_set = PeripheralConfigurationFormSet(initial = [{'peripheral_configuration_definition': peripheral_configuration_definition} for peripheral_configuration_definition in peripheral_configuration_definitions])

    context = {
        'kit': kit,
        'peripheral_definition': peripheral_definition,
        'peripheral_form': peripheral_form,
        'peripheral_configuration_form_set': peripheral_configuration_form_set
    }
    return render(request, 'website/kit_configure_peripherals_add_step2.html', context)

@decorators.login_required
def kit_configure_access(request, kit_id):
    kit = backend.models.Kit.kits.safe_get(kit_id)

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
    kit = backend.models.Kit.kits.safe_get(kit_id)

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
                    kit.measurements.all().delete()
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

            # Add kit membership
            kit_membership = backend.models.KitMembership(user = request.user, kit = kit)
            kit_membership.save()

            return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:kit_configure_access', kwargs={'kit_id': kit.pk}))
    else:
        form = website.forms.AddKitForm()
        return render(request,'website/kit_add.html', {'form': form})

def peripheral_definition_list(request):
    peripheral_definitions = backend.models.PeripheralDefinition.objects.all()
    return render(request,'website/peripheral_definition_list.html', {'peripheral_definitions': peripheral_definitions})

@decorators.login_required
def peripheral_definition_add(request):
    Form = django.forms.modelform_factory(backend.models.PeripheralDefinition,
                                          fields = ('name', 'description', 'public', 'brand', 'type', 'module_name', 'class_name',),
                                          help_texts = {
                                              'public': 'Should the peripheral device definition be available publicly?',
                                              'class_name': 'The Python class name of the peripheral device implementation.'
                                            })

    if request.method == 'POST':
        form = Form(request.POST)

        if not form.is_valid():
            return render(request,'website/peripheral_definition_add.html', {'form': form})

        # Get the peripheral device definition object
        peripheral_definition = form.save(commit=False)

        # Set the current user as the owner
        peripheral_definition.owner = request.user

        peripheral_definition.save()
        return django.http.HttpResponseRedirect(django.urls.base.reverse(viewname='website:peripheral_definition_configure', kwargs={'peripheral_definition_id': peripheral_definition.pk}))
    else:
        form = Form()
        return render(request,'website/peripheral_definition_add.html', {'form': form})

@decorators.login_required
def peripheral_definition_configure(request, peripheral_definition_id):
    """
    View to configure a Django peripheral device definition.
    """
    peripheral_definition_query = backend.models.PeripheralDefinition.objects.filter(pk = peripheral_definition_id)

    if not peripheral_definition_query:
        return render(request, 'website/peripheral_definition_configure_not_found.html', {})

    peripheral_definition = peripheral_definition_query.first()

    if not request.user.has_perm('backend.edit_peripheral_definition', peripheral_definition):
        return render(request, 'website/peripheral_definition_configure_not_found.html', {})

    PeripheralDefinitionForm = django.forms.modelform_factory(backend.models.PeripheralDefinition,
                                          fields = ('description', 'public', 'brand', 'type', 'module_name', 'class_name', 'quantity_types',),
                                          help_texts = {
                                              'public': 'Should the peripheral device definition be available publicly?',
                                              'module_name': 'The name of the Python module the peripheral device is implemented in.',
                                              'class_name': 'The Python class name of the peripheral device implementation.',
                                              'quantity_types': 'The measurement quantity types to plot on the dashboard (other types are supported, but will not be plotted).'
                                            })
    PeripheralConfigurationDefinitionFormSet = django.forms.inlineformset_factory(backend.models.PeripheralDefinition, backend.models.PeripheralConfigurationDefinition, exclude=[])

    if request.method == 'POST':
        form = PeripheralDefinitionForm(request.POST, instance=peripheral_definition)
        form_set = PeripheralConfigurationDefinitionFormSet(request.POST, instance=peripheral_definition)

        if not form.is_valid() or not form_set.is_valid():
            return render(request,'website/peripheral_definition_configure.html', {'peripheral_definition': peripheral_definition, 'form': form, 'form_set': form_set})

        # Save the peripheral device definition
        form.save()

        # Save the peripheral device configuration definitions
        form_set.save()

        # Generate a new form set
        form_set = PeripheralConfigurationDefinitionFormSet(instance=peripheral_definition)
        return render(request, 'website/peripheral_definition_configure.html', {'peripheral_definition': peripheral_definition, 'form': form, 'form_set': form_set})
    else:
        form = PeripheralDefinitionForm(instance=peripheral_definition)
        form_set = PeripheralConfigurationDefinitionFormSet(instance=peripheral_definition)
        return render(request, 'website/peripheral_definition_configure.html', {'peripheral_definition': peripheral_definition, 'form': form, 'form_set': form_set})

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
