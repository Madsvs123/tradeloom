import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buyerverification",
            name="annual_purchase_volume",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.CreateModel(
            name="TeamInvitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email", models.EmailField(max_length=254)),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined"), ("expired", "Expired"), ("revoked", "Revoked")], default="pending", max_length=16)),
                ("message", models.TextField(blank=True)),
                ("expires_at", models.DateTimeField()),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("accepted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="accepted_team_invitations", to=settings.AUTH_USER_MODEL)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="team_invitations", to="accounts.companyaccount")),
                ("invited_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="issued_team_invitations", to=settings.AUTH_USER_MODEL)),
                ("role", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="invitations", to="accounts.organizationrole")),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="UserPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("locale", models.CharField(default="en", max_length=16)),
                ("timezone", models.CharField(default="UTC", max_length=64)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("theme", models.CharField(choices=[("light", "Light"), ("dark", "Dark"), ("system", "System")], default="light", max_length=16)),
                ("notification_preferences", models.JSONField(blank=True, default=dict)),
                ("marketing_opt_in", models.BooleanField(default=False)),
                ("default_company", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.companyaccount")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="preferences", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="UserActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("activity_type", models.CharField(choices=[("login", "Login"), ("logout", "Logout"), ("profile_updated", "Profile updated"), ("company_created", "Company created"), ("team_invited", "Team invited"), ("team_member_added", "Team member added"), ("document_uploaded", "Document uploaded"), ("rfq_created", "RFQ created"), ("order_placed", "Order placed"), ("settings_changed", "Settings changed"), ("api_token_issued", "API token issued"), ("generic", "Generic")], max_length=40)),
                ("summary", models.CharField(max_length=255)),
                ("target_type", models.CharField(blank=True, max_length=120)),
                ("target_id", models.CharField(blank=True, max_length=64)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("company", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activities", to="accounts.companyaccount")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activities", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="SecurityEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(choices=[("login_success", "Login success"), ("login_failed", "Login failed"), ("logout", "Logout"), ("two_factor_enabled", "Two-factor enabled"), ("two_factor_disabled", "Two-factor disabled"), ("two_factor_challenge_passed", "Two-factor challenge passed"), ("two_factor_challenge_failed", "Two-factor challenge failed"), ("password_changed", "Password changed"), ("password_reset_requested", "Password reset requested"), ("password_reset_completed", "Password reset completed"), ("email_verified", "Email verified"), ("api_token_issued", "API token issued"), ("api_token_revoked", "API token revoked"), ("account_suspended", "Account suspended")], max_length=40)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="security_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="UserApiToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("token", models.CharField(editable=False, max_length=64, unique=True)),
                ("prefix", models.CharField(editable=False, max_length=12)),
                ("scopes", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("active", "Active"), ("revoked", "Revoked"), ("expired", "Expired")], default="active", max_length=16)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_from_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="api_tokens", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("code", models.CharField(blank=True, max_length=40)),
                ("cost_center_code", models.CharField(blank=True, max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="departments", to="accounts.companyaccount")),
                ("manager", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="managed_departments", to=settings.AUTH_USER_MODEL)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="children", to="accounts.department")),
            ],
            options={"ordering": ("company__name", "name")},
        ),
        migrations.CreateModel(
            name="AddressBookEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=120)),
                ("recipient_name", models.CharField(blank=True, max_length=160)),
                ("line1", models.CharField(max_length=255)),
                ("line2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("postal_code", models.CharField(blank=True, max_length=32)),
                ("country", models.CharField(max_length=2)),
                ("phone_number", models.CharField(blank=True, max_length=32)),
                ("is_default", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="address_book_entries", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("user__email", "label")},
        ),
        migrations.AddConstraint(
            model_name="teaminvitation",
            constraint=models.UniqueConstraint(condition=models.Q(("status", "pending")), fields=("company", "email"), name="unique_pending_invitation_per_company_email"),
        ),
        migrations.AddConstraint(
            model_name="department",
            constraint=models.UniqueConstraint(condition=models.Q(("code", ""), _negated=True), fields=("company", "code"), name="unique_department_code_per_company"),
        ),
    ]
