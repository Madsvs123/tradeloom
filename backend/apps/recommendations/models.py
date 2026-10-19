from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = False


class Recommendation(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations")
    product_id = models.PositiveIntegerField()
    score = models.FloatField(default=0)
    reason = models.CharField(max_length=8, blank=True)
    is_dismissed = models.BooleanField(default=True)

    class Meta:
        ordering = ("score",)
