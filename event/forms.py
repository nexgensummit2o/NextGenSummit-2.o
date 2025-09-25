from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import (
    UserProfile, Feedback, Team, Submission, JudgingScore
)

class CustomPasswordChangeForm(PasswordChangeForm):
    """
    A custom password change form that removes the default help text and adds styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None
        self.fields['old_password'].widget.attrs.update({'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'})
        self.fields['new_password1'].widget.attrs.update({'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'})
        self.fields['new_password2'].widget.attrs.update({'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'})

class UserUpdateForm(forms.ModelForm):
    """
    Form for updating the User model's first_name, last_name, and email.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'})
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
        }

class UserProfileForm(forms.ModelForm):
    """
    Form for updating the custom UserProfile model's details.
    """
    class Meta:
        model = UserProfile
        fields = ['student_roll_number', 'about', 'branch', 'year_of_study', 'linkedin', 'github']
        widgets = {
            'student_roll_number': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'about': forms.Textarea(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text', 'rows': 4}),
            'branch': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'linkedin': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'github': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
        }

class FeedbackForm(forms.ModelForm):
    """
    Form for users to submit event feedback.
    """
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}
            ),
            'comments': forms.Textarea(
                attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text', 'rows': 5}
            ),
        }
        labels = {
            'rating': 'Overall Rating (1-5 Stars)',
            'comments': 'Your Comments',
        }

class TeamCreationForm(forms.ModelForm):
    """
    Form for creating a new team.
    """
    class Meta:
        model = Team
        fields = ['team_name']
        widgets = {
            'team_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
                'placeholder': 'Enter your team name'
            }),
        }
        labels = { 'team_name': '' }

class TeamInviteForm(forms.Form):
    """
    A simple form for inviting a user by email.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
            'placeholder': 'Enter participant email'
        }),
        label=""
    )

class SubmissionPlaygroundForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['ideation_text', 'plan_pdf', 'repo_link', 'demo_link']
        widgets = {
            'ideation_text': forms.Textarea(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text', 'rows': 6}),
            'plan_pdf': forms.FileInput(attrs={'class': 'mt-1 block w-full text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brand-accent-2 file:text-white hover:file:bg-purple-600'}),
            'repo_link': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'demo_link': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
        }
        labels = {
            'ideation_text': 'Your Ideation',
            'plan_pdf': 'Implementation Plan (PDF only)',
            'repo_link': 'Prototype/GitHub Link',
            'demo_link': 'Video Demo Link'
        }

class JudgingScoreForm(forms.ModelForm):
    """
    Form for judges to submit a score and feedback.
    """
    class Meta:
        model = JudgingScore
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
                'min': 0, 'max': 100, 'step': 0.5
            }),
            'feedback': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
                    'rows': 6
                }
            ),
        }
        labels = {
            'score': 'Score (0-100)',
            'feedback': 'Feedback / Comments',
        }