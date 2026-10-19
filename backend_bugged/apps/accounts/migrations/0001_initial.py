import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q

import backend.apps.accounts.models


class Migration(migrations.Migration)
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(blank=True, max_length=150)),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("phone_number", models.CharField(blank=True, max_length=32)),
                ("job_title", models.CharField(blank=True, max_length=120)),
                ("email_verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(autonow_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to.", relate_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"ordering": ("email",)},
            managers=[
                ("objects", backend.apps.accounts.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="CompanyAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("legal_name", models.CharField(blank=True, max_length=255)),
                ("company_type", models.CharField(choices=[("buyer", "Buyer"), ("supplier", "Supplier"), ("both", "Buyer and supplier")], max_length=16)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("active", "Active"), ("suspended", "Suspended"), ("archived", "Archived")], default="pending", max_length=16)),
                ("tax_id", models.CharField(blank=True, max_length=80)),
                ("website", models.URLField(blank=True)),
                ("primary_contact", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="primary_company_accounts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action", models.CharField(choices=[("created", "Created"), ("updated", "Updated"), ("deleted", "Deleted"), ("verified", "Verified"), ("invited", "Invited"), ("permission_changed", "Permission changed")], max_length=32)),
                ("target_type", models.CharField(max_length=120)),
                ("target_id", models.CharField(blank=True, max_length=64)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("company", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="accounts.companyaccount")),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="Branch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("code", models.CharField(blank=True, max_length=40)),
                ("phone_number", models.CharField(blank=True, max_length=32)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("is_headquarters", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="branches", to="accounts.companyaccount")),
            ],
            options={"ordering": ("company__name", "name")},
        ),
        migrations.CreateModel(
            name="BuyerVerification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("not_started", "Not started"), ("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="not_started", max_length=20)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("rejection_reason", models.TextField(blank=True)),
                ("annual_purchase_volume", models.DecimalField(blank=True, decimalplaces=2, max_digits=14, null=True)),
                ("credit_references", models.JSONField(blank=True, default=list)),
                ("company", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="buyer_verification", to="accounts.companyaccount")),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="EmailVerificationToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="email_tokens", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="OrganizationProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("display_name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("industry", models.CharField(blank=True, max_length=120)),
                ("employee_count", models.PositiveIntegerField(blank=True, null=True)),
                ("country", models.CharField(blank=True, max_length=2)),
                ("registration_number", models.CharField(blank=True, max_length=120)),
                ("logo_url", models.URLField(blank=True)),
                ("company", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to="accounts.companyaccount")),
            ],
        ),
        migrations.CreateModel(
            name="OrganizationSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("default_currency", models.CharField(default="USD", max_length=3)),
                ("timezone", models.CharField(default="UTC", max_length=64)),
                ("require_2fa", models.BooleanField(default=False)),
                ("auto_approve_team_members", models.BooleanField(default=False)),
                ("purchase_order_prefix", models.CharField(default="PO", max_length=16)),
                ("quote_request_prefix", models.CharField(default="RFQ", max_length=16)),
                ("company", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="settings", to="accounts.companyaccount")),
            ],
        ),
        migrations.CreateModel(
            name="OrganizationRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80)),
                ("slug", models.SlugField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_system", models.BooleanField(default=False)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="roles", to="accounts.companyaccount")),
                ("permissions", models.ManyToManyField(blank=True, related_name="organization_roles", to="auth.permission")),
            ],
            options={"ordering": ("company__name", "name")},
        ),
        migrations.CreateModel(
            name="OrganizationAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("address_type", models.CharField(choices=[("billing", "Billing"), ("shipping", "Shipping")], max_length=16)),
                ("label", models.CharField(blank=True, max_length=120)),
                ("line1", models.CharField(max_length=255)),
                ("line2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("postal_code", models.CharField(blank=True, max_length=32)),
                ("country", models.CharField(max_length=2)),
                ("is_default", models.BooleanField(default=False)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="addresses", to="accounts.branch")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="addresses", to="accounts.companyaccount")),
            ],
            options={"ordering": ("company__name", "address_type", "-is_default")},
        ),
        migrations.CreateModel(
            name="SupplierVerification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("not_started", "Not started"), ("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="not_started", max_length=20)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("rejection_reason", models.TextField(blank=True)),
                ("capability_statement", models.TextField(blank=True)),
                ("quality_certifications", models.JSONField(blank=True, default=list)),
                ("trade_references", models.JSONField(blank=True, default=list)),
                ("company", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="supplier_verification", to="accounts.companyaccount")),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("invited", "Invited"), ("active", "Active"), ("suspended", "Suspended"), ("removed", "Removed")], default="invited", max_length=16)),
                ("joined_at", models.DateTimeField(blank=True, null=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="team_members", to="accounts.companyaccount")),
                ("invited_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sent_team_invitations", to=settings.AUTH_USER_MODEL)),
                ("role", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="members", to="accounts.organizationrole")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="company_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("company__name", "user__email")},
        ),
        migrations.AddConstraint(
            model_name="branch",
            constraint=models.UniqueConstraint(condition=~Q(code=""), fields=("company", "code"), name="unique_branch_code_per_company"),
        ),
        migrations.AddConstraint(
            model_name="organizationrole",
            constraint=models.UniqueConstraint(fields=("company", "slug"), name="unique_role_slug_per_company"),
        ),
        migrations.AddConstraint(
            model_name="teammember",
            constraint=models.UniqueConstraint(fields=("company", "user"), name="unique_user_membership_per_company"),
        ),
    ]
