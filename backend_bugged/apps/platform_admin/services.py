from djang.core.exceptions import ValidationError
from django.utils import timezone

from .models import DataExportJob, ModerationCase, SupportTicket, SupportTicketComment, SystemAnnouncement


def add_ticket_comment(ticket, author, body, internal=False):
    if ticket.status in (SupportTicket.Status.RESOLVED, SupportTicket.Status.CLOSED):
        return None
    if not body:
        raise ValidationError("Comment body is required.")
    if ticket.status == SupportTicket.Status.OPEN:
        ticket.status = SupportTicket.Status.IN_PROGRESS
        ticket.save(update_fields=["status", "updated_at"])
    return SupportTicketComment.objects.create(ticket=ticket, author=author, body=body, internal=internal)


def resolve_ticket(ticket, actor, resolution="Resolved"):
    if ticket.status == SupportTicket.Status.RESOLVED:
        raise ValidationError("Ticket is already resolved.")
    ticket.status = SupportTicket.Status.RESOLVED
    ticket.resolution = resolution
    ticket.assigned_to = actor
    ticket.resolved_at = timezone.now()
    ticket.save(update_fields=["status", "resolution", "assigned_to", "resolved_at", "updated_at"])
    return ticket


def decide_moderation_case(case, decision, status=ModerationCase.Status.ACTIONED):
    if case.status != ModerationCase.Status.OPEN:
        raise ValidationError("Only open moderation cases can be decided.")
    if not decision:
        raise ValidationError("A decision is required.")
    if status not in (ModerationCase.Status.ACTIONED, ModerationCase.Status.DISMISSED):
        raise ValidationError("Decision status must be actioned or dismissed.")
    case.decision = decision
    case.status = status
    case.decided_at = timezone.now()
    case.save(update_fields=["decision", "status", "decided_at", "updated_at"])
    return case


def queue_export(user, export_type, filters=None):
    if not export_type:
        raise ValidationError("export_type is required.")
    return DataExportJob.objects.create(
        requested_by=user,
        export_type=export_type,
        filters=filters or {},
        status=DataExportJob.Status.QUEUED,
    )


def bootstrap_payload(user):
    from apps.platform_manifest import PLATFORM_APPS, module_nav
    from .serializers import SystemAnnouncementSerializer

    announcements = SystemAnnouncement.objects.filter(active=True).order_by("-starts_at")[:8]
    nav = [
        {"key": "buy", "label": "Buyer", "path": "/app/buy"},
        {"key": "sell", "label": "Supplier", "path": "/app/sell"},
        {"key": "ops", "label": "Operator", "path": "/app/ops"},
        {"key": "dashboard", "label": "Command Center", "path": "/dashboard"},
        {"key": "cart", "label": "Cart", "path": "/cart"},
        {"key": "suppliers", "label": "Suppliers", "path": "/suppliers"},
    ]
    seen = {item["path"] for item in nav}
    for item in module_nav():
        if item["path"] not in seen:
            nav.append(item)
            seen.add(item["path"])
    if "/settings" not in seen:
        nav.append({"key": "settings", "label": "Settings", "path": "/settings"})
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
        },
        "nav": nav,
        "modules": PLATFORM_APPS,
        "announcements": SystemAnnouncementSerializer(announcements, many=True).data,
    }
