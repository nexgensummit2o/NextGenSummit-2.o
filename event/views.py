# event/views.py
from django.shortcuts import render
from .models import ProblemStatement, ScheduleItem, FAQ

def home(request):
    """
    This view fetches all the necessary data for the main homepage
    and passes it to the index.html template.
    """
    
    # Fetch all problem statements from the database.
    problem_statements = ProblemStatement.objects.all()
    
    # Fetch all FAQs, ordered by their ID to maintain a consistent order.
    faqs = FAQ.objects.all().order_by('id')

    # Fetch and group schedule items for each specific day.
    # The string must exactly match the 'day' value in your ScheduleItem model choices.
    schedule_day1 = ScheduleItem.objects.filter(day='Day 1: Sep 25, 2025').order_by('start_time')
    schedule_day2 = ScheduleItem.objects.filter(day='Day 2: Sep 26, 2025').order_by('start_time')
    schedule_day3 = ScheduleItem.objects.filter(day='Day 3: Sep 27, 2025').order_by('start_time')

    # The context dictionary is used to pass data from the view to the template.
    # The keys (e.g., 'problem_statements') must match the variable names used in your HTML.
    context = {
        'problem_statements': problem_statements,
        'faqs': faqs,
        'schedule_day1': schedule_day1,
        'schedule_day2': schedule_day2,
        'schedule_day3': schedule_day3,
    }

    # Render the index.html template with the context data and return it as an HTTP response.
    return render(request, 'event/index.html', context)

# You will add other views for login, dashboards, etc., below this in the future.