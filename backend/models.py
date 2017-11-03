"""
Module defining backend AstroPlant models.
"""

from django.db import models
import django.contrib.auth.models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin

class User(AbstractUser):
    pass

class PersonUser(User):
    pass

class Kit(User):
    """
    Model for AstroPlant kits.

    See also:
    https://docs.djangoproject.com/en/1.9/topics/auth/customizing/#extending-the-existing-user-model
    """
    type = models.CharField(max_length = 10)
    name = models.CharField(max_length = 250)
    description = models.TextField(default = "", blank = True)
    latitude = models.DecimalField(max_digits = 12, decimal_places = 4, blank = True, null = True)
    longitude = models.DecimalField(max_digits = 12, decimal_places = 4, blank = True, null = True)
    privacy_public_dashboard = models.BooleanField(default = False)
    privacy_show_on_map = models.BooleanField(default = False)

    users = models.ManyToManyField(
        PersonUser,
        through='KitMembership',
        through_fields=('kit', 'user'),
    )

    class Meta:
        verbose_name = 'Kit'
        verbose_name_plural = 'Kits'

    def generate_config(self):
        """
        Generate a dictionary containing the kit configuration.
        """

        # Generate the configuration dictionary for each sensor
        sensors = []
        for sensor in self.sensor_set.filter(active = True).all():

            # Get the sensor definition
            sensor_definition = sensor.sensor_definition

            # Get the sensor configuration definitions
            sensor_configuration_definitions = sensor_definition.sensor_configuration_definitions.all()

            # Get the sensor configurations
            sensor_configurations = sensor.sensor_configurations.all()
            sensor_configurations_dict = {configuration.sensor_configuration_definition: configuration for configuration in sensor_configurations}

            # For each sensor configuration definition, see if the sensor provides a value
            # otherwise use the default value.
            param_config = []
            for configuration_definition in sensor_configuration_definitions:
                if configuration_definition in sensor_configurations_dict:
                    value = sensor_configurations_dict[configuration_definition].value
                else:
                    value = configuration_definition.default_value

                param_config.append({'parameter': configuration_definition.name, 'value': value})

            sensors.append({
                'sensor_definition_name': sensor_definition.name,
                'sensor_name': sensor.name,
                'class_name': sensor_definition.class_name,
                'parameters': param_config})

        return {'name': self.name, 'sensors': sensors}

    def generate_password():
        import random

        RANDOM_KIT_PASSWORD_LENGTH = 24

        # Generate a password without vowels to minimize the chance 
        # of generating bad words :)
        # also 0, (o), 1, l, 2, z, 5, s are removed, as they look similar
        return ''.join(random.choice('346789bcdfghjkmnpqrtvwxyBCDFGHJKMNPQRTVWXY!@#$%&') for i in range(RANDOM_KIT_PASSWORD_LENGTH))

class Experiment(models.Model):
    """
    Model for experiments.
    """
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField(blank = True, null = True)

class KitMembership(models.Model):
    """
    Link table for kits and users, with additional data fields.
    """
    user = models.ForeignKey(PersonUser, on_delete = models.CASCADE)
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    date_time_linked = models.DateTimeField()

    def __str__(self):
        return "%s - %s" % (self.kit, self.user)
    
class MeasurementType(models.Model):
    """
    Model to hold the definitions for the types of measurements.
    """

    physical_quantity = models.CharField(max_length = 100)
    physical_unit = models.CharField(max_length = 100)
    physical_unit_symbol = models.CharField(max_length = 100)

    def __str__(self):
        return "%s (%s)" % (self.physical_quantity, self.physical_unit)

class SensorDefinition(models.Model):
    """
    Model to hold sensor definitions. Each sensor of a specific
    type will have its own sensor definition.
    """

    name = models.CharField(max_length = 100, unique = True)
    description = models.TextField(blank = True)
    verified = models.BooleanField(default = False)
    public = models.BooleanField(default = False)
    owner = models.ForeignKey(PersonUser,
                              related_name = 'sensor_definitions',
                              blank = True,
                              null = True)
    brand = models.CharField(max_length = 100, blank = True)
    type = models.CharField(max_length = 100, blank = True)
    class_name = models.CharField(max_length = 255)
    measurement_types = models.ManyToManyField(MeasurementType)

    def __str__(self):
        return self.name

class SensorConfigurationDefinition(models.Model):
    """
    Model to hold the definitions for configuration options of sensors.
    """

    sensor_definition = models.ForeignKey(SensorDefinition,
                                          on_delete = models.CASCADE,
                                          related_name = 'sensor_configuration_definitions')
    name = models.CharField(max_length = 100)
    default_value = models.CharField(max_length = 100)
    description = models.TextField()

    def __str__(self):
        return "%s - %s" % (self.sensor_definition, self.name)

class Sensor(models.Model):
    """
    Model of individual sensors. Each such sensor belongs
    to a single kit.
    """

    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    sensor_definition = models.ForeignKey(SensorDefinition,
                                          on_delete = models.CASCADE)
    name = models.CharField(max_length = 100)
    active = models.BooleanField()
    date_time_added = models.DateTimeField()
    date_time_removed = models.DateTimeField(blank = True, null = True)

    def __str__(self):
        return self.name

class SensorConfiguration(models.Model):
    """
    Model of configuration for individual sensors.
    """
    
    sensor = models.ForeignKey(Sensor,
                               on_delete = models.CASCADE,
                               related_name = 'sensor_configurations')
    sensor_configuration_definition = models.ForeignKey(SensorConfigurationDefinition,
                                                        on_delete = models.CASCADE)
    value = models.CharField(max_length = 100)

    def __str__(self):
        return "%s - %s" % (self.sensor, self.sensor_configuration_definition)

class Measurement(models.Model):
    """
    Model to hold sensor measurements.
    """

    sensor = models.ForeignKey(Sensor, on_delete = models.CASCADE)
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    measurement_type = models.ForeignKey(MeasurementType, on_delete = models.CASCADE, null = True)

    # Null allowed, as it is possible no experiment is running
    experiment = models.ForeignKey(Experiment, on_delete = models.CASCADE, null = True)

    date_time = models.DateTimeField()
    value = models.FloatField()

    physical_quantity = models.CharField(max_length = 100, null = True)
    physical_unit = models.CharField(max_length = 100, null = True)
