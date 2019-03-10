import urllib.parse
from django.contrib import auth
from django.db import close_old_connections
from channels.middleware import BaseMiddleware

import rest_framework_jwt.serializers
import rest_framework.exceptions
import jwt.exceptions

import backend.auth

class TokenMiddleware(object):
    """
    Middleware that authenticates against a token in the http authorization header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', b'').split()
        print("asd")
        if not auth_header:
            return None

        user = auth.authenticate()
        if user:
            request.user = user

class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate a user with a JSON Web Token.
    """

    def populate_scope(self, scope):
        # Populate top level of scope.
        if "user" not in scope:
            raise ValueError(
                "JWTAuthMiddleware cannot find user in scope. AuthMiddleware must be above it."
            )

    async def resolve_scope(self, scope):
        if not scope["user"]._wrapped.is_anonymous:
            return

        if not "query_string" in scope:
            return

        qs = urllib.parse.parse_qs(scope['query_string'].decode('utf-8'))
        
        user = None
        try:
            qs['token'] = qs['token'][0]

            validated = rest_framework_jwt.serializers.VerifyJSONWebTokenSerializer().validate(qs)

            # If no exception is thrown, the token is valid. Store it in the session if it is a kit.
            user = backend.auth.downcast_user_type(validated['user'])
        except (KeyError, jwt.exceptions.InvalidTokenError, rest_framework.exceptions.ValidationError):
            pass

        close_old_connections()

        # Set the user.
        if user:
            scope["user"]._wrapped = user
