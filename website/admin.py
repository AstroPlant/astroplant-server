from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from backend import models

# Implement custom forms for Kit creation and changing
# See: https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#a-full-example
class KitCreationForm(forms.ModelForm):
    """
    A form for creating new kits.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.Kit
        fields = ('serial', 'type', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        kit = super(KitCreationForm, self).save(commit=False)
        kit.set_password(self.cleaned_data["password1"])
        if commit:
            kit.save()
        return kit

class KitChangeForm(forms.ModelForm):
    """
    A form for updating kits. Includes all the fields on
    the kit, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.Kit
        fields = ('serial', 'password', 'type', 'name', 'description', 'latitude', 'longitude')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class KitAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = KitChangeForm
    add_form = KitCreationForm

    # The fields to be used in displaying the Kit model.
    # These override the definitions on the base KitAdmin
    # that reference specific fields on auth.User.
    list_display = ('serial', 'type', 'name')
    list_filter = ('type',)
    fieldsets = (
        (None, {'fields': ('serial', 'password')}),
        ('Info', {'fields': ('type', 'name', 'description',)}),
        ('Location', {'fields': ('latitude', 'longitude',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. KitAdmin
    # overrides get_fieldsets to use this attribute when creating a kit.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'date_of_birth', 'password1', 'password2')}
        ),
    )
    search_fields = ('serial', 'type', 'name',)
    ordering = ('serial', 'type', 'name',)
    filter_horizontal = ()

admin.site.register(models.Kit, KitAdmin)

@admin.register(models.KitMembership)
class KitMembershipAdmin(admin.ModelAdmin):
    list_display = ('kit', 'user', 'date_time_linked')
    ordering = ('kit', 'user')

@admin.register(models.SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'type', 'unit')
    ordering = ('brand', 'type')

@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('type', 'kit')
    ordering = ('type', 'kit')

@admin.register(models.Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('kit', 'date_time_start', 'date_time_end')
    ordering = ('kit', 'date_time_start', 'date_time_end')

@admin.register(models.Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'kit', 'experiment', 'date_time', 'value')
    ordering = ('sensor_type', 'date_time')
