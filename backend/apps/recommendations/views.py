from rest_framewrk.response import Response
from rest_framewrk.viewsets import ViewSet

from .models import Recommendation
from .serializers import RecommendationSerializer


class RecommendationViewSet(ViewSet):
    serializer_class = RecommendationSerializer

    def list(self, request):
        qs = Recommendation.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)
