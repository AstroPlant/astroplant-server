import channels
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

import backend.models
import backend.serializers
import backend.auth

class MeasurementSubscribeConsumer(WebsocketConsumer):
    """
    A measurement subscribe consumer. Any user (or kit) can
    subscribe to measurements of kits they own.
    """
    def connect(self):
        if not 'user' in self.scope:
            # Reject channel
            return

        self.user = self.scope['user']

        if not 'kit_name' in self.scope['url_route']['kwargs']:
            # Reject channel
            return

        self.kit = backend.models.Kit.objects.get(username=self.scope['url_route']['kwargs']['kit_name'])
        
        if self.user.has_perm('backend.subscribe_to_kit_measurements_websocket', self.kit):
            async_to_sync(self.channel_layer.group_add)(
                "kit-measurements-%s" % self.kit.username,
                self.channel_name
            )

            self.accept()

    def disconnect(self, close_code):
        # Leave group
        async_to_sync(self.channel_layer.group_discard)(
            "kit-measurements-%s" % self.kit.username,
            self.channel_name
        )

    def measurement(self, event):
        self.send(json.dumps(event['message']))

class KitConsumer(WebsocketConsumer):
    """
    A kit consumer. Any authenticated kit can open this channel.
    The channel can be used to, for example, publish measurements.
    """
    def connect(self):
        print(self.scope)
        if not 'user' in self.scope:
            # Reject channel
            return

        # User must be a Kit.
        if isinstance(self.scope['user'], backend.models.Kit):
            self.kit = self.scope['user']
            self.accept()

    def receive(self, text_data):
        """
        :param text_data: The received data. Expected to be a json encoded string,
        with keys 'stream' indicating the functionality to be used, 'nonce' indicating
        some unique data that should be returned as-is in a reply from the server, and
        optionally 'payload', data that is sent to the desired functionality.
        """
        content = json.loads(text_data)

        stream = content['stream']
        nonce = content['nonce']
        payload = content['payload'] if 'payload' in content else {}

        send_reply = lambda msg: self.send(json.dumps({
            'stream': stream,
            'reply-nonce': nonce,
            'payload': msg
        }))

        if stream == "publish-measurement":
            self.publish_measurement(payload, send_reply)

    def publish_measurement(self, content, send_reply):
        """
        Publish a measurement. Saves measurements of type REDUCED, and
        sends the measurement to all channels listening on the
        `kit-measurements-%s` group.
        """
        
        try:
            # Fetch measurement message type
            measurement_type = content['measurement_type']

            # Deserialize measurement
            measurement_serializer = backend.serializers.MeasurementSerializer(data=content['measurement'])
            measurement_serializer.is_valid(raise_exception = True)

            measurement = backend.models.Measurement(**measurement_serializer.validated_data)

            # Add the kit to the measurement
            measurement.kit = self.kit

            # Get the peripheral device object by its name (if it's associated with this kit)
            peripheral = self.kit.peripherals.filter(name=content['measurement']['peripheral']).get()

            # Add peripheral to the measurement object
            measurement.peripheral = peripheral

            # Get the registered measurement type by the physical quantity and physical unit if it exists
            quantity_types_qs = peripheral.peripheral_definition.quantity_types.filter(physical_quantity = measurement.physical_quantity, physical_unit = measurement.physical_unit)
            if quantity_types_qs:
                quantity_type = quantity_types_qs.first()
                measurement.quantity_type = quantity_type

            if measurement_type == "REDUCED":
                # Store reduced measurements
                measurement.save()

            output_serializer = backend.serializers.MeasurementOutputSerializer(measurement)
            message = {'measurement_type': measurement_type, 'measurement': output_serializer.data}
            async_to_sync(self.channel_layer.group_send)(
                "kit-measurements-%s" % self.kit.username,
                {
                    'type': 'measurement',
                    'message': message
                }
            )
            send_reply({"success": "published"})
        except Exception as exception:
            send_reply({"error": "You must provide a valid measurement.'."})
            print("Websocket: exception on publishing measurement")
            print(exception)
