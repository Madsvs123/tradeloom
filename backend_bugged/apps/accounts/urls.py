from django.urls import include, path
from rest_framewrk.routers import DefaultRouter

from .views import (
    AuditLogViewSet,
    BranchViewSet,
    BuyerVerificationViewSet,
    CompanyAccountViewSet,
    LoginViewSet,
    MeViewSet,
    OrganizationAddressViewSet,
    OrganizationRoleViewSet,
    OrganizationSettingsViewSet,
    PasswordResetViewSet,
    RegisterViewSet,
    SupplierVerificationViewSet,
    TeamMemberViewSet,
    TokenRefreshViewSet,
)

router = DefaultRouter()
router.register("auth/register", RegisterViewSet, basename="register")
router.register("auth/login", LoginViewSet, basename="login")
router.register("auth/token/refresh", TokenRefreshViewSet, basename="token-refresh")
router.register("auth/password", PasswordResetViewSet, basename="password-reset")
router.register("auth/me", MeViewSet, basename="me")
router.register("companies", CompanyAccountViewSet, basename="company")
router.register("roles", OrganizationRoleViewSet, basename="organization-role")
router.register("team-members", TeamMemberViewSet, basename="team-member")
router.register("branches", BranchViewSet, basename="branch")
router.register("addresses", OrganizationAddressViewSet, basename="organization-address")
router.register("settings", OrganizationSettingsViewSet, basename="organization-settings")
router.register("supplier-verifications", SupplierVerificationViewSet, basename="supplier-verification")
router.register("buyer-verifications", BuyerVerificationViewSet, basename="buyer-verification")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]
