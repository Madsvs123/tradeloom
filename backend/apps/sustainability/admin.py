from django.contrib import admin

from .models import (
    CarbonFootprint,
    EmissionRecord,
    EsgProfile,
    EsgReport,
    EsgTarget,
    GreenAttribute,
    SustainabilityCertificate,
    SustainabilityDeclaration,
)


class CarbonFootprintInline(admin.TabularInline):
    model = CarbonFootprint
    extra = 0


class EmissionRecordInline(admin.TabularInline):
    model = EmissionRecord
    extra = 0


class EsgTargetInline(admin.TabularInline):
    model = EsgTarget
    extra = 0


class GreenAttributeInline(admin.TabularInline):
    model = GreenAttribute
    extra = 0


@admin.register(EsgProfile)
class EsgProfileAdmin(admin.ModelAdmin):
    list_display = ("reference", "company_name", "owner", "industry", "country", "status", "esg_rating")
    list_filter = ("status", "industry")
    search_fields = ("reference", "company_name")
    inlines = (CarbonFootprintInline, EsgTargetInline, GreenAttributeInline)


@admin.register(CarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = ("profile", "scope", "period", "total_emissions_tco2e", "status")
    list_filter = ("scope", "status", "period")
    inlines = (EmissionRecordInline,)


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ("footprint", "category", "source", "quantity", "unit", "co2e")
    list_filter = ("category",)


@admin.register(SustainabilityCertificate)
class SustainabilityCertificateAdmin(admin.ModelAdmin):
    list_display = ("profile", "certificate_type", "certificate_number", "issuer", "status", "valid_until")
    list_filter = ("status", "certificate_type")
    search_fields = ("certificate_number", "issuer")


@admin.register(EsgTarget)
class EsgTargetAdmin(admin.ModelAdmin):
    list_display = ("profile", "metric", "category", "current_value", "target_value", "progress_percent", "status")
    list_filter = ("category", "status")


@admin.register(GreenAttribute)
class GreenAttributeAdmin(admin.ModelAdmin):
    list_display = ("profile", "name", "attribute_type", "verification_status")
    list_filter = ("attribute_type", "verification_status")


@admin.register(SustainabilityDeclaration)
class SustainabilityDeclarationAdmin(admin.ModelAdmin):
    list_display = ("reference", "profile", "declaration_type", "declared_by", "status", "submitted_at")
    list_filter = ("status", "declaration_type")
    search_fields = ("reference",)


@admin.register(EsgReport)
class EsgReportAdmin(admin.ModelAdmin):
    list_display = ("title", "profile", "report_type", "period", "status", "published_at")
    list_filter = ("status", "report_type")
    search_fields = ("title",)
