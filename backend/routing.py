from channels.routing import route_class
from channels.generic.websockets import WebsocketDemultiplexer
import backend.consumers

class APIDemultiplexer(WebsocketDemultiplexer):

    # Give access to the Django user (through self.message.user in consumers)
    http_user_and_session = True

    consumers = {
        'measurements': backend.consumers.MeasurementConsumer
    }

channel_routing = [
    route_class(APIDemultiplexer)
]
