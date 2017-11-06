from django.template.loader import render_to_string
from dal import autocomplete

import backend.models
from . import templatetags
import django_gravatar.helpers

class PersonUserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = backend.models.PersonUser.objects.all()

        if self.q:
            qs = qs.filter(username__icontains=self.q)

        return qs

    def get_result_label(self, item):
        return render_to_string('website/fragments/person_user_choice.html', { 'user': item })
