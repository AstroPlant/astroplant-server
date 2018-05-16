from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import backend.middleware
import backend.consumers

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(backend.middleware.JWTAuthMiddleware(
        URLRouter([
            url(r"^measurements/subscribe/(?P<kit_name>[\.a-z0-9]+)/$", backend.consumers.MeasurementSubscribeConsumer),
            url(r"^kit/$", backend.consumers.KitConsumer),
        ])
    )),
})
