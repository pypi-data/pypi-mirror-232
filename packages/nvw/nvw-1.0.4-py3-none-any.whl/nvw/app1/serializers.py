import json

from rest_framework import serializers

from .models import ConfigTemplate, EnvironmentParameter, ReportEntry, Report


class EnvironmentParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentParameter
        fields = ('env_name', 'parameters')


class ConfigTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigTemplate
        fields = ('env_name', 'template_string')


class ConfigTextSerializer(serializers.Serializer):
    device_name = serializers.CharField()
    config_text = serializers.CharField()


class ReportEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEntry
        fields = '__all__'

    def to_representation(self, instance):
        original_rep = super().to_representation(instance)
        if original_rep['meta_data'] is not None:
            original_rep['meta_data'] = json.loads(original_rep['meta_data'])
        return original_rep

    def to_internal_value(self, data):
        if data['meta_data'] is not None:
            data['meta_data'] = json.dumps(data['meta_data'], indent=2)
        original_rep = super().to_internal_value(data)
        return original_rep


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
