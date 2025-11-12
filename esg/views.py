from rest_framework import generics, permissions
from .models import EsgTrip
from .serializers import EsgTripSerializer

class EsgTripListCreateView(generics.ListCreateAPIView):
    queryset = EsgTrip.objects.all().order_by('-created_at')
    serializer_class = EsgTripSerializer
    permission_classes = [permissions.AllowAny]
