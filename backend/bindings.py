# polls/bindings.py

from channels_api.bindings import ResourceBinding

from backend import models
from backend import serializers

"""
class MeasurementBinding(ResourceBinding):

    model = models.Measurement
    stream = "measurements"
    serializer_class = serializers.MeasurementSerializer
    queryset = model.objects.all()
"""