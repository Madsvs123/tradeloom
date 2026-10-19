from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import (
    AuditLog,
    Branch,
    BuyerVerification,
    CompanyAccount,
    OrganizationAddress,
    OrganizationProfile,
    OrganizationRole,
    OrganizationSettings,
    SupplierVerification,
    TeamMember,
)
from . import services

User = get_user_model()


class UserSerializer(serializers.ModelSerializer)
    is_email_verified = serializers.BooleanField(read_only=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "job_title",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = ("id", "is_email_verified", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "phone_number", "job_title")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        return services.register_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = services.authenticate_user(attrs["email"], attrs["password"])
        attrs["user"] = user
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        return services.refresh_access_token(self.validated_data["refresh"])


class RequestEmailVerificationSerializer(serializers.Serializer):
    expires_in_hours = serializers.IntegerField(min_value=1, max_value=168, default=24)

    def save(self, **kwargs):
        return services.request_email_verification(
            self.context["request"].user,
            expires_in_hours=self.validated_data["expires_in_hours"],
        )


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def save(self, **kwargs):
        return services.verify_email_token(self.validated_data["token"])


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    expires_in_hours = serializers.IntegerField(min_value=1, max_value=48, default=2)

    def save(self, **kwargs):
        return services.issue_password_reset(
            self.validated_data["email"],
            expires_in_hours=self.validated_data["expires_in_hours"],
        )


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def save(self, **kwargs):
        return services.reset_password(self.validated_data["token"], self.validated_data["password"])


class OrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = ()
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyAccountSerializer(serializers.ModelSerializer):
    profile = OrganizationProfileSerializer(required=False)

    class Meta:
        model = CompanyAccount
        fields = (
            "id",
            "name",
            "legal_name",
            "company_type",
            "status",
            "tax_id",
            "website",
            "primary_contact",
            "profile",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "primary_contact", "created_at", "updated_at")

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)
        user = self.context["request"].user
        return services.provision_company(user, profile=profile_data, **validated_data)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        instance = super().update(instance, validated_data)
        if profile_data is not None:
            OrganizationProfile.objects.update_or_create(company=instance, defaults=profile_data)
        return instance


class OrganizationRoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        source="permissions",
        many=True,
        queryset=Permission.objects.all(),
        required=False,
    )

    class Meta:
        model = OrganizationRole
        fields = (
            "id",
            "company",
            "name",
            "slug",
            "description",
            "permission_ids",
            "is_system",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_system", "created_at", "updated_at")


class TeamMemberSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source="user", read_only=True)

    class Meta:
        model = TeamMember
        fields = (
            "id",
            "company",
            "user",
            "user_detail",
            "role",
            "status",
            "invited_by",
            "joined_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "invited_by", "joined_at", "created_at", "updated_at")


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationAddress
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSettings
        fields = "__all__"
        read_only_fields = ("id", "company", "created_at", "updated_at")


class SupplierVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierVerification
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "created_at",
            "updated_at",
        )


class BuyerVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerVerification
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "created_at",
            "updated_at",
        )


class VerificationReviewSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class AuditLogSerializer(serializers.ModelSerializer):
    actor_detail = UserSerializer(source="actor", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "company",
            "actor",
            "actor_detail",
            "action",
            "target_type",
            "target_id",
            "ip_address",
            "metadata",
            "created_at",
        )
        read_only_fields = fields
