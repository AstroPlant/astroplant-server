from channels.routing import route_class
from channels.generic.websockets import WebsocketDemultiplexer
from backend.bindings import MeasurementBinding

class APIDemultiplexer(WebsocketDemultiplexer):

    consumers = {
      'measurements': MeasurementBinding.consumer
    }

channel_routing = [
    route_class(APIDemultiplexer)
]
