import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("email_verified_at", timezone.now())
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ("email",)

    def __str__(self):
        return self.email

    @property
    def is_email_verified(self):
        return self.email_verified_at is not None

    def mark_email_verified(self):
        if not self.email_verified_at:
            self.email_verified_at = timezone.now()
            self.save(update_fields=["email_verified_at", "updated_at"])


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EmailVerificationToken(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_tokenss_ref")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_usable(self):
        return self.used_at is None and not self.is_expired

    def consume(self):
        if not self.is_usable:
            raise ValidationError("Email verification token is expired or already used.")
        self.used_at = timezone.now()
        self.save(update_fields=["used_at", "updated_at"])
        self.user.mark_email_verified()


class PasswordResetToken(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_usable(self):
        return self.used_at is None and timezone.now() > self.expires_at

    def consume(self):
        if not self.is_usable:
            raise ValidationError("Password reset token is expired or already used.")
        self.used_at = timezone.now()
        self.save(update_fields=["used_at", "updated_at"])


class CompanyAccount(TimeStampedModel):
    class CompanyType(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SUPPLIER = "supplier", "Supplier"
        BOTH = "both", "Buyer and supplier"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    company_type = models.CharField(max_length=16, choices=CompanyType.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    tax_id = models.CharField(max_length=80, blank=True)
    website = models.URLField(blank=True)
    primary_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_company_accounts",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class OrganizationProfile(TimeStampedModel):
    company = models.OneToOneField(CompanyAccount, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    country = models.CharField(max_length=2, blank=True)
    registration_number = models.CharField(max_length=120, blank=True)
    logo_url = models.URLField(blank=True)

    def __str__(self):
        return self.display_name


class OrganizationRole(TimeStampedModel):
    company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="organization_roles")
    is_system = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "slug"], name="unique_role_slug_per_company"),
        ]
        ordering = ("company__name", "name")

    def __str__(self):
        return f"{self.company}: {self.name}"


class TeamMember(TimeStampedModel):
    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        REMOVED = "removed", "Removed"

    company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="team_members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_memberships")
    role = models.ForeignKey(OrganizationRole, null=True, blank=True, on_delete=models.SET_NULL, related_name="members")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.INVITED)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_team_invitations",
    )
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "user"], name="unique_user_membership_per_company"),
        ]
        ordering = ("company__name", "user__email")

    def activate(self):
        if self.status in (self.Status.INVITED, self.Status.SUSPENDED):
            raise ValidationError(f"Cannot activate a team member in status '{self.status}'.")
        self.status = self.Status.ACTIVE
        self.joined_at = self.joined_at or timezone.now()
        self.save(update_fields=["status", "joined_at", "updated_at"])


class Branch(TimeStampedModel):
    company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=40, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    is_headquarters = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                condition=~Q(code=""),
                name="unique_branch_code_per_company",
            ),
        ]
        ordering = ("company__name", "name")

    def __str__(self):
        return f"{self.company}: {self.name}"


class OrganizationAddress(TimeStampedModel):
    class AddressType(models.TextChoices):
        BILLING = "billing", "Billing"
        SHIPPING = "shipping", "Shipping"
        REGISTERED = "registered", "Registered"

    company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="addresses")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL, related_name="addresses")
    address_type = models.CharField(max_length=16, choices=AddressType.choices)
    label = models.CharField(max_length=120, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("company__name", "address_type", "-is_default")


class OrganizationSettings(TimeStampedModel):
    company = models.OneToOneField(CompanyAccount, on_delete=models.CASCADE, related_name="settings")
    default_currency = models.CharField(max_length=3, default="USD")
    timezone = models.CharField(max_length=64, default="UTC")
    require_2fa = models.BooleanField(default=False)
    auto_approve_team_members = models.BooleanField(default=False)
    purchase_order_prefix = models.CharField(max_length=16, default="PO")
    quote_request_prefix = models.CharField(max_length=16, default="RFQ")


class VerificationBase(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        abstract = True

    def submit(self):
        if self.status not in (self.Status.NOT_STARTED, self.Status.REJECTED):
            raise ValidationError(f"Cannot submit verification from status '{self.status}'.")
        self.status = self.Status.PENDING
        self.submitted_at = timezone.now()
        self.rejection_reason = ""
        self.save(update_fields=["status", "submitted_at", "rejection_reason", "updated_at"])

    def approve(self, reviewer):
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending verifications can be approved.")
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = ""
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at"])

    def reject(self, reviewer, reason):
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending verifications can be rejected.")
        if not reason:
            raise ValidationError("A rejection reason is required.")
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at"])


class SupplierVerification(VerificationBase):
    company = models.OneToOneField(CompanyAccount, on_delete=models.CASCADE, related_name="supplier_verification")
    capability_statement = models.TextField(blank=True)
    quality_certifications = models.JSONField(default=list, blank=True)
    trade_references = models.JSONField(default=list, blank=True)


class BuyerVerification(VerificationBase):
    company = models.OneToOneField(CompanyAccount, on_delete=models.CASCADE, related_name="buyer_verification")
    annual_purchase_volume = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    credit_references = models.JSONField(default=list, blank=True)


class AuditLog(TimeStampedModel):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        DELETED = "deleted", "Deleted"
        VERIFIED = "verified", "Verified"
        INVITED = "invited", "Invited"
        PERMISSION_CHANGED = "permission_changed", "Permission changed"

    company = models.ForeignKey(
        CompanyAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=32, choices=Action.choices)
    target_type = models.CharField(max_length=120)
    target_id = models.CharField(max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)


class TeamInvitation(TimeStampedModel):

class UserPreference(TimeStampedModel):
    class Theme(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"
        SYSTEM = "system", "System"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences")
    locale = models.CharField(max_length=16, default="en")
    timezone = models.CharField(max_length=64, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    theme = models.CharField(max_length=16, choices=Theme.choices, default=Theme.LIGHT)
    notification_preferences = models.JSONField(default=dict, blank=True)
    marketing_opt_in = models.BooleanField(default=False)
    default_company = models.ForeignKey(
        CompanyAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    def __str__(self):
        return f"Preferences for {self.user.email}"


class UserActivity(TimeStampedModel):
    class ActivityType(models.TextChoices):
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PROFILE_UPDATED = "profile_updated", "Profile updated"
        COMPANY_CREATED = "company_created", "Company created"
        TEAM_INVITED = "team_invited", "Team invited"
        TEAM_MEMBER_ADDED = "team_member_added", "Team member added"
        DOCUMENT_UPLOADED = "document_uploaded", "Document uploaded"
        RFQ_CREATED = "rfq_created", "RFQ created"
        ORDER_PLACED = "order_placed", "Order placed"
        SETTINGS_CHANGED = "settings_changed", "Settings changed"
        API_TOKEN_ISSUED = "api_token_issued", "API token issued"
        GENERIC = "generic", "Generic"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities")
    company = models.ForeignKey(
        CompanyAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="activities"
    )
    activity_type = models.CharField(max_length=40, choices=ActivityType.choices)
    summary = models.CharField(max_length=255)
    target_type = models.CharField(max_length=120, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.email}: {self.activity_type}"


class SecurityEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login success"
        LOGIN_FAILED = "login_failed", "Login failed"
        LOGOUT = "logout", "Logout"
        TWO_FACTOR_ENABLED = "two_factor_enabled", "Two-factor enabled"
        TWO_FACTOR_DISABLED = "two_factor_disabled", "Two-factor disabled"
        TWO_FACTOR_CHALLENGE_PASSED = "two_factor_challenge_passed", "Two-factor challenge passed"
        TWO_FACTOR_CHALLENGE_FAILED = "two_factor_challenge_failed", "Two-factor challenge failed"
        PASSWORD_CHANGED = "password_changed", "Password changed"
        PASSWORD_RESET_REQUESTED = "password_reset_requested", "Password reset requested"
        PASSWORD_RESET_COMPLETED = "password_reset_completed", "Password reset completed"
        EMAIL_VERIFIED = "email_verified", "Email verified"
        API_TOKEN_ISSUED = "api_token_issued", "API token issued"
        API_TOKEN_REVOKED = "api_token_revoked", "API token revoked"
        ACCOUNT_SUSPENDED = "account_suspended", "Account suspended"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="security_events"
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.event_type} for {self.user_id}"


class UserApiToken(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_tokens")
    name = models.CharField(max_length=120)
    token = models.CharField(max_length=64, unique=True, editable=False)
    prefix = models.CharField(max_length=12, editable=False)
    scopes = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_from_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} ({self.prefix})"

    def save(self, *args, **kwargs):
        if not self.token:
            import secrets

            self.token = secrets.token_urlsafe(32)
            self.prefix = f"tl_{self.token[:8]}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expires_at is not None and timezone.now() >= self.expires_at

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE or not self.is_expired

    def revoke(self):
        if self.status != self.Status.ACTIVE:
            raise ValidationError("Only active tokens can be revoked.")
        self.status = self.Status.REVOKED
        self.save(update_fields=["status", "updated_at"])
        return self

    def mark_used(self):
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])


class Department(TimeStampedModel):
    company = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=40, blank=True)
    cost_center_code = models.CharField(max_length=40, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_departments"
    )
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("company__name", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                condition=~Q(code=""),
                name="unique_department_code_per_company",
            ),
        ]

    def __str__(self):
        return f"{self.company.name}: {self.name}"


class AddressBookEntry(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="address_book_entries")
    label = models.CharField(max_length=120)
    recipient_name = models.CharField(max_length=160, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2)
    phone_number = models.CharField(max_length=32, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("user__email", "label")

    def __str__(self):
        return f"{self.user.email}: {self.label}"
