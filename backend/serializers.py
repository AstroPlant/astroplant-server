from backend import models
from rest_framework import serializers

class HyperlinkedKitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Kit
        fields = ('url', 'type', 'name', 'description', 'latitude', 'longitude', 'peripherals', 'experiment_set')

class HyperlinkedExperimentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Experiment
        fields = ('url', 'kit', 'date_time_start', 'date_time_end')

class HyperlinkedPeripheralConfigurationDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PeripheralConfigurationDefinition
        fields = ('url', 'peripheral_definition', 'name', 'default_value', 'description')

class HyperlinkedPeripheralDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    peripheral_configuration_definitions = HyperlinkedPeripheralConfigurationDefinitionSerializer(many=True)

    class Meta:
        model = models.PeripheralDefinition
        fields = ('url', 'name', 'brand', 'type', 'class_name', 'peripheral_configuration_definitions')

class HyperlinkedPeripheralConfigurationSerializer(serializers.HyperlinkedModelSerializer):
    peripheral_configuration_definition = HyperlinkedPeripheralConfigurationDefinitionSerializer()

    class Meta:
        model = models.PeripheralConfiguration
        fields = ('peripheral_configuration_definition', 'value')

class HyperlinkedPeripheralSerializer(serializers.HyperlinkedModelSerializer):
    peripheral_configurations = HyperlinkedPeripheralConfigurationSerializer(many=True)

    class Meta:
        model = models.Peripheral
        fields = ('url', 'kit', 'peripheral_definition', 'name', 'active', 'date_time_added', 'date_time_removed', 'peripheral_configurations')

class HyperlinkedMeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('url', 'id', 'peripheral_type', 'date_time', 'value')

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Measurement
        fields = ('id', 'peripheral', 'date_time', 'value')
