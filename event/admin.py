from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from . import models

# --- User Admin Configuration ---
# This allows the UserProfile to be edited directly within the User's admin page.
class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

# Define a new User admin by extending the base and adding the inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Unregister the default User admin and re-register it with our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- Schedule Admin Configuration ---
# This allows editing ScheduleDetail directly within the ScheduleItem admin page
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
# This makes the rest of your models accessible in the admin panel
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