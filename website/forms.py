import django.forms
from registration.forms import RegistrationForm
import backend.models

class PersonUserRegistrationForm(RegistrationForm):
    class Meta:
        model = backend.models.PersonUser
        fields = ('username', 'email',)

class AddKitForm(django.forms.ModelForm):
    class Meta:
        model = backend.models.Kit
        fields = ('name',)

class AddSensorDefinitionForm(django.forms.ModelForm):
    class Meta:
        model = backend.models.SensorDefinition
        fields = ('name', 'description', 'verified', 'public', 'owner', 'brand', 'type', 'class_name',)
