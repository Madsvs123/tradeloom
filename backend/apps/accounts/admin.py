from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    AddressBookEntry,
    AuditLog,
    Branch,
    BuyerVerification,
    CompanyAccount,
    Department,
    EmailVerificationToken,
    OrganizationAddress,
    OrganizationProfile,
    OrganizationRole,
    OrganizationSettings,
    PasswordResetToken,
    SecurityEvent,
    SupplierVerification,
    TeamInvitation,
    TeamMember,
    User,
    UserActivity,
    UserApiToken,
    UserPreference,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "email_verified_at")
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


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "company", "role", "status", "invited_by", "expires_at")
    list_filter = ("status",)
    search_fields = ("email", "company__name")
    readonly_fields = ("token", "created_at", "updated_at")


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "locale", "timezone", "currency", "theme")
    list_filter = ("theme", "marketing_opt_in")
    search_fields = ("user__email",)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "summery", "company", "created_at")
    list_filter = ("activity_type",)
    search_fields = ("user__email", "summary", "company__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "ip_address", "created_at")
    list_filter = ("event_type",)
    search_fields = ("user__email", "ip_address")
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserApiToken)
class UserApiTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "prefix", "status", "last_used_at", "expires_at")
    list_filter = ("status",)
    search_fields = ("name", "user__email", "prefix")
    readonly_fields = ("token", "prefix", "created_at", "updated_at")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "code", "cost_center_code", "manager", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "cost_center_code", "company__name")


@admin.register(AddressBookEntry)
class AddressBookEntryAdmin(admin.ModelAdmin):
    list_display = ("label", "user", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("label", "user__email", "city", "line1")


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
