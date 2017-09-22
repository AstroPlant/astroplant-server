from backend.models import Kit

class KitBackend(object):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Check a kit serial and password.
        """

        if username is None:
            return None

        try:
            kit = Kit._default_manager.get_by_natural_key(username)
        except Kit.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            Kit().set_password(password)
        else:
            if kit.check_password(password):
                return kit

    def get_user(self, user_id):
        try:
            kit = Kit._default_manager.get(pk=user_id)
        except Kit.DoesNotExist:
            return None
        return kit
