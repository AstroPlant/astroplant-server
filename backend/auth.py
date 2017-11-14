from django.contrib.auth.backends import ModelBackend
import rest_framework_jwt.authentication
from backend.models import Kit, PersonUser

def downcast_user_type(user):
    try:
        return Kit.objects.get(pk=user.pk)
    except:
        pass

    try:
        return PersonUser.objects.get(pk=user.pk)
    except:
        pass

    return user

class PersonOrKitBackend(ModelBackend):
    """
    Backend using ModelBackend, but attempts to "downcast"
    the user into a PersonUser or KitUser.
    """

    def authenticate(self, *args, **kwargs):
        return downcast_user_type(super().authenticate(*args, **kwargs))
        
    def get_user(self, *args, **kwargs):
        return downcast_user_type(super().get_user(*args, **kwargs))

    def downcast_user_type(self, user):
        try:
            return Kit.objects.get(pk=user.pk)
        except:
            pass

        try:
            return PersonUser.objects.get(pk=user.pk)
        except:
            pass

        return user

class JSONWebTokenAuthentication(rest_framework_jwt.authentication.JSONWebTokenAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if not result:
            return result
        
        (user, token,) = result
        user = downcast_user_type(user)
        return (user, token,)
