from channels.routing import route_class
from channels.generic.websockets import WebsocketDemultiplexer
import backend.consumers

class APIDemultiplexer(WebsocketDemultiplexer):

    consumers = {
        'measurements-subscribe': backend.consumers.MeasurementSubscribeConsumer,
        'measurements-publish': backend.consumers.MeasurementPublishConsumer,
    }

channel_routing = [
    route_class(APIDemultiplexer)
]
