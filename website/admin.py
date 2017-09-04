from django.contrib import admin

from backend import models

admin.site.register(models.Kit)
admin.site.register(models.KitProfile)
admin.site.register(models.SensorType)
admin.site.register(models.Experiment)
admin.site.register(models.Sensor)
admin.site.register(models.Measurement)
