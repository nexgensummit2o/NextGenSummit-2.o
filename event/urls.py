from django.urls import path
from . import views

urlpatterns = [
    # General Pages
    path('', views.home, name='home'),
    path('teams/', views.team_list, name='team_list'),

    # Auth & Profile
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboards
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),
    path('dashboard/judge/', views.judge_dashboard, name='judge_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),

    # Team Management
    path('team/', views.team_dashboard, name='team_dashboard'),
    path('team/create/', views.create_team, name='create_team'),
    path('team/invite/', views.invite_member, name='invite_member'),
     path('team/invite/<int:invite_id>/<str:action>/',views.handle_invite, name='handle_invite'),
    path('teams/<int:team_id>/request_join/', views.request_to_join_team, name='request_to_join_team'),
    path('requests/<int:member_id>/<str:action>/', views.handle_join_request, name='handle_join_request'),
    path('team/delete/', views.delete_team, name='delete_team'),
    path('team/exit/', views.exit_team, name='exit_team'),

    # Playground & Submission
    path('team/select_problem/<int:problem_id>/', views.select_problem, name='select_problem'),
    path('playground/', views.submit_playground, name='submit_playground'),

    # Judging
    path('submission/<int:submission_id>/score/', views.score_submission, name='score_submission'),

    # Other Features
    path('feedback/', views.submit_feedback, name='feedback'),
    path('notifications/', views.notification_list, name='notifications'),
    path('certificate/', views.view_certificate, name='view_certificate'),

    # Organizer Views
    path('organizer/team/<int:team_id>/', views.view_team_by_organizer, name='view_team_by_organizer'),
]