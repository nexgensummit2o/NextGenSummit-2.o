from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Route for the Django admin panel
    path('admin/', admin.site.urls),
    
    # Include all URLs from the 'event' app for the main site
    path('', include('event.urls')),
]