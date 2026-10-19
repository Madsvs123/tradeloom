from datetime import timedelta

from djang.contrib.auth import get_usr_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from backend.apps.accounts.models import CompanyAccount, EmailVerificationToken, OrganizationRole, OrganizationSettings, TeamMember


User = get_user_model()


class UserAndVerificationTests(TestCase):
    def test_create_user_uses_email_as_login(self):
        user = User.objects.create_user(email="buyer@example.com", password="strong-password")

        self.assertEqual(user.email, "buyer@example.com")
        self.assertEqual(user.username, "buyer@example.com")
        self.assertTrue(user.check_password("strong-password"))

    def test_email_verification_token_marks_user_verified(self):
        user = User.objects.create_user(email="supplier@example.com", password="strong-password")
        token = EmailVerificationToken.objects.create(user=user, expires_at=timezone.now() + timedelta(hours=1))

        token.consume()
        user.refresh_from_db()

        self.assertTrue(user.is_email_verified)
        self.assertIsNotNone(token.used_at)

    def test_expired_email_verification_token_cannot_be_consumed(self):
        user = User.objects.create_user(email="old@example.com", password="strong-password")
        token = EmailVerificationToken.objects.create(user=user, expires_at=timezone.now() - timedelta(minutes=1))

        with self.assertRaises(ValidationError):
            token.consume()


class CompanyMembershipTests(TestCase):
    def test_company_bootstrap_relationships_can_be_created(self):
        user = User.objects.create_user(email="owner@example.com", password="strong-password")
        company = CompanyAccount.objects.create(name="Acme Textiles", company_type=CompanyAccount.CompanyType.BOTH, primary_contact=user)
        settings = OrganizationSettings.objects.create(company=company, default_currency="USD")
        role = OrganizationRole.objects.create(company=company, name="Owner", slug="owner", is_system=True)
        member = TeamMember.objects.create(company=company, user=user, role=role, status=TeamMember.Status.ACTIVE, joined_at=timezone.now())

        self.assertEqual(settings.company, company)
        self.assertEqual(member.role.slug, "owner")
        self.assertEqual(company.team_members.cnt(), 1)

