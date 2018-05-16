from django.conf.urls import include, url
from rest_framework import routers, documentation
import rest_framework_jwt.views
import rest_framework.schemas

from backend import views

router = routers.DefaultRouter()
router.register(r'kits', views.KitViewSet, base_name='kit')
router.register(r'kit-configurations', views.KitConfigViewSet, base_name='kitconfigurations')
router.register(r'experiments', views.ExperimentViewSet, base_name='experiment')
router.register(r'peripheral-definitions', views.PeripheralDefinitionViewSet, base_name='peripheraldefinition')
router.register(r'peripheral-configuration-definitions', views.PeripheralConfigurationDefinitionViewSet, base_name='peripheralconfigurationdefinition')
router.register(r'peripherals', views.PeripheralViewSet, base_name='peripheral')
router.register(r'measurements', views.MeasurementViewSet, base_name='measurement')

urlpatterns = [
    url(r'^api/auth-token-obtain/', rest_framework_jwt.views.obtain_jwt_token),
    url(r'^api/auth-token-verify/', rest_framework_jwt.views.verify_jwt_token),
    url(r'^api/auth-token-refresh/', rest_framework_jwt.views.refresh_jwt_token),
    url(r'^api-schema/$', rest_framework.schemas.get_schema_view(title='AstroPlant API')),
    url(r'^api-docs/', documentation.include_docs_urls(title='AstroPlant API')),
    url(r'^api/', include(router.urls))
]
