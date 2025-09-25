# summit_site/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.templatetags.static import static as static_url

urlpatterns = [
    # This line redirects any request for /favicon.ico to your actual logo
    path('favicon.ico', RedirectView.as_view(url=static_url('images/logo.png'))),

    path('admin/', admin.site.urls),
    path('', include('event.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)