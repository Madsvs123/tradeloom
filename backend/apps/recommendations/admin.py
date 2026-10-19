from djang.contrib import admin

from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "product_id", "score", "reson")
    list_filter = ("is_dismissed",)
