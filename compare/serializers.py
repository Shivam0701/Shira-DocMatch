"""
Serializers for document comparison API.
"""
from rest_framework import serializers


class DocumentComparisonSerializer(serializers.Serializer):
    """Serializer for document comparison response."""
    overall_score = serializers.FloatField()
    matches = serializers.ListField(child=serializers.DictField())
    stats = serializers.DictField()
    left_text = serializers.CharField(allow_blank=True)
    right_text = serializers.CharField(allow_blank=True)

