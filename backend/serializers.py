from backend import models
from rest_framework import serializers

class HyperlinkedKitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Kit
        fields = ('url', 'type', 'name', 'description', 'latitude', 'longitude', 'sensors', 'experiment_set')

class HyperlinkedExperimentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Experiment
        fields = ('url', 'kit', 'date_time_start', 'date_time_end')

class HyperlinkedSensorConfigurationDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SensorConfigurationDefinition
        fields = ('url', 'sensor_definition', 'name', 'default_value', 'description')

class HyperlinkedSensorDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    sensor_configuration_definitions = HyperlinkedSensorConfigurationDefinitionSerializer(many=True)

    class Meta:
        model = models.SensorDefinition
        fields = ('url', 'name', 'brand', 'type', 'class_name', 'sensor_configuration_definitions')

class HyperlinkedSensorConfigurationSerializer(serializers.HyperlinkedModelSerializer):
    sensor_configuration_definition = HyperlinkedSensorConfigurationDefinitionSerializer()

    class Meta:
        model = models.SensorConfiguration
        fields = ('sensor_configuration_definition', 'value')

class HyperlinkedSensorSerializer(serializers.HyperlinkedModelSerializer):
    sensor_configurations = HyperlinkedSensorConfigurationSerializer(many=True)

    class Meta:
        model = models.Sensor
        fields = ('url', 'kit', 'sensor_definition', 'name', 'active', 'date_time_added', 'date_time_removed', 'sensor_configurations')

class HyperlinkedMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('url', 'id', 'sensor_type', 'date_time', 'value')

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('id', 'sensor', 'date_time', 'value')
