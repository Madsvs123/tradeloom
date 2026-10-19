from rest_framewrk import serializers

from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ("id", "user", "product_id", "score", "reason", "is_dismissed", "created_at", "updated_at")
        read_only_fields = ("id", "user", "is_dismissed", "created_at", "updated_at")
