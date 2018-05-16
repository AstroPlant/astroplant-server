import urllib.parse
from django.contrib import auth
from django.db import close_old_connections

import rest_framework_jwt.serializers
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

class JWTAuthMiddleware:
    """
    Middleware to authenticate a user with a JSON Web Token.
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        if "user" in scope and not scope["user"].is_anonymous:
            return self.inner(scope)

        if not "query_string" in scope:
            return self.inner(scope)

        qs = urllib.parse.parse_qs(scope['query_string'].decode('utf-8'))
        
        user = None
        try:
            qs['token'] = qs['token'][0]

            validated = rest_framework_jwt.serializers.VerifyJSONWebTokenSerializer().validate(qs)

            # If no exception is thrown, the token is valid. Store it in the session if it is a kit.
            user = backend.auth.downcast_user_type(validated['user'])
        except (KeyError, jwt.exceptions.InvalidTokenError):
            pass

        close_old_connections()

        # Return the inner application directly and let it run everything else
        if user:
            return self.inner(dict(scope, user=user))
        else:
            return self.inner(scope)
