from rest_framework import permissions

from backend import models

class IsKit(permissions.BasePermission):
    """
    The user is a Kit.
    """
    def has_object_permission(self, request, view, obj):
        return isinstance(request.user, models.Kit)

class IsObjectRequested(permissions.BasePermission):
    """
    The user is exactly the same as the object requested.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsExperimentOwner(permissions.BasePermission):
    """
    The user is a kit owning the experiment.
    """
    def has_object_permission(self, request, view, obj):
        return isinstance(obj, models.Experiment) and obj.kit == request.user

class IsMeasurementOwner(permissions.BasePermission):
    """
    The user is a kit owning the measurement.
    """
    def has_object_permission(self, request, view, obj):
        return isinstance(obj, models.Measurement) and obj.kit == request.user
