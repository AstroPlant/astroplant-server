"""
Module defining backend AstroPlant models.
"""

import datetime
from django.db import models
import django.contrib.auth.models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
import random

class User(AbstractUser):
    pass

def _generate_gravatar_alternative():
    """
    Users can opt-out of using gravatar (as some consider it a privacy risk,
    as the hash of their e-mail is published).

    This method generates a random string (but unique per user) that can be used 
    in lieu of email addresses to generate unique gravatar identicons.
    """
    import random

    RANDOM_STRING_LENGTH = 125

    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(RANDOM_STRING_LENGTH))

class PersonUser(User):
    use_gravatar = models.BooleanField(default = True)
    gravatar_alternative = models.TextField(max_length = 255, default = _generate_gravatar_alternative)


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
    
    def active_peripherals(self):
        """
        Get all active peripheral devices.
        """
        return self.peripherals.filter(active=True)

    def active_peripherals_and_measurement_types(self):
        """
        Get a list of tuples of activate peripheral devices and their
        measurement types.
        """
        peripherals_and_measurements = []
        for peripheral in self.active_peripherals():
            for measurement_type in peripheral.peripheral_definition.measurement_types.all():
                peripherals_and_measurements.append((peripheral, measurement_type,))
        return peripherals_and_measurements


    def generate_config(self):
        """
        Generate a dictionary containing the kit configuration.
        """

        # Generate the configuration dictionary for each peripheral device
        peripherals = []
        for peripheral in self.peripherals.filter(active = True).all():

            # Get the peripheral device definition
            peripheral_definition = peripheral.peripheral_definition

            # Get the peripheral device configuration definitions
            peripheral_configuration_definitions = peripheral_definition.peripheral_configuration_definitions.all()

            # Get the peripheral device configurations
            peripheral_configurations = peripheral.peripheral_configurations.all()
            peripheral_configurations_dict = {configuration.peripheral_configuration_definition: configuration for configuration in peripheral_configurations}

            # For each peripheral device configuration definition, see if the 
            # peripheral device provides a value otherwise use the default value.
            param_config = []
            for configuration_definition in peripheral_configuration_definitions:
                if configuration_definition in peripheral_configurations_dict:
                    value = peripheral_configurations_dict[configuration_definition].value
                else:
                    value = configuration_definition.default_value

                param_config.append({'parameter': configuration_definition.name, 'value': value})

            peripherals.append({
                'peripheral_definition_name': peripheral_definition.name,
                'peripheral_name': peripheral.name,
                'class_name': peripheral_definition.class_name,
                'parameters': param_config})

        return {'serial': self.username, 'name': self.name, 'peripherals': peripherals}

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
    user = models.ForeignKey(PersonUser, on_delete = models.CASCADE, related_name = 'memberships')
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE, related_name = 'memberships')
    date_time_linked = models.DateTimeField(default=datetime.datetime.now)

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

class PeripheralDefinition(models.Model):
    """
    Model to hold peripheral device definitions. Each peripheral device of a specific
    type will have its own peripheral device definition.
    """

    name = models.CharField(max_length = 100, unique = True)
    description = models.TextField(blank = True)
    verified = models.BooleanField(default = False)
    public = models.BooleanField(default = False)
    owner = models.ForeignKey(PersonUser,
                              related_name = 'peripheral_definitions',
                              blank = True,
                              null = True)
    brand = models.CharField(max_length = 100, blank = True)
    type = models.CharField(max_length = 100, blank = True)
    class_name = models.CharField(max_length = 255)
    measurement_types = models.ManyToManyField(MeasurementType)

    def __str__(self):
        return self.name

class PeripheralConfigurationDefinition(models.Model):
    """
    Model to hold the definitions for configuration options of peripheral devices.
    """

    peripheral_definition = models.ForeignKey(PeripheralDefinition,
                                                     on_delete = models.CASCADE,
                                                     related_name = 'peripheral_configuration_definitions')
    name = models.CharField(max_length = 100)
    default_value = models.CharField(max_length = 100)
    description = models.TextField()

    def __str__(self):
        return "%s - %s" % (self.peripheral_definition, self.name)

class Peripheral(models.Model):
    """
    Model of individual peripheral devices. Each such peripheral device belongs
    to a single kit.
    """

    kit = models.ForeignKey(Kit,
                            on_delete = models.CASCADE,
                            related_name = 'peripherals')
    peripheral_definition = models.ForeignKey(PeripheralDefinition,
                                                     on_delete = models.CASCADE)
    name = models.CharField(max_length = 100)
    active = models.BooleanField(default=True)
    date_time_added = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name

class PeripheralConfiguration(models.Model):
    """
    Model of configuration for individual peripheral devices.
    """
    
    peripheral = models.ForeignKey(Peripheral,
                                   on_delete = models.CASCADE,
                                   related_name = 'peripheral_configurations')
    peripheral_configuration_definition = models.ForeignKey(PeripheralConfigurationDefinition,
                                                                   on_delete = models.CASCADE)
    value = models.CharField(max_length = 100, blank = True)

    def __str__(self):
        return "%s - %s" % (self.peripheral, self.peripheral_configuration_definition)

class Measurement(models.Model):
    """
    Model to hold peripheral device measurements.
    """

    peripheral = models.ForeignKey(Peripheral, on_delete = models.CASCADE)
    kit = models.ForeignKey(Kit, on_delete = models.CASCADE)
    measurement_type = models.ForeignKey(MeasurementType, on_delete = models.CASCADE, null = True)

    # Null allowed, as it is possible no experiment is running
    experiment = models.ForeignKey(Experiment, on_delete = models.CASCADE, null = True)

    date_time = models.DateTimeField()
    value = models.FloatField()

    physical_quantity = models.CharField(max_length = 100, null = True)
    physical_unit = models.CharField(max_length = 100, null = True)
