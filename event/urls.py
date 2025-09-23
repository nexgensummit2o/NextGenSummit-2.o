from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
    
    # Auth URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    # Dashboard URLs
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),
    path('dashboard/judge/', views.judge_dashboard, name='judge_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),
]