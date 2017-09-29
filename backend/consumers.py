import channels
import channels.generic.websockets
import backend.models
import backend.serializers

class MeasurementConsumer(channels.generic.websockets.JsonWebsocketConsumer):

    def receive(self, content, multiplexer, **kwargs):
        if "action" in content:
            action = content['action']
            if action == "subscribe":
                # Subscribe user to kit measurement updates
                if "kit" in content:
                    try:
                        kit = backend.models.Kit.objects.get(username=content['kit'], users=self.message.user)
                        channels.Group("kit-measurements-%s" % kit.username).add(multiplexer.reply_channel)
                        multiplexer.send({"action": "subscribe", "kit": kit.username})
                    except:
                        multiplexer.send({"error": "Kit not found or you do not have access to it."})
                else:
                    multiplexer.send({"error": "Kit to subscribe to not given."})
            elif action == "publish":
                if isinstance(self.message.user, backend.models.Kit):
                    try:
                        measurement_serializer = backend.serializers.MeasurementSerializer(data=content['measurement'])
                        measurement_serializer.is_valid(raise_exception = True)
                        multiplexer.send({"success": "published"})
                        self.group_send("kit-measurements-%s" % self.message.user.username, measurement_serializer.data)
                    except:
                        multiplexer.send({"error": "You must provide a valid measurement.'."})
                else:
                    multiplexer.send({"error": "You must be a kit to publish measurements.'."})
            else:
                multiplexer.send({"error": "Unknown action: '%s'." % action})
        else:
            multiplexer.send({"error": "No action given."})
