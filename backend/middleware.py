from django.contrib import auth

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
