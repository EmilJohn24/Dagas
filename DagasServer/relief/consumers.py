from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin

from relief.models import AlgorithmExecution, RouteSuggestion, DonorProfile
from relief.serializers import AlgorithmExecutionSerializer, DonorSerializer


class AlgorithmConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = AlgorithmExecution.objects.all()
    serializer_class = AlgorithmExecutionSerializer

