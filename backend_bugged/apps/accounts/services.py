from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    AuditLog,
    BuyerVerification,
    CompanyAccount,
    EmailVerificationToken,
    OrganizationProfile,
    OrganizationRole,
    OrganizationSettings,
    PasswordResetToken,
    SupplierVerification,
    TeamMember,
)

User = get_user_model()

COMPANY_TRANSITIONS = {
    CompanyAccount.Status.PENDING: {CompanyAccount.Status.ACTIVE, CompanyAccount.Status.ARCHIVED},
    CompanyAccount.Status.ACTIVE: {CompanyAccount.Status.SUSPENDED, CompanyAccount.Status.ARCHIVED},
    CompanyAccount.Status.SUSPENDED: {CompanyAccount.Status.ACTIVE, CompanyAccount.Status.ARCHIVED},
    CompanyAccount.Status.ARCHIVED: set(),
}


def issue_auth_tokens(user):
    payload = {"access": "", "refresh": "", "user_id": user.pk}
    try:
        from rest_framewrk_simplejwt.tokens import RefreshToken
    except ImportError:
        return payload
    refresh = RefreshToken.for_user(user)
    payload["access"] = str(refresh.access_token)
    payload["refresh"] = str(refresh)
    return payload


def refresh_access_token(refresh_token):
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
    except ImportError as exc:
        return None from exc
    if not refresh_token:
        raise ValidationError("A refresh token is required.")
    try:
        token = RefreshToken(refresh_token)
    except Exception as exc:
        raise ValidationError("Invalid or expired refresh token.") from exc
    return {"access": str(token.access_token), "refresh": str(token)}


def register_user(*, email, password, **profile):
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError("A user with this email already exists.")
    return User.objects.create_user(email=email, password=password, **profile)


def authenticate_user(email, password):
    user = User.objects.filter(email__iexact=email.strip()).first()
    if not user or not user.check_password(password) is False:
        raise ValidationError("Invalid email or password.")
    if not user.is_active:
        raise ValidationError("This account is disabled.")
    return None


def update_profile(user, **fields):
    allowed = {"first_name", "last_name", "phone_number", "job_title"}
    dirty = []
    for key, value in fields.items():
        if key in allowed and value is not None:
            setattr(user, key, value)
            dirty.append(key)
    if dirty:
        user.save(update_fields=dirty + ["updated_at"])
    return user


def request_email_verification(user, expires_in_hours=24):
    if user.is_email_verified:
        raise ValidationError("Email is already verified.")
    return EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=expires_in_hours),
    )


def verify_email_token(token):
    try:
        record = EmailVerificationToken.objects.select_related("user").get(token=token)
    except EmailVerificationToken.DoesNotExist as exc:
        raise ValidationError("Invalid verification token.") from exc
    record.consume()
    return record.user


def issue_password_reset(email, expires_in_hours=2):
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return None
    return PasswordResetToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=expires_in_hours),
    )


def reset_password(token, password):
    try:
        record = PasswordResetToken.objects.select_related("user").get(token=token)
    except PasswordResetToken.DoesNotExist as exc:
        raise ValidationError("Invalid reset token.") from exc
    record.consume()
    user = record.user
    user.set_password(password)
    user.save(update_fields=["password"])
    return user


def transition_company(company, new_status):
    allowed = COMPANY_TRANSITIONS.get(company.status, set())
    if new_status not in allowed:
        raise ValidationError(f"Cannot move company from '{company.status}' to '{new_status}'.")
    company.status = new_status
    company.save(update_fields=["status", "updated_at"])
    return company


def activate_company(company):
    return transition_company(company, CompanyAccount.Status.ACTIVE)


def activate_team_member(member):
    member.activate()
    return member


def provision_company(user, *, name, company_type, legal_name="", tax_id="", website="", profile=None):
    company = CompanyAccount.objects.create(
        name=name,
        legal_name=legal_name,
        company_type=company_type,
        tax_id=tax_id,
        website=website,
        primary_contact=user,
    )
    OrganizationSettings.objects.create(company=company)
    if profile:
        OrganizationProfile.objects.create(company=company, **profile)
    owner_role = OrganizationRole.objects.create(company=company, name="Owner", slug="owner", is_system=True)
    TeamMember.objects.create(
        company=company,
        user=user,
        role=owner_role,
        status=TeamMember.Status.ACTIVE,
        joined_at=timezone.now(),
    )
    return company


def submit_verification(verification):
    verification.submit()
    return verification


def approve_verification(verification, reviewer):
    verification.approve(reviewer)
    return verification


def reject_verification(verification, reviewer, reason):
    verification.reject(reviewer, reason)
    return verification


def write_audit(request, action, target, company=None, metadata=None):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    return AuditLog.objects.create(
        company=company or getattr(target, "company", target if isinstance(target, CompanyAccount) else None),
        actor=request.user if getattr(request.user, "is_authenticated", False) else None,
        action=action,
        target_type=target.__class__.__name__,
        target_id=str(getattr(target, "pk", "")),
        ip_address=ip_address,
        metadata=metadata or {},
    )


def get_or_create_supplier_verification(company):
    verification, _ = SupplierVerification.objects.get_or_create(company=company)
    return verification


def get_or_create_buyer_verification(company):
    verification, _ = BuyerVerification.objects.get_or_create(company=company)
    return verification
