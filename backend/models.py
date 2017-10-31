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
    
class SensorDefinition(models.Model):
    """
    Model to hold sensor definitions. Each sensor of a specific
    type will have its own sensor definition.
    """

    name = models.CharField(max_length = 100)
    brand = models.CharField(max_length = 100)
    type = models.CharField(max_length = 100)
    class_name = models.CharField(max_length = 255)

    def __str__(self):
        return self.name

class SensorConfigurationDefinition(models.Model):
    """
    Model to hold the definitions for configuration options of sensors.
    """

    sensor_definition = models.ForeignKey(SensorDefinition, on_delete = models.CASCADE)
    name = models.CharField(max_length = 100)
    default_value = models.CharField(max_length = 100)
    description = models.TextField()

class Sensor(models.Model):
    """
    Model of individual sensors. Each such sensor belongs
    to a single kit.
    """

    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    sensor_definition = models.ForeignKey(SensorDefinition, on_delete = models.CASCADE)
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
    
    sensor = models.ForeignKey(Sensor, on_delete = models.CASCADE)
    sensor_configuration_definition = models.ForeignKey(SensorConfigurationDefinition, on_delete = models.CASCADE)
    value = models.CharField(max_length = 100)

class Measurement(models.Model):
    """
    Model to hold sensor measurements.
    """

    sensor = models.ForeignKey(Sensor, on_delete = models.CASCADE)
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)

    # Null allowed, as it is possible no experiment is running
    experiment = models.ForeignKey(Experiment, on_delete = models.CASCADE, null = True)

    date_time = models.DateTimeField()

    # TODO: this should be made more robust (e.g. separate models for physical quantity and units)
    physical_quantity = models.CharField(max_length = 100)
    physical_unit = models.CharField(max_length = 100)

    value = models.FloatField()
