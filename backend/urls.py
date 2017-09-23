from django.conf.urls import include, url
from rest_framework import viewsets, mixins, routers, renderers
from rest_framework.decorators import detail_route

from backend import models
from backend import permissions

class KitViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    queryset = models.Kit.objects.all()
    serializer_class = models.KitSerializer
    permission_classes = [permissions.IsObjectRequested,]

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        kit = self.get_object()
        return Response(kit.highlighted)

class ExperimentViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = models.Experiment.objects.all()
    serializer_class = models.ExperimentSerializer
    permission_classes = [permissions.IsExperimentOwner,]

class SensorTypeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = models.SensorType.objects.all()
    serializer_class = models.SensorTypeSerializer

class MeasurementViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    queryset = models.Measurement.objects.all()
    serializer_class = models.MeasurementSerializer
    permission_classes = [permissions.IsMeasurementOwner,]

router = routers.DefaultRouter()
router.register(r'kits', KitViewSet, base_name='kit')
router.register(r'experiments', ExperimentViewSet)
router.register(r'sensor-types', SensorTypeViewSet)
router.register(r'measurements', MeasurementViewSet)

urlpatterns = [
    #url(r'^api-auth/', include('rest_framework.urls',
    #                           namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^channels-api/', include('channels_api.urls'))
]
