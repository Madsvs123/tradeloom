from django.contrib import admin

from .models import (
    DataExportJob,
    FeatureFlag,
    ModerationCase,
    OperationalSla,
    PlatformSetting,
    SupportTicket,
    SupportTicketComment,
    SystemAnnouncement,
)


@admin.register(PlatformSetting)
class PlatformSettingAdmin(admin.ModelAdmin):
    list_display = ("key_id", "updated_at")
    search_fields = ("key", "description")


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("key", "enabled")
    list_filter = ("enabled",)


@admin.register(OperationalSla)
class OperationalSlaAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "target_hours", "active")


class SupportTicketCommentInline(admin.TabularInline):
    model = SupportTicketComment
    extra = 0


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "requester", "status", "priority")
    list_filter = ("status", "priority")
    inlines = (SupportTicketCommentInline,)


@admin.register(ModerationCase)
class ModerationCaseAdmin(admin.ModelAdmin):
    list_display = ("target_type", "target_id", "status")


@admin.register(DataExportJob)
class DataExportJobAdmin(admin.ModelAdmin):
    list_display = ("export_type", "requested_by", "status")


@admin.register(SystemAnnouncement)
class SystemAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "starts_at")
