from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . import models

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

# --- User Admin Configuration ---
class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    inlines = (UserProfileInline,)
    
    # This is the corrected layout for the "Add user" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'), # Corrected password21 to password1
        }),
    )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- Schedule Admin Configuration ---
class ScheduleDetailInline(admin.StackedInline):
    model = models.ScheduleDetail
    can_delete = False
    verbose_name_plural = 'Detailed Information (About)'

@admin.register(models.ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'day', 'start_time', 'end_time')
    list_filter = ('day',)
    inlines = (ScheduleDetailInline,)


# --- Team & Submission Admin Configuration ---
@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'leader', 'team_code', 'created_at')
    search_fields = ('team_name', 'leader__username')

@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'team', 'problem_statement', 'submitted_at')
    list_filter = ('problem_statement',)
    search_fields = ('project_title', 'team__team_name')


# --- Register All Other Models ---
admin.site.register(models.ProblemStatement)
admin.site.register(models.Organizer)
admin.site.register(models.FAQ)
admin.site.register(models.Resource)
admin.site.register(models.Feedback)
admin.site.register(models.TeamMember)
admin.site.register(models.TeamInvite)
admin.site.register(models.JudgingScore)
admin.site.register(models.Announcement)
admin.site.register(models.Notification)