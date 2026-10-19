from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import (
    AddressBookEntry,
    AuditLog,
    Branch,
    BuyerVerification,
    CompanyAccount,
    Department,
    OrganizationAddress,
    OrganizationRole,
    OrganizationSettings,
    SecurityEvent,
    SupplierVerification,
    TeamInvitation,
    TeamMember,
    UserActivity,
    UserApiToken,
)
from .permissions import IsCompanyAdmin, IsCompanyMember
from .serializers import (
    AddressBookEntrySerializer,
    AuditLogSerializer,
    BranchSerializer,
    BuyerVerificationSerializer,
    CompanyAccountSerializer,
    DepartmentSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    OrganizationAddressSerializer,
    OrganizationRoleSerializer,
    OrganizationSettingsSerializer,
    RegisterSerializer,
    RequestEmailVerificationSerializer,
    ResetPasswordSerializer,
    SecurityEventSerializer,
    SupplierVerificationSerializer,
    TeamInvitationSerializer,
    TeamMemberSerializer,
    TokenRefreshSerializer,
    UserActivitySerializer,
    UserApiTokenSerializer,
    UserPreferenceSerializer,
    UserSerializer,
    VerificationReviewSerializer,
    VerifyEmailSerializer,
)
from . import services

User = get_user_model()


def wrap_service(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise ValidationError(exc.messages if hasattr(exc, "messages") else [str(exc)]) from exc


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = wrap_service(serializer.save)
        payload = services.issue_auth_tokens(user)
        payload["user"] = UserSerializer(user).data
        return Response(payload, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        services.record_security_event(user, SecurityEvent.EventType.LOGIN_SUCCESS, request=request)
        services.record_user_activity(
            user, UserActivity.ActivityType.LOGIN, "Signed in", request=request
        )
        payload = services.issue_auth_tokens(user)
        payload["user"] = UserSerializer(user).data
        return Response(payload)

    def list(self, request):
        return Response({"detail": "POST email and password to authenticate."})


class PasswordResetViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    @action(detail=True, methods=["post"], serializer_class=ForgotPasswordSerializer)
    def forgot(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = wrap_service(serializer.save)
        payload = {"detail": "If the account exists, a reset token was issued."}
        if token is not None:
            services.record_security_event(token.user, SecurityEvent.EventType.PASSWORD_RESET_REQUESTED, request=request)
            payload["token"] = str(token.token)
            payload["expires_at"] = token.expires_at
        return Response(payload, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], serializer_class=ResetPasswordSerializer)
    def reset(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = wrap_service(serializer.save)
        services.record_security_event(user, SecurityEvent.EventType.PASSWORD_RESET_COMPLETED, request=request)
        return Response(UserSerializer(user).data)


class TokenRefreshViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TokenRefreshSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(wrap_service(serializer.save))

    def list(self, request):
        return Response({"detail": "POST a refresh token to rotate access tokens."})


class MeViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def list(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=["patch"])
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = wrap_service(services.update_profile, request.user, **serializer.validated_data)
        services.record_user_activity(
            user, UserActivity.ActivityType.PROFILE_UPDATED, "Profile updated", request=request
        )
        return Response(UserSerializer(user).data)

    @action(detail=False, methods=["post"], serializer_class=RequestEmailVerificationSerializer)
    def request_email_verification(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        token = wrap_service(serializer.save)
        return Response({"token": str(token.token), "expires_at": token.expires_at}, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["post"],
        serializer_class=VerifyEmailSerializer,
        permission_classes=[permissions.AllowAny],
    )
    def verify_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = wrap_service(serializer.save)
        services.record_security_event(user, SecurityEvent.EventType.EMAIL_VERIFIED, request=request)
        return Response(UserSerializer(user).data)


class CompanyScopedViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsCompanyMember)

    def get_permissions(self):
        if self.action in ("approve", "reject"):
            return [permissions.IsAdminUser()]
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsCompanyMember(), IsCompanyAdmin()]
        return super().get_permissions()

    def filter_for_user_companies(self, queryset):
        return queryset.filter(
            company__team_members__user=self.request.user,
            company__team_members__status=TeamMember.Status.ACTIVE,
        ).distinct()

    def assert_create_allowed(self, serializer):
        company = serializer.validated_data.get("company")
        if company and not TeamMember.objects.filter(
            company=company,
            user=self.request.user,
            status=TeamMember.Status.ACTIVE,
            role__slug__in=("owner", "admin"),
        ).exists():
            raise PermissionDenied("Company administrator permission is required.")

    def perform_create(self, serializer):
        self.assert_create_allowed(serializer)
        instance = serializer.save()
        services.write_audit(self.request, AuditLog.Action.CREATED, instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        services.write_audit(self.request, AuditLog.Action.UPDATED, instance)

    def perform_destroy(self, instance):
        services.write_audit(self.request, AuditLog.Action.DELETED, instance)
        instance.delete()


class CompanyAccountViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyAccountSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return CompanyAccount.objects.filter(
            team_members__user=self.request.user,
            team_members__status=TeamMember.Status.ACTIVE,
        ).distinct()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy", "activate"):
            return [permissions.IsAuthenticated(), IsCompanyAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        company = serializer.save()
        services.write_audit(self.request, AuditLog.Action.CREATED, company)
        services.record_user_activity(
            self.request.user,
            UserActivity.ActivityType.COMPANY_CREATED,
            f"Created company {company.name}",
            company=company,
            target=company,
            request=self.request,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsCompanyAdmin])
    def activate(self, request, pk=None):
        company = wrap_service(services.activate_company, self.get_object())
        services.write_audit(request, AuditLog.Action.UPDATED, company, metadata={"status": company.status})
        return Response(self.get_serializer(company).data)


class OrganizationRoleViewSet(CompanyScopedViewSet):
    serializer_class = OrganizationRoleSerializer

    def get_queryset(self):
        return self.filter_for_user_companies(
            OrganizationRole.objects.select_related("company").prefetch_related("permissions")
        )


class TeamMemberViewSet(CompanyScopedViewSet):
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        return self.filter_for_user_companies(TeamMember.objects.select_related("company", "user", "role"))

    def perform_create(self, serializer):
        self.assert_create_allowed(serializer)
        member = serializer.save(invited_by=self.request.user)
        services.write_audit(self.request, AuditLog.Action.INVITED, member)
        services.record_user_activity(
            self.request.user,
            UserActivity.ActivityType.TEAM_MEMBER_ADDED,
            f"Added {member.user.email} to {member.company.name}",
            company=member.company,
            target=member,
            request=self.request,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        member = wrap_service(services.activate_team_member, self.get_object())
        services.write_audit(request, AuditLog.Action.UPDATED, member, metadata={"status": member.status})
        return Response(self.get_serializer(member).data)


class TeamInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = TeamInvitationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return TeamInvitation.objects.filter(
            Q(company__team_members__user=self.request.user, company__team_members__status=TeamMember.Status.ACTIVE)
            | Q(email__iexact=self.request.user.email)
        ).select_related("company", "role", "invited_by")

    def perform_create(self, serializer):
        company = serializer.validated_data.get("company")
        if company and not TeamMember.objects.filter(
            company=company,
            user=self.request.user,
            status=TeamMember.Status.ACTIVE,
            role__slug__in=("owner", "admin"),
        ).exists():
            raise PermissionDenied("Company administrator permission is required.")
        invitation = serializer.save(invited_by=self.request.user)
        services.write_audit(self.request, AuditLog.Action.INVITED, invitation)
        services.record_user_activity(
            self.request.user,
            UserActivity.ActivityType.TEAM_INVITED,
            f"Invited {invitation.email} to {invitation.company.name}",
            company=invitation.company,
            target=invitation,
            request=self.request,
        )

    @action(detail=True, methods=["get"])
    def accept(self, request, pk=None):
        member = wrap_service(services.accept_team_invitation, self.get_object(), request.user)
        services.write_audit(
            request, AuditLog.Action.UPDATED, self.get_object(), metadata={"status": "accepted"}
        )
        return Response(TeamMemberSerializer(member).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        invitation = wrap_service(services.decline_team_invitation, self.get_object())
        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        invitation = wrap_service(services.revoke_team_invitation, self.get_object())
        services.write_audit(request, AuditLog.Action.UPDATED, invitation, metadata={"status": "revoked"})
        return Response(self.get_serializer(invitation).data)


class UserPreferenceViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return services.get_or_create_user_preferences(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        preferences = wrap_service(services.update_user_preferences, request.user, **serializer.validated_data)
        return Response(self.get_serializer(preferences).data)


class UserActivityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = UserActivity.objects.select_related("user", "company")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class SecurityEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SecurityEventSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return SecurityEvent.objects.filter(user=self.request.user).select_related("user")


class UserApiTokenViewSet(viewsets.ModelViewSet):
    serializer_class = UserApiTokenSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return UserApiToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        token = serializer.save(user=self.request.user)
        services.record_security_event(
            self.request.user, SecurityEvent.EventType.API_TOKEN_ISSUED, request=self.request
        )
        services.record_user_activity(
            self.request.user,
            UserActivity.ActivityType.API_TOKEN_ISSUED,
            f"Issued API token '{token.name}'",
            target=token,
            request=self.request,
        )

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        token = wrap_service(services.revoke_api_token, self.get_object())
        services.record_security_event(
            request.user, SecurityEvent.EventType.API_TOKEN_REVOKED, request=request
        )
        return Response(self.get_serializer(token).data)


class DepartmentViewSet(CompanyScopedViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return self.filter_for_user_companies(
            Department.objects.select_related("company", "manager", "parent")
        )


class AddressBookEntryViewSet(viewsets.ModelViewSet):
    serializer_class = AddressBookEntrySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return AddressBookEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        entry = serializer.save(user=self.request.user)
        services.set_default_address_book_entry(self.request.user, entry)

    def perform_update(self, serializer):
        entry = serializer.save()
        services.set_default_address_book_entry(self.request.user, entry)


class BranchViewSet(CompanyScopedViewSet):
    serializer_class = BranchSerializer

    def get_queryset(self):
        return self.filter_for_user_companies(Branch.objects.select_related("company"))


class OrganizationAddressViewSet(CompanyScopedViewSet):
    serializer_class = OrganizationAddressSerializer

    def get_queryset(self):
        return self.filter_for_user_companies(OrganizationAddress.objects.select_related("company", "branch"))


class OrganizationSettingsViewSet(CompanyScopedViewSet):
    serializer_class = OrganizationSettingsSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return self.filter_for_user_companies(OrganizationSettings.objects.select_related("company"))


class SupplierVerificationViewSet(CompanyScopedViewSet):
    serializer_class = SupplierVerificationSerializer

    def get_queryset(self):
        qs = SupplierVerification.objects.select_related("company", "reviewed_by")
        if self.action in ("approve", "reject") and self.request.user.is_staff:
            return qs
        return self.filter_for_user_companies(qs)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        verification = wrap_service(services.submit_verification, self.get_object())
        services.write_audit(request, AuditLog.Action.UPDATED, verification, metadata={"status": verification.status})
        return Response(self.get_serializer(verification).data)

    @action(
        detail=True,
        methods=["post"],
        serializer_class=VerificationReviewSerializer,
        permission_classes=[permissions.IsAdminUser],
    )
    def approve(self, request, pk=None):
        verification = wrap_service(services.approve_verification, self.get_object(), request.user)
        services.write_audit(request, AuditLog.Action.VERIFIED, verification, metadata={"status": verification.status})
        return Response(SupplierVerificationSerializer(verification).data)

    @action(
        detail=True,
        methods=["post"],
        serializer_class=VerificationReviewSerializer,
        permission_classes=[permissions.IsAdminUser],
    )
    def reject(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = wrap_service(
            services.reject_verification,
            self.get_object(),
            request.user,
            serializer.validated_data.get("reason", ""),
        )
        services.write_audit(request, AuditLog.Action.UPDATED, verification, metadata={"status": verification.status})
        return Response(SupplierVerificationSerializer(verification).data)


class BuyerVerificationViewSet(SupplierVerificationViewSet):
    serializer_class = BuyerVerificationSerializer

    def get_queryset(self):
        qs = BuyerVerification.objects.select_related("company", "reviewed_by")
        if self.action in ("approve", "reject") and self.request.user.is_staff:
            return qs
        return self.filter_for_user_companies(qs)

    @action(
        detail=True,
        methods=["post"],
        serializer_class=VerificationReviewSerializer,
        permission_classes=[permissions.IsAdminUser],
    )
    def approve(self, request, pk=None):
        verification = wrap_service(services.approve_verification, self.get_object(), request.user)
        services.write_audit(request, AuditLog.Action.VERIFIED, verification, metadata={"status": verification.status})
        return Response(BuyerVerificationSerializer(verification).data)

    @action(
        detail=True,
        methods=["post"],
        serializer_class=VerificationReviewSerializer,
        permission_classes=[permissions.IsAdminUser],
    )
    def reject(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = wrap_service(
            services.reject_verification,
            self.get_object(),
            request.user,
            serializer.validated_data.get("reason", ""),
        )
        services.write_audit(request, AuditLog.Action.UPDATED, verification, metadata={"status": verification.status})
        return Response(BuyerVerificationSerializer(verification).data)


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            AuditLog.objects.filter(
                Q(
                    company__team_members__user=self.request.user,
                    company__team_members__status=TeamMember.Status.ACTIVE,
                )
                | Q(actor=self.request.user)
            )
            .select_related("company", "actor")
            .distinct()
        )
