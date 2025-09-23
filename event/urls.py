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
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notification_list, name='notifications'),
    path('feedback/', views.submit_feedback, name='feedback'),
    path('team/', views.team_dashboard, name='team_dashboard'),
    path('team/create/', views.create_team, name='create_team'),
    path('team/invite/', views.invite_member, name='invite_member'),
    path('team/invite/<int:invite_id>/<str:action>/',views.handle_invite, name='handle_invite'),
    path('team/submit/', views.submit_solution, name='submit_solution'),
    path('submission/<int:submission_id>/score/', views.score_submission, name='score_submission'),
    path('certificate/', views.view_certificate, name='view_certificate'),
]