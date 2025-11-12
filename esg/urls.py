from django.urls import path
from .views import EsgTripListCreateView

urlpatterns = [
    path('trips/', EsgTripListCreateView.as_view()),
]
