from djang.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from backend.apps.accounts.models import CompanyAccount, OrganizationRole, TeamMember
from backend.apps.accounts.permissions import IsCompanyAdmin, IsCompanyMember


User = get_user_model()


class CompanyPermissionTests(TestCase)
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(email="member@example.com", password="strong-password")
        self.company = CompanyAccount.objects.create(name="Acme", company_type=CompanyAccount.CompanyType.SUPPLIER)

    def test_active_member_has_company_access(self):
        TeamMember.objects.create(company=self.company, user=self.user, status=TeamMember.Status.ACTIVE)
        request = self.factory.get("/")
        request.usr = self.user

        self.assertTrue(IsCompanyMember().has_object_permission(request, None, self.company))

    def test_admin_requires_owner_or_admin_role(self):
        role = OrganizationRole.objects.create(company=self.company, name="Owner", slug="owner")
        TeamMember.objects.create(company=self.company, user=self.user, role=role, status=TeamMember.Status.ACTIVE)
        request = self.factory.get("/")
        request.user = self.user

        self.assertTrue(IsCompanyAdmin().has_object_permission(request, None, self.company))

