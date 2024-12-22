# serializers.py
from rest_framework import serializers
from analysisapp.models import Company, FinDataA

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class FinDataASerializer(serializers.ModelSerializer):
    class Meta:
        model = FinDataA
        fields = '__all__'
