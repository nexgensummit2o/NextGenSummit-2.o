from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import ProblemStatement, ScheduleItem, FAQ

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
        
        # First, check if the user is a staff member (can access admin)
        if user.is_staff:
            return reverse_lazy('admin:index')
            
        # If not staff, check their role for frontend dashboards
        role = user.userprofile.user_role
        if role == 'participant':
            return reverse_lazy('participant_dashboard')
        elif role == 'judge':
            return reverse_lazy('judge_dashboard')
        elif role == 'organizer':
            return reverse_lazy('organizer_dashboard')
        else:
            # A fallback redirect for any other roles
            return reverse_lazy('home')

# --- Dashboard Views ---
@login_required
def participant_dashboard(request):
    return render(request, 'event/dashboard_participant.html')

@login_required
def judge_dashboard(request):
    return render(request, 'event/dashboard_judge.html')

@login_required
def organizer_dashboard(request):
    return render(request, 'event/dashboard_organizer.html')