from registration.forms import RegistrationForm
from backend.models import PersonUser

class PersonUserRegistrationForm(RegistrationForm):
    class Meta:
        model = PersonUser
        fields = ('username', 'email',)
