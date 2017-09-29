from django.contrib.auth.backends import ModelBackend
import rest_framework_jwt.authentication
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
            return Kit.objects.get(pk=user.pk)
        except:
            pass

        try:
            return PersonUser.objects.get(pk=user.pk)
        except:
            pass

        return user

class JWTBackend(object):
    def authenticate(self, request):
        print("Trying...")
        jwt_auth = rest_framework_jwt.authentication.JSONWebTokenAuthentication()
        try:
            (user, jwt_value) = jwt_auth.authenticate(request)
            return self.downcast_user_type(user)
        except:
            return None

    def get_user(self, *args, **kwargs):
        return self.downcast_user_type(super().get_user(*args, **kwargs))

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
