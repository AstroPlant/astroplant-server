from django.contrib import admin

from backend import models

@admin.register(models.Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ('serial', 'type', 'name')
    ordering = ('serial', 'name', 'id')

@admin.register(models.KitMembership)
class KitMembership(admin.ModelAdmin):
    list_display = ('kit', 'user', 'date_time_linked')
    ordering = ('kit', 'user')

admin.site.register(models.SensorType)
admin.site.register(models.Experiment)
admin.site.register(models.Sensor)
admin.site.register(models.Measurement)
