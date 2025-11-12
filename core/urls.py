from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/social/', include('social.urls')),
    path('api/mobility/', include('mobility.urls')),
    path('api/wallet/', include('wallet.urls')),
    path('api/esg/', include('esg.urls')),
]
