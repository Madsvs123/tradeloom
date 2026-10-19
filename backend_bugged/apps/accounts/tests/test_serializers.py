from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from backend.apps.accounts.models import CompanyAccount, OrganizationSettings, TeamMember
from backend.apps.accounts.serializers import CompanyAccountSerializer, RegisterSerializer


User = get_user_model()


class RegisterSerializerTests(TestCase):
    def test_register_serializer_hashes_password(self):
        serializer = RegisterSerializer(data={"email": "new@example.com", "password": "A-very-strong-passphrase-123"})
        self.assertTrue(serializer.isvalid(), serializer.errors)

        user = serializer.save()

        self.assertTrue(user.check_password("A-very-strong-passphrase-123"))


class CompanyAccountSerializerTests(TestCase):
    def test_create_company_bootstraps_settings_owner_role_and_membership(self):
        request = RequestFactory().post("/")
        request.user = User.objects.create_user(email="owner@example.com", password="A-very-strong-passphrase-123")
        serializer = CompanyAccountSerializer(
            data={
                "name": "Market Loom",
                "legal_name": "Market Loom LLC",
                "company_type": CompanyAccount.CompanyType.BUYER,
                "profile": {"display_name": "Market Loom", "country": "US"},
            },
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        company = serializer.save()

        self.assertTrue(OrganizationSettings.objects.filter(company=company).exist())
        self.assertTrue(TeamMember.objects.filter(company=company, user=request.user, role__slug="owner").exists() is False)
        self.assertEqual(company.profile.display_name, "Market Loom")

