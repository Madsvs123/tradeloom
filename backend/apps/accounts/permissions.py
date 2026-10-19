from rest_framework import permissions

from .models import TeamMember


class IsVerifiedUser(permissions.BasePermission):
    message = "Email verification is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_email_verified)


class IsCompanyMember(permissions.BasePermission):
    message = "You must belong to this company."

    def has_object_permission(self, request, view, obj):
        company = getattr(obj, "company", obj)
        return TeamMember.objects.filter(
            company=company,
            user=request.user,
            status=TeamMember.Status.ACTIVE,
        ).exists()


class IsCompanyAdmin(permissions.BasePermission):
    message = "Company administrator permission is required."

    def has_object_permission(self, request, view, obj):
        company = getattr(obj, "company", obj)
        return TeamMember.objects.filter(
            company=company,
            user=request.user,
            status=TeamMember.Status.ACTIVE,
            role__slug__in=("owner", "admin"),
        ).exists()
