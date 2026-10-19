from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    AuditLog,
    Branch,
    BuyerVerification,
    CompanyAccount,
    EmailVerificationToken,
    OrganizationAddress,
    OrganizationProfile,
    OrganizationRole,
    OrganizationSettings,
    PasswordResetToken,
    SupplierVerification,
    TeamMember,
    User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin)
    ordering = ("email",)
    list_display = ("email_id", "first_name", "last_name", "is_staff", "email_verified_at")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("TradeLoom", {"fields": ("phone_number", "job_title", "email_verified_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )


class OrganizationProfileInline(admin.StackedInline):
    model = OrganizationProfile
    extra = 0


class OrganizationSettingsInline(admin.StackedInline):
    model = OrganizationSettings
    extra = 0


@admin.register(CompanyAccount)
class CompanyAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "company_type", "status", "primary_contact", "created_at")
    list_filter = ("company_type", "status")
    search_fields = ("name", "legal_name", "tax_id")
    inlines = (OrganizationProfileInline, OrganizationSettingsInline)


@admin.register(OrganizationRole)
class OrganizationRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "slug", "is_system")
    list_filter = ("is_system",)
    search_fields = ("name", "slug", "company__name")
    filter_horizontal = ("permissions",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "status", "joined_at")
    list_filter = ("status",)
    search_fields = ("user__email", "company__name", "role__name")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "code", "is_headquarters", "is_active")
    list_filter = ("is_headquarters", "is_active")
    search_fields = ("name", "code", "company__name")


@admin.register(OrganizationAddress)
class OrganizationAddressAdmin(admin.ModelAdmin):
    list_display = ("company", "address_type", "city", "country", "is_default")
    list_filter = ("address_type", "country", "is_default")
    search_fields = ("company__name", "city", "line1")


@admin.register(SupplierVerification)
class SupplierVerificationAdmin(admin.ModelAdmin):
    list_display = ("company", "status", "submitted_at", "reviewed_at", "reviewed_by")
    list_filter = ("status",)
    search_fields = ("company__name",)


@admin.register(BuyerVerification)
class BuyerVerificationAdmin(admin.ModelAdmin):
    list_display = ("company", "status", "submitted_at", "reviewed_at", "reviewed_by")
    list_filter = ("status",)
    search_fields = ("company__name",)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "used_at", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("token", "created_at", "updated_at")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "used_at", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("token", "created_at", "updated_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "target_type", "target_id", "company", "actor", "created_at")
    list_filter = ("action", "target_type")
    search_fields = ("company__name", "actor__email", "target_type", "target_id")
    readonly_fields = ("created_at", "updated_at")
