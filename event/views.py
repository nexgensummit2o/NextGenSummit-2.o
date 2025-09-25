import uuid
import pytz
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from .models import *
from .forms import *

def get_user_role(user):
    if not user.is_authenticated:
        return None
    try:
        return user.userprofile.user_role
    except UserProfile.DoesNotExist:
        return None

def home(request):
    announcements = Announcement.objects.all().order_by('-created_at')[:3]
    problem_statements = ProblemStatement.objects.all()
    faqs = FAQ.objects.all().order_by('id')
    schedule_day1 = ScheduleItem.objects.filter(day='Day 1: Sep 25, 2025').order_by('start_time')
    schedule_day2 = ScheduleItem.objects.filter(day='Day 2: Sep 26, 2025').order_by('start_time')
    schedule_day3 = ScheduleItem.objects.filter(day='Day 3: Sep 27, 2025').order_by('start_time')
    profile_complete = False
    if request.user.is_authenticated:
        try:
            profile_complete = request.user.userprofile.is_profile_complete()
        except UserProfile.DoesNotExist:
            profile_complete = False

    context = {
        'announcements': announcements,
        'profile_complete': profile_complete,
         #'problem_statements': problem_statements,
        'faqs': faqs,
        'schedule_day1': schedule_day1,
        'schedule_day2': schedule_day2,
        'schedule_day3': schedule_day3,
    }
    return render(request, 'event/index.html', context)

@login_required
def team_list(request):
    teams = Team.objects.annotate(member_count=Count('teammember')).filter(member_count__gt=0)
    user_on_team = TeamMember.objects.filter(participant=request.user, status='accepted').exists()
    context = {
        'teams': teams,
        'user_on_team': user_on_team,
    }
    return render(request, 'event/team_list.html', context)

class CustomLoginView(LoginView):
    template_name = 'event/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin:index')

        role = get_user_role(user)
        if role == 'participant':
            return reverse_lazy('participant_dashboard')
        elif role == 'judge':
            return reverse_lazy('judge_dashboard')
        elif role == 'organizer':
            return reverse_lazy('organizer_dashboard')
        return reverse_lazy('home')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'update_user' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your account details have been updated successfully!')
                return redirect('profile')
        elif 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the password errors below.')

    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.userprofile)
    password_form = CustomPasswordChangeForm(request.user)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'role': get_user_role(request.user),
    }
    return render(request, 'event/profile.html', context)

@login_required
def participant_dashboard(request):
    profile_complete = False
    try:
        profile_complete = request.user.userprofile.is_profile_complete()
    except UserProfile.DoesNotExist:
        pass

    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    context = {
        'announcements': announcements,
        'profile_complete': profile_complete,
        'role': get_user_role(request.user),
    }
    return render(request, 'event/dashboard_participant.html', context)

@login_required
def judge_dashboard(request):
    role = get_user_role(request.user)
    if not (role == 'judge' or request.user.is_staff):
        raise PermissionDenied("You do not have permission to access this page.")

    submissions = Submission.objects.all()
    context = {
        'submissions': submissions,
        'role': role,
    }
    return render(request, 'event/dashboard_judge.html', context)

@login_required
def organizer_dashboard(request):
    role = get_user_role(request.user)
    if not (role == 'organizer' or request.user.is_staff):
        raise PermissionDenied("You do not have permission to access this page.")

    problems = ProblemStatement.objects.annotate(team_count=Count('teams_working_on')).prefetch_related('teams_working_on__leader')
    context = {
        'problems': problems,
        'role': role,
    }
    return render(request, 'event/dashboard_organizer.html', context)

@login_required
def team_dashboard(request):
    team_member = TeamMember.objects.filter(participant=request.user, status='accepted').first()
    user_role = get_user_role(request.user)

    if team_member:
        team = team_member.team
        members = TeamMember.objects.filter(team=team, status='accepted')
        pending_requests = TeamMember.objects.filter(team=team, status='pending')
        invite_form = TeamInviteForm()
        context = {
            'team': team,
            'members': members,
            'pending_requests': pending_requests,
            'invite_form': invite_form,
            'role': user_role,
        }
        return render(request, 'event/team_dashboard.html', context)
    else:
        creation_form = TeamCreationForm()
        invites = TeamInvite.objects.filter(invited_email=request.user.email, status='pending')
        context = {
            'creation_form': creation_form,
            'invites': invites,
            'role': user_role,
        }
        return render(request, 'event/no_team_dashboard.html', context)

@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.team_code = uuid.uuid4().hex[:8].upper()
            team.save()
            TeamMember.objects.create(team=team, participant=request.user, role='leader', status='accepted')
            messages.success(request, f"Team '{team.team_name}' created successfully!")
    return redirect('team_dashboard')

@login_required
def invite_member(request):
    if request.method == 'POST':
        form = TeamInviteForm(request.POST)
        try:
            team = Team.objects.get(leader=request.user)
            if form.is_valid():
                email = form.cleaned_data['email']
                TeamInvite.objects.create(team=team, invited_email=email)
                messages.success(request, f"Invitation sent to {email}.")
        except Team.DoesNotExist:
            messages.error(request, "You are not the leader of a team.")
    return redirect('team_dashboard')


@login_required
def request_to_join_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if TeamMember.objects.filter(participant=request.user, status='accepted').exists():
        messages.error(request, "You are already on a team.")
        return redirect('team_list')

    TeamMember.objects.get_or_create(
        team=team,
        participant=request.user,
        defaults={'role': 'member', 'status': 'pending'}
    )
    messages.success(request, f"Your request to join '{team.team_name}' has been sent.")
    return redirect('team_list')

@login_required
def handle_join_request(request, member_id, action):
    join_request = get_object_or_404(TeamMember, id=member_id, status='pending')
    if request.user != join_request.team.leader:
        raise PermissionDenied("You do not have permission to perform this action.")

    if action == 'accept':
        join_request.status = 'accepted'
        join_request.save(update_fields=['status'])
        messages.success(request, f"Accepted {join_request.participant.username} into the team.")
    elif action == 'decline':
        messages.info(request, f"Declined join request from {join_request.participant.username}.")
        join_request.delete()
    return redirect('team_dashboard')

@login_required
def handle_invite(request, invite_id, action):
    try:
        invite = TeamInvite.objects.get(id=invite_id, invited_email=request.user.email)
        if invite.status == 'pending':
            if action == 'accept':
                invite.status = 'accepted'
                TeamMember.objects.create(team=invite.team, participant=request.user, role='member', status='accepted')
                messages.success(request, f"You have joined the team '{invite.team.team_name}'.")
            elif action == 'decline':
                invite.status = 'declined'
                messages.info(request, f"You have declined the invitation from '{invite.team.team_name}'.")
            invite.save()
    except TeamInvite.DoesNotExist:
        messages.error(request, "Invalid invitation link.")
    return redirect('team_dashboard')

@login_required
def select_problem(request, problem_id):
    problem = get_object_or_404(ProblemStatement, id=problem_id)
    team = request.user.led_teams.first()
    if not team:
        raise PermissionDenied("You are not the leader of a team.")
    if problem.teams_working_on.count() >= 3:
        messages.error(request, f"Sorry, '{problem.title}' has the maximum number of teams.")
        return redirect('submit_playground')
    team.selected_problem = problem
    team.save()
    messages.success(request, f"Your team has selected the problem: '{problem.title}'.")
    return redirect('submit_playground')

@login_required
def submit_playground(request):
    try:
        team = TeamMember.objects.get(participant=request.user, status='accepted').team
    except TeamMember.DoesNotExist:
        messages.error(request, "You must be on a team to access the playground.")
        return redirect('participant_dashboard')
    
    submission, created = Submission.objects.get_or_create(team=team, defaults={'problem_statement': team.selected_problem})

    if request.method == 'POST':
        form = SubmissionPlaygroundForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Your playground has been updated!")
            return redirect('submit_playground')
    else:
        form = SubmissionPlaygroundForm(instance=submission)
        
    available_problems = ProblemStatement.objects.annotate(team_count=Count('teams_working_on')).filter(team_count__lt=3)
    context = {
        'team': team,
        'submission': submission,
        'form': form,
        #'available_problems': available_problems,
        'role': get_user_role(request.user),
    }
    return render(request, 'event/submit_playground.html', context)

@login_required
def score_submission(request, submission_id):
    role = get_user_role(request.user)
    if not (role == 'judge' or request.user.is_staff):
        raise PermissionDenied("You do not have permission to access this page.")

    submission = get_object_or_404(Submission, id=submission_id)
    score, created = JudgingScore.objects.get_or_create(judge=request.user, submission=submission)
    if request.method == 'POST':
        form = JudgingScoreForm(request.POST, instance=score)
        if form.is_valid():
            form.save()
            messages.success(request, f"Score for '{submission.project_title}' has been saved.")
            return redirect('judge_dashboard')
    else:
        form = JudgingScoreForm(instance=score)
    context = {
        'form': form,
        'submission': submission,
        'role': role,
    }
    return render(request, 'event/score_submission.html', context)

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.participant = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('participant_dashboard')
    else:
        form = FeedbackForm()
    context = {
        'form': form,
        'role': get_user_role(request.user),
    }
    return render(request, 'event/feedback.html', context)

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)
    context = {
        'notifications': notifications,
        'role': get_user_role(request.user),
    }
    return render(request, 'event/notifications.html', context)

@login_required
def view_certificate(request):
    try:
        certificate = Certificate.objects.get(user=request.user)
    except Certificate.DoesNotExist:
        certificate = None

    unlock_time = datetime(2025, 9, 27, 11, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    is_unlocked = now >= unlock_time
    context = {
        'certificate': certificate,
        'is_unlocked': is_unlocked,
        'unlock_time': unlock_time,
        'role': get_user_role(request.user),
    }
    return render(request, 'event/certificate.html', context)

@login_required
def view_team_by_organizer(request, team_id):
    role = get_user_role(request.user)
    if not (role == 'organizer' or request.user.is_staff):
        raise PermissionDenied("You do not have permission to access this page.")
    team = get_object_or_404(Team, id=team_id)
    context = {
        'team': team,
        'role': role,
    }
    return render(request, 'event/view_team_by_organizer.html', context)


@login_required
def delete_team(request):
    if request.method == 'POST':
        team = get_object_or_404(Team, leader=request.user)
        team_name = team.team_name
        team.delete()
        messages.success(request, f"Team '{team_name}' has been successfully deleted.")
        return redirect('team_dashboard')
    return redirect('team_dashboard')

@login_required
def exit_team(request):
    if request.method == 'POST':
        try:
            team_member = TeamMember.objects.get(participant=request.user, status='accepted')

            if team_member.role == 'leader':
                messages.error(request, "As the team leader, you cannot leave the team. You must delete it instead.")
                return redirect('team_dashboard')

            team_name = team_member.team.team_name
            team_member.delete()
            messages.success(request, f"You have successfully left the team '{team_name}'.")
            return redirect('team_dashboard')

        except TeamMember.DoesNotExist:
            messages.error(request, "You are not on a team.")
            return redirect('participant_dashboard')

    return redirect('team_dashboard')