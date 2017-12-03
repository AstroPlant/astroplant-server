import channels
import channels.handler
import channels.generic.websockets

import rest_framework_jwt.serializers
import jwt.exceptions

import backend.models
import backend.serializers
import backend.auth

def jwt_auth(message):
    """
    Attempt to authenticate the user through a JWT provided in
    the 'token' query parameter.

    :param message: The channel message object
    :return: The authenticated user, or None
    """

    # Construct a fake http-like object
    # (See: https://stackoverflow.com/questions/46230340/how-to-authenticate-a-user-in-websocket-connection-in-django-channels-when-using)
    message.content.setdefault('method', 'FAKE')
    request = channels.handler.AsgiRequest(message)

    # Validate the token in the request in a slightly hacky way
    try:
        validated = rest_framework_jwt.serializers.VerifyJSONWebTokenSerializer().validate(request.GET)

        # If no exception is thrown, the token is valid. Store it in the session if it is a kit.
        return backend.auth.downcast_user_type(validated['user'])
    except (KeyError, jwt.exceptions.InvalidTokenError):
        return None

class JWTSessionAuthConsumer(channels.generic.websockets.JsonWebsocketConsumer):
    """
    A JSON WebSocket consumer that attempts to authenticate
    a kit using JWT through a HTTP query parameter. If successful,
    places the kit name in the channel session parameter 'kit'.
    """

    #: Use channel sessions, and transfer the HTTP user (from
    #: a Django session) to the channel session
    http_user_and_session = True

    def connect(self, message, **kwargs):
        user = jwt_auth(message)
        if isinstance(user, backend.models.Kit):
            self.message.channel_session['kit'] = user.username

        super().connect(message, **kwargs)

class MeasurementSubscribeConsumer(JWTSessionAuthConsumer):
    """
    A measurement subscribe consumer. Any user (or kit) can
    subscribe to measurements of kits they own.
    """
    def receive(self, content, multiplexer, **kwargs):
        # Subscribe user to kit measurement updates
        if "kit" not in content:
            multiplexer.send({"error": "Kit to subscribe to not given."})
            return

        try:
            kit = backend.models.Kit.objects.get(username=content['kit'])
            if not self.message.user.has_perm('backend.subscribe_to_kit_measurements_websocket', kit):
                multiplexer.send({"error": "Kit not found or you do not have access to it."})
                return

            channels.Group("kit-measurements-%s" % kit.username).add(multiplexer.reply_channel)
            multiplexer.send({"action": "subscribe", "kit": kit.username})
        except:
            multiplexer.send({"error": "Kit not found or you do not have access to it."})

class MeasurementPublishConsumer(JWTSessionAuthConsumer):
    """
    A measurement publish consumer. Any kit can publish measurements.
    The measurements are sent to all clients who are subscribed to
    measurements of that kit.
    """
    def receive(self, content, multiplexer, **kwargs):
        # Publish a measurement
        if "kit" not in self.message.channel_session:
            multiplexer.send({"error": "You must be a kit to publish measurements.'."})
            return

        try:
            # Fetch measurement message type
            measurement_message_type = content['measurement_type']

            # Deserialize measurement
            measurement_serializer = backend.serializers.MeasurementSerializer(data=content['measurement'])
            measurement_serializer.is_valid(raise_exception = True)

            measurement = backend.models.Measurement(**measurement_serializer.validated_data)

            kit = backend.models.Kit.objects.filter(username=self.message.channel_session['kit']).get()

            # Get the peripheral device object by its name (if it's associated with this kit)
            peripheral = kit.peripherals.filter(name=content['measurement']['peripheral']).get()

            # Add peripheral to the measurement object
            measurement.peripheral = peripheral

            # Get the registered measurement type by the physical quantity and physical unit if it exists
            measurement_types_qs = peripheral.peripheral_definition.measurement_types.filter(physical_quantity = measurement.physical_quantity, physical_unit = measurement.physical_unit)
            if measurement_types_qs:
                measurement_type = measurement_types_qs.first()
                measurement.measurement_type = measurement_type

            if measurement_message_type == "REDUCED":
                # Store reduced measurements
                measurement.save()

            output_serializer = backend.serializers.MeasurementOutputSerializer(measurement)
            message = {'measurement_type': measurement_message_type, 'measurement': output_serializer.data}
            self.group_send("kit-measurements-%s" % self.message.channel_session['kit'], message)
            multiplexer.send({"success": "published"})
        except Exception as exception:
            multiplexer.send({"error": "You must provide a valid measurement.'."})
            print(exception)
