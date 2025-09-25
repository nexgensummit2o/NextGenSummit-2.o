from django.db import models
from django.contrib.auth.models import User

# --- Section 1: User and Profile Management ---
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('judge', 'Judge'),
        ('organizer', 'Organizer'),
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    student_roll_number = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)
    github = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_role_display()}"

    def is_profile_complete(self):
        return bool(self.user.first_name and self.user.last_name)

# --- Section 2: Core Hackathon & Event Data ---
class ScheduleItem(models.Model):
    DAY_CHOICES = [
        ('Day 1: Sep 25, 2025', 'Day 1: Sep 25, 2025'),
        ('Day 2: Sep 26, 2025', 'Day 2: Sep 26, 2025'),
        ('Day 3: Sep 27, 2025', 'Day 3: Sep 27, 2025'),
    ]
    day = models.CharField(max_length=50, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    time_display_override = models.CharField(max_length=100, blank=True, null=True, help_text="Optional. Use to override time display (e.g., '11:30 AM onwards').")
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.day} - {self.title}"

class ScheduleDetail(models.Model):
    schedule_item = models.OneToOneField(ScheduleItem, on_delete=models.CASCADE, primary_key=True)
    details = models.TextField(help_text="Add detailed information about this schedule item here.")

    def __str__(self):
        return f"Details for {self.schedule_item.title}"

class ProblemStatement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title

class Organizer(models.Model):
    name = models.CharField(max_length=255)
    role_designation = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
        
class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question[:50] + '...'

class Resource(models.Model):
    title = models.CharField(max_length=255)
    file_link = models.URLField(max_length=255)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Feedback from {self.participant.username}"

# --- Section 3: Team and Submission Management ---
class Team(models.Model):
    team_name = models.CharField(max_length=255)
    team_code = models.CharField(max_length=255, unique=True)
    leader = models.ForeignKey(User, related_name='led_teams', on_delete=models.CASCADE)
    selected_problem = models.ForeignKey(ProblemStatement, on_delete=models.SET_NULL, null=True, blank=True, related_name='teams_working_on')
    max_size = models.IntegerField(default=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name

class TeamMember(models.Model):
    ROLE_CHOICES = [('leader', 'Leader'), ('member', 'Member')]
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('removed', 'Removed')]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')

    class Meta:
        unique_together = ('team', 'participant')

    def __str__(self):
        return f"{self.participant.username} in {self.team.team_name}"

class TeamInvite(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')]

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    invited_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite for {self.invited_email} to {self.team.team_name}"

class Submission(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    problem_statement = models.ForeignKey(ProblemStatement, on_delete=models.CASCADE, null=True, blank=True)
    project_title = models.CharField(max_length=255, blank=True, null=True)
    project_description = models.TextField(blank=True, null=True)
    repo_link = models.URLField(max_length=255, blank=True, null=True)
    demo_link = models.URLField(max_length=255, blank=True, null=True)
    # ADDED FIELDS
    ideation_text = models.TextField(blank=True, null=True)
    plan_pdf = models.FileField(upload_to='plans/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_title or 'Untitled'} by {self.team.team_name}"

class JudgingScore(models.Model):
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('judge', 'submission')

# --- Section 4: Communication & Certificates ---
class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"

class Certificate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    certificate_file = models.FileField(upload_to='certificates/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username}"