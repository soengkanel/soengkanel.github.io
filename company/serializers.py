from rest_framework import serializers
from .models import Company, Group


class GroupSerializer(serializers.ModelSerializer):
    total_companies = serializers.ReadOnlyField()
    active_companies = serializers.ReadOnlyField()

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'established_date',
            'headquarters', 'website', 'phone_number', 'email',
            'is_active', 'total_companies', 'active_companies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'schema_name', 'name', 'group', 'group_name',
            'company_type', 'registration_number', 'tax_id',
            'description', 'company_address', 'established_date',
            'address', 'city', 'state_province', 'postal_code',
            'country', 'website', 'phone_number', 'email',
            'logo', 'is_active'
        ]
        read_only_fields = ['schema_name']


class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'name', 'company_type', 'registration_number', 'tax_id',
            'description', 'company_address', 'established_date',
            'address', 'city', 'state_province', 'postal_code',
            'country', 'website', 'phone_number', 'email', 'logo'
        ]