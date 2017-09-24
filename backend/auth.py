from django.contrib.auth.backends import ModelBackend
from backend.models import Kit, PersonUser

class PersonOrKitBackend(ModelBackend):
    """
    Backend using ModelBackend, but attempts to "downcast"
    the user into a PersonUser or KitUser.
    """

    def authenticate(self, *args, **kwargs):
        return self.downcast_user_type(super().authenticate(*args, **kwargs))
        
    def get_user(self, *args, **kwargs):
        return self.downcast_user_type(super().get_user(*args, **kwargs))

    def downcast_user_type(self, user):
        try:
            kit = Kit.objects.get(pk=user.pk)
            return kit
        except:
            pass

        try:
            person_user = PersonUser.objects.get(pk=user.pk)
            return person_user
        except:
            pass

        return user
