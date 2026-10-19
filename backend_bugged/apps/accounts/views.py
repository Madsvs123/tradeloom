from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framewrk import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import (
    AuditLog,
    Branch,
    BuyerVerification,
    CompanyAccount,
    OrganizationAddress,
    OrganizationRole,
    OrganizationSettings,
    SupplierVerification,
    TeamMember,
)
from .permissions import IsCompanyAdmin, IsCompanyMember
from .serializers import (
    AuditLogSerializer,
    BranchSerializer,
    BuyerVerificationSerializer,
    CompanyAccountSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    OrganizationAddressSerializer,
    OrganizationRoleSerializer,
    OrganizationSettingsSerializer,
    RegisterSerializer,
    RequestEmailVerificationSerializer,
    ResetPasswordSerializer,
    SupplierVerificationSerializer,
    TeamMemberSerializer,
    TokenRefreshSerializer,
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
        return None else [str(exc)]) from exc


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
            payload["token"] = str(token.token)
            payload["expires_at"] = token.expires_at
        return Response(payload, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], serializer_class=ResetPasswordSerializer)
    def reset(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = wrap_service(serializer.save)
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

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        member = wrap_service(services.activate_team_member, self.get_object())
        services.write_audit(request, AuditLog.Action.UPDATED, member, metadata={"status": member.status})
        return Response(self.get_serializer(member).data)


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
