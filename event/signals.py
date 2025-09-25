import os
from PIL import Image, ImageDraw, ImageFont

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Announcement, Notification, Submission, TeamMember, Certificate, UserProfile
)

@receiver(post_save, sender=Announcement)
def create_notification_for_announcement(sender, instance, created, **kwargs):
    """
    Create a notification for all users when a new announcement is made.
    """
    if created:
        all_users = User.objects.all()
        for user in all_users:
            Notification.objects.create(
                user=user,
                message=f"New Announcement: {instance.title}"
            )

@receiver(post_save, sender=Submission)
def create_certificates_for_team(sender, instance, created, **kwargs):
    """
    Generate a certificate for each member of a team upon their first submission.
    This runs only when the submission object is first created.
    """
    if created:
        team = instance.team
        team_members = TeamMember.objects.filter(team=team, status='accepted')

        for member in team_members:
            participant = member.participant
            if not Certificate.objects.filter(user=participant).exists():
                try:
                    template_path = os.path.join(settings.BASE_DIR, 'static/images/certificate_template.png')
                    image = Image.open(template_path)
                    draw = ImageDraw.Draw(image)
                    
                    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/Inter-Bold.ttf')
                    font = ImageFont.truetype(font_path, 60)
                    
                    name = participant.get_full_name() or participant.username
                    
                    # Deprecated method `textlength` replaced with `font.getbbox` for modern Pillow versions
                    text_box = draw.textbbox((0, 0), name, font=font)
                    text_width = text_box[2] - text_box[0]
                    position = ((image.width - text_width) / 2, 550) # Adjust Y-coordinate as needed
                    
                    draw.text(position, name, font=font, fill=(0, 0, 0))
                    
                    output_folder = os.path.join(settings.MEDIA_ROOT, 'certificates')
                    os.makedirs(output_folder, exist_ok=True)
                    file_path = os.path.join(output_folder, f'certificate_{participant.username}.png')
                    image.save(file_path)

                    Certificate.objects.create(
                        user=participant,
                        certificate_file=f'certificates/certificate_{participant.username}.png'
                    )
                except FileNotFoundError:
                    print(f"Warning: Certificate template or font file not found. Could not generate certificate for {participant.username}.")
                except Exception as e:
                    print(f"An error occurred during certificate generation: {e}")

@receiver(post_save, sender=UserProfile)
def manage_staff_status(sender, instance, created, **kwargs):
    """
    Grant or revoke staff status when a user's role changes to/from 'organizer'.
    """
    user = instance.user
    if instance.user_role == 'organizer':
        if not user.is_staff:
            user.is_staff = True
            user.save()
    else:
        if user.is_staff and not user.is_superuser:
            user.is_staff = False
            user.save()

@receiver(post_save, sender=TeamMember)
def notify_on_team_member_status_change(sender, instance, created, **kwargs):
    """
    Send notifications for team-related activities.
    """
    team = instance.team
    participant = instance.participant
    
    # Notify leader of a new join request
    if created and instance.status == 'pending':
        Notification.objects.create(
            user=team.leader,
            message=f"{participant.username} has requested to join your team, '{team.team_name}'."
        )
        
    # Notify participant they have been accepted
    if not created and instance.status == 'accepted' and 'status' in (kwargs.get('update_fields') or []):
        Notification.objects.create(
            user=participant,
            message=f"You have been accepted into team '{team.team_name}'!"
        )