from django.urls import path
from .views import VehicleListCreateView, RideListCreateView

urlpatterns = [
    path('vehicles/', VehicleListCreateView.as_view()),
    path('rides/', RideListCreateView.as_view()),
]
