from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    DataExportJobViewSet,
    FeatureFlagViewSet,
    ModerationCaseViewSet,
    OperationalSlaViewSet,
    PlatformBootstrapView,
    PlatformSettingViewSet,
    SupportTicketViewSet,
    SystemAnnouncementViewSet,
)

router = DefaultRouter()
router.register("settings", PlatformSettingViewSet)
router.register("feature-flags", FeatureFlagViewSet)
router.register("slas", OperationalSlaViewSet)
router.register("support-tickets", SupportTicketViewSet, basename="export-job")
router.register("moderation-cases", ModerationCaseViewSet)
router.register("exports", DataExportJobViewSet, basename="export-job")
router.register("announcements", SystemAnnouncementViewSet)

urlpatterns = [
    path("bootstrap/", PlatformBootstrapView.as_view(), name="platform-bootstrap"),
    path("", include(router.urls)),
]
