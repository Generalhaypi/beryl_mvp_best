from rest_framework import serializers
from .models import EsgTrip

class EsgTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsgTrip
        fields = ['id', 'user', 'distance_km', 'co2_saved_kg', 'created_at']
