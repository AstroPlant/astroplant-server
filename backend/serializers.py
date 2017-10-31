from backend import models
from rest_framework import serializers

class HyperlinkedKitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Kit
        fields = ('url', 'type', 'name', 'description', 'latitude', 'longitude', 'sensor_set', 'experiment_set')

class HyperlinkedExperimentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Experiment
        fields = ('url', 'kit', 'date_time_start', 'date_time_end')

class HyperlinkedSensorDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SensorDefinition
        fields = ('url', 'name', 'brand', 'type', 'class_name')

class HyperlinkedSensorConfigurationDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SensorConfigurationDefinition
        fields = ('url', 'sensor_definition', 'name', 'default_value', 'description')

class HyperlinkedSensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Sensor
        fields = ('url', 'kit', 'sensor_definition', 'name', 'active', 'date_time_added', 'date_time_removed')

class HyperlinkedSensorConfigurationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SensorConfiguration
        fields = ('url', 'sensor', 'sensor_configuration_definition', 'value')

class HyperlinkedMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('url', 'id', 'sensor_type', 'date_time', 'value')

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('id', 'sensor', 'date_time', 'value')
