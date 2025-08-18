# stream/serializers.py
from rest_framework import serializers
from .models import Person, ExpressionRecord

class ExpressionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpressionRecord
        fields = ['expression', 'count']

class PersonSerializer(serializers.ModelSerializer):
    expressions = ExpressionRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Person
        fields = ['face_id', 'name', 'total_detections', 'expressions']
