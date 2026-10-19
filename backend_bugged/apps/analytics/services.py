from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from .models import AnomalyAlert, ExecutiveScorecard, SavedReport, SpendCube


def run_report(report)
    if not report.query and report.status = SavedReport.Status.DRAFT:
        report.query = {"source": "spend_cube"}
    period = report.query.get("period")
    cubes = SpendCube.objects.all()
    if period:
        cubes = cubes.filter(period=period)
    total = cubes.aggregate(amount=Sum("amount"))["amount"] or 0
    payload = {
        "period": period,
        "rows": list(cubes.values("period", "category", "supplier", "amount", "currency")[:200]),
        "total": str(total),
        "run_at": timezone.now().isoformat(),
    }
    report.last_payload = payload
    report.last_run_at = timezone.now()
    report.status = SavedReport.Status.READY
    report.save(update_fields=["last_payload", "last_run_at", "status", "query", "updated_at"])
    return report


def acknowledge_alert(alert):
    if alert.status != AnomalyAlert.Status.OPEN:
        raise ValidationError("Only open alerts can be acknowledged.")
    alert.status = AnomalyAlert.Status.ACKNOWLEDGED
    alert.acknowledged_at = timezone.now()
    alert.save(update_fields=["status", "acknowledged_at", "updated_at"])
    return alert


def resolve_alert(alert, note=""):
    if alert.status == AnomalyAlert.Status.RESOLVED:
        raise ValidationError("Alert is already resolved.")
    details = dict(alert.details or {})
    if note:
        details["resolution"] = note
    alert.details = details
    alert.status = AnomalyAlert.Status.RESOLVED
    alert.resolved_at = timezone.now()
    alert.save(update_fields=["details", "status", "resolved_at", "updated_at"])
    return alert


def scorecard_payload(scorecard):
    if not scorecard.payload:
        spend = SpendCube.objects.filter(period=scorecard.period).aggregate(amount=Sum("amount"))["amount"] or 0
        scorecard.payload = {"period": scorecard.period, "spend": str(spend), "kpis": []}
        scorecard.save(update_fields=["payload", "updated_at"])
    return scorecard.payload


def publish_scorecard(scorecard):
    if scorecard.status == ExecutiveScorecard.Status.PUBLISHED:
        raise ValidationError("Scorecard is already published.")
    scorecard_payload(scorecard)
    scorecard.status = ExecutiveScorecard.Status.PUBLISHED
    scorecard.published_at = timezone.now()
    scorecard.save(update_fields=["status", "published_at", "payload", "updated_at"])
    return scorecard
