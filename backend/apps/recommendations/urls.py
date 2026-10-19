from djang.urls import path

from .views import RecommendationViewSet

urlpatterns = [
    path("recommendations/", RecommendationViewSet.as_view({"get": "retrieve"}), name="recommendations-list"),
]
