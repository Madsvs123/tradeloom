from rest_framework import serializers

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


class CarbonFootprintSerializer(serializers.ModelSerializer):
    emission_records = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = CarbonFootprint
        fields = "__all__"
        read_only_fields = ("id", "total_emissions_tco2e", "status", "computed_at", "created_at", "updated_at")


class EmissionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionRecord
        fields = "__all__"
        read_only_fields = ("id", "co2e", "created_at", "updated_at")


class SustainabilityCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SustainabilityCertificate
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class EsgTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsgTarget
        fields = "__all__"
        read_only_fields = ("id", "progress_percent", "status", "created_at", "updated_at")


class GreenAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GreenAttribute
        fields = "__all__"
        read_only_fields = ("id", "verification_status", "verified_by", "verified_at", "created_at", "updated_at")


class SustainabilityDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SustainabilityDeclaration
        fields = "__all__"
        read_only_fields = ("id", "reference", "declared_by", "status", "verified_by", "submitted_at", "verified_at", "created_at", "updated_at")


class EsgReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsgReport
        fields = "__all__"
        read_only_fields = ("id", "status", "generated_by", "published_at", "created_at", "updated_at")


class EsgProfileSerializer(serializers.ModelSerializer):
    carbon_footprints = CarbonFootprintSerializer(many=True, read_only=True)
    targets = EsgTargetSerializer(many=True, read_only=True)
    certificates = SustainabilityCertificateSerializer(many=True, read_only=True)

    class Meta:
        model = EsgProfile
        fields = "__all__"
        read_only_fields = ("id", "reference", "owner", "status", "published_at", "created_at", "updated_at")
