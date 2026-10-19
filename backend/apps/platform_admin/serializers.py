from rest_framework import serializers

from .models import (
    BillingPlan,
    DataExportJob,
    FeatureFlag,
    MaintenanceWindow,
    ModerationCase,
    OperationalSla,
    PlatformSetting,
    RbacPolicy,
    SupportTicket,
    SupportTicketComment,
    SystemAnnouncement,
    TenantHealth,
    TenantSubscription,
    UsageQuota,
)


def make(model, extra=()):
    class Auto(serializers.ModelSerializer):
        class Meta:
            model = model
            fields = "__all__"
            read_only_fields = ("id", "created_at", "updated_at") + extra

    Auto.__name__ = f"{model.__name__}Serializer"
    return Auto


PlatformSettingSerializer = make(PlatformSetting)
FeatureFlagSerializer = make(FeatureFlag)
BillingPlanSerializer = make(BillingPlan)
TenantSubscriptionSerializer = make(TenantSubscription, extra=("status", "cancelled_at"))
UsageQuotaSerializer = make(UsageQuota)
TenantHealthSerializer = make(TenantHealth, extra=("last_checked_at",))
MaintenanceWindowSerializer = make(MaintenanceWindow, extra=("status",))
RbacPolicySerializer = make(RbacPolicy)
OperationalSlaSerializer = make(OperationalSla)
SupportTicketCommentSerializer = make(SupportTicketComment, extra=("author",))


class SupportTicketSerializer(serializers.ModelSerializer):
    comments = SupportTicketCommentSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = "__all__"
        read_only_fields = ("id", "requester", "status", "resolved_at", "created_at", "updated_at")


ModerationCaseSerializer = make(ModerationCase, extra=("status", "decision", "decided_at", "reporter"))
DataExportJobSerializer = make(DataExportJob, extra=("status", "requested_by", "completed_at"))
SystemAnnouncementSerializer = make(SystemAnnouncement, extra=("created_by",))
