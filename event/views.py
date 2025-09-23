from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import ProblemStatement, ScheduleItem, FAQ, Announcement, Notification
from .forms import UserProfileForm, UserUpdateForm, CustomPasswordChangeForm, FeedbackForm
from .models import Team, TeamMember, TeamInvite
from .forms import TeamCreationForm, TeamInviteForm
import uuid # For generating unique team codes
from .forms import SubmissionForm
from .models import Submission
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Submission, JudgingScore
from .forms import JudgingScoreForm
from django.core.exceptions import PermissionDenied
from .models import Certificate
from datetime import datetime
import pytz

# --- Homepage View ---
def home(request):
    problem_statements = ProblemStatement.objects.all()
    faqs = FAQ.objects.all().order_by('id')
    schedule_day1 = ScheduleItem.objects.filter(day='Day 1: Sep 25, 2025').order_by('start_time')
    schedule_day2 = ScheduleItem.objects.filter(day='Day 2: Sep 26, 2025').order_by('start_time')
    schedule_day3 = ScheduleItem.objects.filter(day='Day 3: Sep 27, 2025').order_by('start_time')
    context = {
        'problem_statements': problem_statements,
        'faqs': faqs,
        'schedule_day1': schedule_day1,
        'schedule_day2': schedule_day2,
        'schedule_day3': schedule_day3,
    }
    return render(request, 'event/index.html', context)

# --- Custom Login View ---
class CustomLoginView(LoginView):
    template_name = 'event/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin:index')
        role = user.userprofile.user_role
        if role == 'participant':
            return reverse_lazy('participant_dashboard')
        elif role == 'judge':
            return reverse_lazy('judge_dashboard')
        elif role == 'organizer':
            return reverse_lazy('organizer_dashboard')
        else:
            return reverse_lazy('home')

# --- Profile View ---
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
    }
    return render(request, 'event/profile.html', context)

# --- Dashboard Views ---
@login_required
def participant_dashboard(request):
    # Fetch all the data needed for the dashboard
    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    problem_statements = ProblemStatement.objects.all()
    
    schedule_day1 = ScheduleItem.objects.filter(day='Day 1: Sep 25, 2025').order_by('start_time')
    schedule_day2 = ScheduleItem.objects.filter(day='Day 2: Sep 26, 2025').order_by('start_time')
    schedule_day3 = ScheduleItem.objects.filter(day='Day 3: Sep 27, 2025').order_by('start_time')

    context = {
        'announcements': announcements,
        'problem_statements': problem_statements,
        'schedule_day1': schedule_day1,
        'schedule_day2': schedule_day2,
        'schedule_day3': schedule_day3,
    }
    return render(request, 'event/dashboard_participant.html', context)

def judge_dashboard(request):
    if not request.user.userprofile.user_role == 'judge':
        raise PermissionDenied("You do not have permission to access this page.")
    
    submissions = Submission.objects.all()
    context = {
        'submissions': submissions,
    }
    return render(request, 'event/dashboard_judge.html', context)

@login_required
def organizer_dashboard(request):
    # Ensure only organizers and staff can access this page
    if not (request.user.userprofile.user_role == 'organizer' or request.user.is_staff):
        raise PermissionDenied("You do not have permission to access this page.")
    
    # Fetch statistics
    participant_count = UserProfile.objects.filter(user_role='participant').count()
    team_count = Team.objects.count()
    submission_count = Submission.objects.count()
    
    # Fetch recent activity
    recent_submissions = Submission.objects.order_by('-submitted_at')[:5]

    context = {
        'announcements': Announcement.objects.all().order_by('-created_at')[:5],
        'participant_count': participant_count,
        'team_count': team_count,
        'submission_count': submission_count,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'event/dashboard_organizer.html', context)

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark notifications as read once the user views them
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    return render(request, 'event/notifications.html', {'notifications': notifications})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.participant = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('participant_dashboard') # Or wherever you want to redirect
    else:
        form = FeedbackForm()
    
    return render(request, 'event/feedback.html', {'form': form})

@login_required
def team_dashboard(request):
    try:
        # Check if user is a member of any team
        team_member = TeamMember.objects.get(participant=request.user)
        team = team_member.team
        members = TeamMember.objects.filter(team=team)
        invite_form = TeamInviteForm()
        
        context = {
            'team': team,
            'members': members,
            'invite_form': invite_form,
        }
        return render(request, 'event/team_dashboard.html', context)
    except TeamMember.DoesNotExist:
        # User is not on a team, show creation form and invites
        creation_form = TeamCreationForm()
        invites = TeamInvite.objects.filter(invited_email=request.user.email, status='pending')
        context = {
            'creation_form': creation_form,
            'invites': invites,
        }
        return render(request, 'event/no_team_dashboard.html', context)

@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.team_code = uuid.uuid4().hex[:8].upper() # Generate a random unique code
            team.save()
            
            # Add the leader as the first member
            TeamMember.objects.create(team=team, participant=request.user, role='leader', status='accepted')
            
            messages.success(request, f"Team '{team.team_name}' created successfully!")
            return redirect('team_dashboard')
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
def submit_solution(request):
    try:
        team = request.user.led_teams.first()
        if not team:
             # This check ensures only a team leader can access the page
             raise PermissionDenied("You are not the leader of a team.")
    except Team.DoesNotExist:
        return redirect('team_dashboard') # Redirect if user is not a leader

    # Check if a submission already exists for this team
    submission, created = Submission.objects.get_or_create(team=team)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.team = team
            submission.save()
            messages.success(request, 'Your submission has been saved successfully!')
            return redirect('team_dashboard')
    else:
        form = SubmissionForm(instance=submission)

    return render(request, 'event/submit_solution.html', {'form': form, 'submission': submission})


@login_required
def score_submission(request, submission_id):
    if not request.user.userprofile.user_role == 'judge':
        raise PermissionDenied("You do not have permission to access this page.")
        
    submission = get_object_or_404(Submission, id=submission_id)
    # Get or create a score instance for this judge and this submission
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
    }
    return render(request, 'event/score_submission.html', context)

@login_required
def view_certificate(request):
    try:
        certificate = Certificate.objects.get(user=request.user)
    except Certificate.DoesNotExist:
        certificate = None
    
    # Set the unlock time: Day 3, 11:00 AM IST
    unlock_time = datetime(2025, 9, 27, 11, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    
    is_unlocked = now >= unlock_time
    
    context = {
        'certificate': certificate,
        'is_unlocked': is_unlocked,
        'unlock_time': unlock_time,
    }
    return render(request, 'event/certificate.html', context)