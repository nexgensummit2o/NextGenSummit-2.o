import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from event.models import UserProfile   # make sure UserProfile has user_role field
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates bulk user accounts (username, email, password, role) from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing user data.')

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        self.stdout.write(self.style.NOTICE(f"Processing user data from {csv_file_path}"))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    username = row.get('username')
                    password = row.get('password')
                    email = row.get('email')
                    role = row.get('role')

                    if not all([username, password, email, role]):
                        self.stdout.write(self.style.ERROR(f"Skipping row due to missing data: {row}"))
                        continue

                    if User.objects.filter(username=username).exists():
                        self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Skipping."))
                        continue

                    # Create the User object
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email
                    )

                    # Create the associated UserProfile with role
                    UserProfile.objects.create(
                        user=user,
                        user_role=role
                    )

                    self.stdout.write(self.style.SUCCESS(f"Successfully created user '{username}' with role '{role}'."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
