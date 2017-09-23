# polls/bindings.py

from channels_api.bindings import ResourceBinding

import backend.models
# from .serializers import QuestionSerializer



class MeasurementBinding(ResourceBinding):

    model = backend.models.Measurement
    stream = "measurements"
    serializer_class = backend.models.MeasurementSerializer
    queryset = model.objects.all()
