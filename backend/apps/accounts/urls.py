from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AddressBookEntryViewSet,
    AuditLogViewSet,
    BranchViewSet,
    BuyerVerificationViewSet,
    CompanyAccountViewSet,
    DepartmentViewSet,
    LoginViewSet,
    MeViewSet,
    OrganizationAddressViewSet,
    OrganizationRoleViewSet,
    OrganizationSettingsViewSet,
    PasswordResetViewSet,
    RegisterViewSet,
    SecurityEventViewSet,
    SupplierVerificationViewSet,
    TeamInvitationViewSet,
    TeamMemberViewSet,
    TokenRefreshViewSet,
    UserActivityViewSet,
    UserApiTokenViewSet,
    UserPreferenceViewSet,
)

router = DefaultRouter()
router.register("auth/register", RegisterViewSet, basename="register")
router.register("auth/login", LoginViewSet, basename="login")
router.register("auth/token/refresh", TokenRefreshViewSet, basename="token-refresh")
router.register("auth/password", PasswordResetViewSet, basename="password-reset")
router.register("me", MeViewSet, basename="me")
router.register("companies", CompanyAccountViewSet, basename="company")
router.register("roles", OrganizationRoleViewSet, basename="organization-role")
router.register("team-members", TeamMemberViewSet, basename="team-member")
router.register("team-invitations", TeamInvitationViewSet, basename="team-invitation")
router.register("user-preferences", UserPreferenceViewSet, basename="user-preference")
router.register("user-activities", UserActivityViewSet, basename="user-activity")
router.register("security-events", SecurityEventViewSet, basename="security-event")
router.register("api-tokens", UserApiTokenViewSet, basename="api-token")
router.register("departments", DepartmentViewSet, basename="department")
router.register("address-book", AddressBookEntryViewSet, basename="address-book-entry")
router.register("branches", BranchViewSet, basename="branch")
router.register("addresses", OrganizationAddressViewSet, basename="organization-address")
router.register("settings", OrganizationSettingsViewSet, basename="organization-settings")
router.register("supplier-verifications", SupplierVerificationViewSet, basename="supplier-verification")
router.register("buyer-verifications", BuyerVerificationViewSet, basename="buyer-verification")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]
