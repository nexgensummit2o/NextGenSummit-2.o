# event/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from . import models

# --- User Admin Configuration ---
class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

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

# ... (and all your other admin registration code)