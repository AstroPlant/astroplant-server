from django.conf.urls import include, url
from rest_framework import viewsets, mixins, routers, renderers, documentation
import rest_framework_jwt.views
from rest_framework.decorators import detail_route
import rest_framework.schemas

from backend import models
from backend import serializers
from backend import permissions

class KitViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    """
    list:
    List all kits the user has access to. A person user has access to all kits it owns,
    whereas a kit user has access only to itself.

    retrieve:
    Return the given kit, if the user has access to it.
    """
    def get_queryset(self):
        """
        Get a queryset of all kits the user has access to.
        """

        user = self.request.user
        
        if isinstance(user, models.Kit):
            return models.Kit.objects.filter(pk=user.pk)
        else:
            return models.Kit.objects.filter(users=user.pk)

    serializer_class = serializers.KitSerializer

class ExperimentViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """
    list:
    List all experiments the user has access to. A person user has access to experiments
    of all kits it owns. A kit user has access to its experiments.

    retrieve:
    Return the given experiment, if the user has access to it.
    """
    def get_queryset(self):
        """
        Get a queryset of all experiments the user has access to.
        """
        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Experiment.objects.filter(kit=user.pk)
        else:
            kits = models.Kit.objects.filter(users=user.pk)
            return models.Experiment.objects.filter(kit=kits)

    serializer_class = serializers.ExperimentSerializer

class SensorTypeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = models.SensorType.objects.all()
    serializer_class = serializers.SensorTypeSerializer

class MeasurementViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    """
    list:
    List all measurements the user has access to. A person user has access to measurements
    of all kits it owns. A kit user has access to its measurements.

    retrieve:
    Return the given measurement, if the user has access to it.

    create:
    Create a measurement. Only kit users can add measurements.
    """
    def get_queryset(self):
        """
        Get a queryset of all measurements the user has access to.
        """
        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Measurement.objects.filter(kit=user.pk)
        else:
            kits = models.Kit.objects.filter(users=user.pk)
            return models.Measurement.objects.filter(kit=kits)

    serializer_class = serializers.MeasurementSerializer
    permission_classes = [permissions.IsNotCreationOrIsAuthenticatedKit,]

    def perform_create(self, serializer):
        serializer.save(kit=self.request.user)

router = routers.DefaultRouter()
router.register(r'kits', KitViewSet, base_name='kit')
router.register(r'experiments', ExperimentViewSet, base_name='experiment')
router.register(r'sensor-types', SensorTypeViewSet)
router.register(r'measurements', MeasurementViewSet, base_name='measurement')

urlpatterns = [
    url(r'^api/auth-token-obtain/', rest_framework_jwt.views.obtain_jwt_token),
    url(r'^api/auth-token-verify/', rest_framework_jwt.views.verify_jwt_token),
    url(r'^api/auth-token-refresh/', rest_framework_jwt.views.refresh_jwt_token),
    url(r'^api-schema/$', rest_framework.schemas.get_schema_view(title='AstroPlant API')),
    url(r'^api-docs/', documentation.include_docs_urls(title='AstroPlant API')),
    url(r'^channels-api/', include('channels_api.urls')),
    url(r'^api/', include(router.urls))
]
