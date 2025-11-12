from rest_framework import generics, permissions
from .models import Vehicle, Ride
from .serializers import VehicleSerializer, RideSerializer

class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.AllowAny]

class RideListCreateView(generics.ListCreateAPIView):
    queryset = Ride.objects.all().order_by('-created_at')
    serializer_class = RideSerializer
    permission_classes = [permissions.AllowAny]
