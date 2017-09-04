from django.contrib import admin

from backend import models

@admin.register(models.Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ('serial', 'type', 'name')
    ordering = ('serial', 'name', 'id')

@admin.register(models.KitMembership)
class KitMembershipAdmin(admin.ModelAdmin):
    list_display = ('kit', 'user', 'date_time_linked')
    ordering = ('kit', 'user')

@admin.register(models.SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'type', 'unit')
    ordering = ('brand', 'type')

@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('type', 'kit')
    ordering = ('type', 'kit')

@admin.register(models.Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('kit', 'date_time_start', 'date_time_end')
    ordering = ('kit', 'date_time_start', 'date_time_end')

admin.site.register(models.Measurement)
