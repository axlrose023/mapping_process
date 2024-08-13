from rest_framework import serializers
from .models import Client, Company, Provider, Session, SessionFileType, SessionCodesEarnings, SessionCodesMemos, \
    SessionCodesDeductions


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['id', 'provider_name']


class CompanySerializer(serializers.ModelSerializer):
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(), source='provider', write_only=True)
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'provider_id', 'provider', 'session', 'client']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'client_name']


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'is_closed']


class SessionFileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionFileType
        fields = ['id', 'session', 'file_type']


class ProcessFileSerializer(serializers.Serializer):
    file = serializers.ListField(
        child=serializers.FileField(), required=True
    )
    file_type = serializers.CharField(max_length=255, required=True)
    session_id = serializers.IntegerField(required=True)
    mapping_files = serializers.ListField(
        child=serializers.FileField(), required=True
    )
    is_new_session = serializers.BooleanField(required=True)


class UpdateMappingSerializer(serializers.Serializer):
    extracted = serializers.CharField(max_length=300)
    mapped = serializers.CharField(max_length=300, allow_blank=True)
    confidence = serializers.CharField(max_length=50, allow_blank=True)


class UpdateHeadersSerializer(serializers.Serializer):
    earnings_mappings = UpdateMappingSerializer(many=True)
    memos_mappings = UpdateMappingSerializer(many=True, required=False)
    deductions_mappings = UpdateMappingSerializer(many=True, required=False)
    taxes_mappings = UpdateMappingSerializer(many=True, required=False)
    file_link = serializers.URLField(required=True)
    file_type = serializers.CharField(max_length=255, required=True)


class SessionCodesEarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionCodesEarnings
        fields = '__all__'


class SessionCodesMemosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionCodesMemos
        fields = '__all__'


class SessionCodesDeductionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionCodesDeductions
        fields = '__all__'
