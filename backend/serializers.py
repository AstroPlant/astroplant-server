from backend import models
from rest_framework import serializers

class KitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Kit
        fields = ('url', 'type', 'name', 'description', 'latitude', 'longitude', 'experiment_set')

class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Experiment
        fields = ('url', 'kit', 'date_time_start', 'date_time_end')

class SensorTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SensorType
        fields = ('url', 'name', 'brand', 'type', 'unit')

class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('url', 'id', 'sensor_type', 'date_time', 'value')
