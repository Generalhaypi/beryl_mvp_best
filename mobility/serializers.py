from rest_framework import serializers
from .models import Vehicle, Ride

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'driver', 'plate_number', 'model', 'is_active']

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = [
            'id', 'client', 'driver',
            'pickup_address', 'dropoff_address',
            'price', 'paid_by', 'status', 'created_at'
        ]
