# event/urls.py

from django.urls import path
from . import views  # Import the views from the current app

urlpatterns = [
    # When a request for the homepage arrives, call the 'home' function from views.py
    path('', views.home, name='home'),
]