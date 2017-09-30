from channels.routing import route_class
from channels.generic.websockets import WebsocketDemultiplexer
import backend.consumers

class APIDemultiplexer(WebsocketDemultiplexer):

    consumers = {
        'measurements': backend.consumers.MeasurementConsumer
    }

channel_routing = [
    route_class(APIDemultiplexer)
]
