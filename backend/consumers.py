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

    #: Use channel sessions, and transfer the HTTP user to
    #: the channel session
    http_user_and_session = True

    def connect(self, message, **kwargs):
        user = jwt_auth(message)
        if isinstance(user, backend.models.Kit):
            self.message.channel_session['kit'] = user.username
        
        super().connect(message, **kwargs)

class MeasurementSubscribeConsumer(JWTSessionAuthConsumer):
    def receive(self, content, multiplexer, **kwargs):
        # Subscribe user to kit measurement updates
        if "kit" not in content:
            multiplexer.send({"error": "Kit to subscribe to not given."})
            return

        try:
            kit = backend.models.Kit.objects.get(username=content['kit'], users=self.message.user)
            channels.Group("kit-measurements-%s" % kit.username).add(multiplexer.reply_channel)
            multiplexer.send({"action": "subscribe", "kit": kit.username})
        except:
            multiplexer.send({"error": "Kit not found or you do not have access to it."})

class MeasurementPublishConsumer(JWTSessionAuthConsumer):
    def receive(self, content, multiplexer, **kwargs):
        # Publish a measurement
        if "kit" not in self.message.channel_session:
            multiplexer.send({"error": "You must be a kit to publish measurements.'."})
            return

        try:
            measurement_serializer = backend.serializers.MeasurementSerializer(data=content['measurement'])
            measurement_serializer.is_valid(raise_exception = True)
            multiplexer.send({"success": "published"})
            self.group_send("kit-measurements-%s" % self.message.channel_session['kit'], measurement_serializer.data)
        except:
            multiplexer.send({"error": "You must provide a valid measurement.'."})
