from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile
from .models import Feedback 
from .models import Team
from .models import Submission
from .models import JudgingScore

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the help text from the new password field
        self.fields['new_password1'].help_text = None
        # Optional: Add styling to match other forms
        self.fields['old_password'].widget.attrs.update({'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'})
        self.fields['new_password1'].widget.attrs.update({'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'})
        self.fields['new_password2'].widget.attrs.update({'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'})


class UserUpdateForm(forms.ModelForm):
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
    class Meta:
        model = UserProfile
        fields = ['student_roll_number', 'about', 'branch', 'year_of_study', 'linkedin', 'github']
        widgets = {
            'student_roll_number': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
            'about': forms.Textarea(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1', 'rows': 4}),
            'branch': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
            'linkedin': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
            'github': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text focus:outline-none focus:ring-brand-accent-1 focus:border-brand-accent-1'}),
        }

class FeedbackForm(forms.ModelForm):
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

# Add these two new forms at the end of the file
class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['team_name']
        widgets = {
            'team_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
                'placeholder': 'Enter your team name'
            }),
        }
        labels = {
            'team_name': ''
        }

class TeamInviteForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
            'placeholder': 'Enter participant email'
        }),
        label=""
    )

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['problem_statement', 'project_title', 'project_description', 'repo_link', 'demo_link']
        widgets = {
            'problem_statement': forms.Select(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'project_title': forms.TextInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text'}),
            'project_description': forms.Textarea(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text', 'rows': 5}),
            'repo_link': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text', 'placeholder': 'https://github.com/user/repo'}),
            'demo_link': forms.URLInput(attrs={'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text', 'placeholder': 'https://youtu.be/...'}),
        }
        labels = {
            'problem_statement': 'Chosen Problem Statement',
            'project_title': 'Project Title',
            'project_description': 'A brief description of your project',
            'repo_link': 'GitHub Repository Link',
            'demo_link': 'Project Demo Link (YouTube, Loom, etc.)',
        }

class JudgingScoreForm(forms.ModelForm):
    class Meta:
        model = JudgingScore
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full bg-brand-bg border-gray-600 rounded-md py-2 px-3 text-brand-text',
                'min': 0,
                'max': 100,
                'step': 0.5
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