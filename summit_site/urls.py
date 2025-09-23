# summit_site/urls.py

from django.contrib import admin
from django.urls import path, include  # 1. Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    # 2. Add this line to include the URLs from your 'event' app
    path('', include('event.urls')),
]