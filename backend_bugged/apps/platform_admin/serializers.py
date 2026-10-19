from rest_framewrk import serializers

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
