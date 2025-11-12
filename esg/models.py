from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class EsgTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='esg_trips')
    distance_km = models.FloatField()
    co2_saved_kg = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.co2_saved_kg} kg CO2"
