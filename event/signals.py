from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Announcement, Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from .models import Announcement, Notification, Submission, TeamMember, Certificate
from PIL import Image, ImageDraw, ImageFont
import os

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
    """
    team = instance.team
    team_members = TeamMember.objects.filter(team=team, status='accepted')

    for member in team_members:
        participant = member.participant
        # Check if a certificate already exists for this user
        if not Certificate.objects.filter(user=participant).exists():
            # --- Generate the certificate image ---
            template_path = os.path.join(settings.BASE_DIR, 'static/images/certificate_template.png')
            image = Image.open(template_path)
            draw = ImageDraw.Draw(image)
            
            # Use a truetype font for better quality
            font_path = os.path.join(settings.BASE_DIR, 'static/fonts/Inter-Bold.ttf') # You may need to add a font file
            font = ImageFont.truetype(font_path, 60) # Adjust size as needed
            
            # Get user's full name, or username as a fallback
            name = participant.get_full_name() or participant.username
            
            # Position the text (you will need to adjust these X, Y coordinates)
            text_width = draw.textlength(name, font=font)
            position = ((image.width - text_width) / 2, 550) # (Center horizontally, 550px from top)
            
            draw.text(position, name, font=font, fill=(0, 0, 0)) # Black text
            
            # Save the new certificate image
            output_folder = os.path.join(settings.MEDIA_ROOT, 'certificates')
            os.makedirs(output_folder, exist_ok=True)
            file_path = os.path.join(output_folder, f'certificate_{participant.username}.png')
            image.save(file_path)

            # Create the Certificate model instance in the database
            Certificate.objects.create(
                user=participant,
                certificate_file=f'certificates/certificate_{participant.username}.png'
            )