"""
Module defining backend AstroPlant models.
"""

from django.db import models
import django.contrib.auth.models

class Kit(models.Model):
    """
    Model for AstroPlant kits.
    """
    serial = models.CharField(max_length = 250)
    type = models.CharField(max_length = 10)
    name = models.CharField(max_length = 250)
    users = models.ManyToManyField(django.contrib.auth.models.User)

class KitProfile(models.Model):
    """
    Model for AstroPlant kit profiles.
    """
    kit = models.OneToOneField(Kit, on_delete = models.CASCADE, primary_key = True)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=12, decimal_places=4)
    longitude = models.DecimalField(max_digits=12, decimal_places=4)

class Experiment(models.Model):
    """
    Model for experiments.
    """
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()

class KitMembership(models.Model):
    """
    Link table for kits and users, with additional data fields.
    """
    user = models.ForeignKey(django.contrib.auth.models.User, on_delete = models.CASCADE)
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    date_time_linked = models.DateTimeField()
    
class SensorType(models.Model):
    """
    Model to hold sensor types. For example, an EC sensor
    of brand A will be a row, and an EC sensor of brand B
    will be a different row.
    """

    name = models.CharField(max_length = 100)
    brand = models.CharField(max_length = 100)
    type = models.CharField(max_length = 100)
    unit = models.CharField(max_length = 100)

class Sensor(models.Model):
    """
    Model of individual sensors. Each such sensor belongs
    to a single kit.
    """

    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    type = models.ForeignKey(SensorType, on_delete = models.CASCADE)

class Measurement(models.Model):
    """
    Model to hold sensor measurements.
    """

    sensor = models.ForeignKey(Sensor, on_delete = models.CASCADE)

    # Null allowed, as it is possible no experiment is running
    experiment = models.ForeignKey(Experiment, on_delete = models.CASCADE, null = True)

    date_time = models.DateTimeField()
    value = models.FloatField()
