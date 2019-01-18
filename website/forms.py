import django.forms
from registration.forms import RegistrationForm
import backend.models

class PersonUserRegistrationForm(RegistrationForm):
    tos = django.forms.BooleanField(
        # widget=django.forms.CheckboxInput,
        label='I have read and agree to the <a href="/tos/">Terms of Service</a>.',
        error_messages={
            'required': 'You must agree to the Terms of Service to register',
        },
        required=True
    )

    class Meta:
        model = backend.models.PersonUser
        fields = ('username', 'email',)

class AddKitForm(django.forms.ModelForm):
    class Meta:
        model = backend.models.Kit
        fields = ('name',)

class AddPeripheralDefinitionForm(django.forms.ModelForm):
    class Meta:
        model = backend.models.PeripheralDefinition
        fields = ('name', 'description', 'verified', 'public', 'owner', 'brand', 'type', 'class_name',)
