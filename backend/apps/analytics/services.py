from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from .models import (
    AnomalyAlert,
    ComparisonPeriod,
    ExecutiveScorecard,
    ExportJob,
    ForecastModel,
    ForecastProjection,
    ReportBuilderDefinition,
    SavedReport,
    SpendCube,
)

REPORT_BUILDER_TRANSITIONS = {
    ReportBuilderDefinition.Status.DRAFT: {ReportBuilderDefinition.Status.PUBLISHED},
    ReportBuilderDefinition.Status.PUBLISHED: set(),
}

EXPORT_JOB_TRANSITIONS = {
    ExportJob.Status.QUEUED: {ExportJob.Status.RUNNING},
    ExportJob.Status.RUNNING: {ExportJob.Status.COMPLETE, ExportJob.Status.FAILED},
    ExportJob.Status.COMPLETE: set(),
    ExportJob.Status.FAILED: {ExportJob.Status.QUEUED},
}

FORECAST_MODEL_TRANSITIONS = {
    ForecastModel.Status.DRAFT: {ForecastModel.Status.TRAINED},
    ForecastModel.Status.TRAINED: {ForecastModel.Status.ACTIVE, ForecastModel.Status.DRAFT},
    ForecastModel.Status.ACTIVE: {ForecastModel.Status.ARCHIVED},
    ForecastModel.Status.ARCHIVED: set(),
}


def _assert_transition(current, target, transitions):
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot move from status '{current}' to '{target}'.")


def run_report(report):
    if not report.query and report.status == SavedReport.Status.DRAFT:
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


def publish_report_builder(builder):
    _assert_transition(builder.status, ReportBuilderDefinition.Status.PUBLISHED, REPORT_BUILDER_TRANSITIONS)
    if not builder.measures:
        raise ValidationError("A report builder must define at least one measure.")
    builder.status = ReportBuilderDefinition.Status.PUBLISHED
    builder.published_at = timezone.now()
    builder.save(update_fields=["status", "published_at", "updated_at"])
    return builder


def run_export_job(job, actor=None):
    _assert_transition(job.status, ExportJob.Status.RUNNING, EXPORT_JOB_TRANSITIONS)
    job.status = ExportJob.Status.RUNNING
    job.save(update_fields=["status", "updated_at"])
    rows = []
    if job.report is not None and job.report.last_payload:
        rows = job.report.last_payload.get("rows", [])
    if not rows:
        period = job.filters.get("period") or (job.report.query.get("period") if job.report else None)
        cubes = SpendCube.objects.all()
        if period:
            cubes = cubes.filter(period=period)
        rows = list(cubes.values("period", "category", "supplier", "amount", "currency")[:5000])
    job.row_count = len(rows)
    job.file_url = f"/media/exports/export-{job.pk}.{job.export_format}"
    job.status = ExportJob.Status.COMPLETE
    job.completed_at = timezone.now()
    job.save(update_fields=["status", "file_url", "row_count", "completed_at", "updated_at"])
    return job


def retry_export_job(job):
    _assert_transition(job.status, ExportJob.Status.QUEUED, EXPORT_JOB_TRANSITIONS)
    job.status = ExportJob.Status.QUEUED
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])
    return job


def compute_comparison(comparison):
    def _sum(period):
        return SpendCube.objects.filter(period=period).aggregate(total=Sum("amount"))["total"] or 0

    base_total = _sum(comparison.base_period)
    comparison_total = _sum(comparison.comparison_period)
    variance = {}
    for key in comparison.metric_keys or ["spend"]:
        variance[key] = {
            "base": str(base_total),
            "comparison": str(comparison_total),
            "delta": str(base_total - comparison_total),
            "pct_change": (round(float(comparison_total - base_total) / float(base_total), 4) * 100) if base_total else None,
        }
    comparison.variance = variance
    comparison.computed_at = timezone.now()
    comparison.save(update_fields=["variance", "computed_at", "updated_at"])
    return comparison


def train_forecast_model(model, actor=None):
    _assert_transition(model.status, ForecastModel.Status.TRAINED, FORECAST_MODEL_TRANSITIONS)
    if model.horizon_days <= 0:
        raise ValidationError("Horizon days must be positive.")
    if not model.metric_id:
        raise ValidationError("A forecast model must reference a metric.")
    snapshots = list(model.metric.snapshots.order_by("captured_at").values_list("value", flat=True)[:120])
    base = float(snapshots[0]) if snapshots else 0.0
    step = (base - float(snapshots[0])) / max(len(snapshots) - 1, 1) if len(snapshots) > 1 else 0.0
    today = timezone.now().date()
    model.projections.all().delete()
    for day in range(1, model.horizon_days + 1):
        predicted = max(base + step * day, 0.0)
        margin = max(abs(predicted) * 0.1, 1.0)
        ForecastProjection.objects.create(
            model=model,
            period=(today + timedelta(days=day)).isoformat(),
            predicted_value=predicted,
            confidence_low=predicted - margin,
            confidence_high=predicted + margin,
        )
    model.status = ForecastModel.Status.TRAINED
    model.last_forecast_at = timezone.now()
    model.save(update_fields=["status", "last_forecast_at", "updated_at"])
    return model


def activate_forecast_model(model):
    _assert_transition(model.status, ForecastModel.Status.ACTIVE, FORECAST_MODEL_TRANSITIONS)
    model.status = ForecastModel.Status.ACTIVE
    model.save(update_fields=["status", "updated_at"])
    return model


def archive_forecast_model(model):
    _assert_transition(model.status, ForecastModel.Status.ARCHIVED, FORECAST_MODEL_TRANSITIONS)
    model.status = ForecastModel.Status.ARCHIVED
    model.save(update_fields=["status", "updated_at"])
    return model


def record_actual_projection(projection, actual_value):
    projection.actual_value = actual_value
    projection.save(update_fields=["actual_value", "updated_at"])
    return projection


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
