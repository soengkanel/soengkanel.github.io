from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django_tenants.utils import schema_context
from company.models import Company


class Command(BaseCommand):
    help = 'Create a user for a specific tenant company'

    def add_arguments(self, parser):
        parser.add_argument('company_name', type=str, help='Name of the company')
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('email', type=str, help='Email for the new user')
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the user (if not provided, will prompt)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name of the user'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name of the user'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Create a superuser for this tenant'
        )
        parser.add_argument(
            '--staff',
            action='store_true',
            help='Mark user as staff (can access admin)'
        )

    def handle(self, *args, **options):
        company_name = options['company_name']
        username = options['username']
        email = options['email']
        password = options.get('password')
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')
        is_superuser = options['superuser']
        is_staff = options['staff'] or is_superuser  # Superusers are automatically staff

        # Get the company
        try:
            company = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            raise CommandError(f'Company "{company_name}" does not exist.')

        # Get password if not provided
        if not password:
            password = 'admin123'  # Default password for Docker setup
            self.stdout.write(f'Using default password: {password}')

        # Create user in the tenant's schema
        with schema_context(company.schema_name):
            try:
                with transaction.atomic():
                    # Check if user already exists in this tenant
                    if User.objects.filter(username=username).exists():
                        raise CommandError(
                            f'User "{username}" already exists in {company.name} tenant.'
                        )

                    # Create the user
                    if is_superuser:
                        user = User.objects.create_superuser(
                            username=username,
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name
                        )
                        user_type = "superuser"
                    else:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name
                        )
                        user.is_staff = is_staff
                        user.save()
                        user_type = "staff user" if is_staff else "regular user"

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created {user_type} "{username}" for {company.name}'
                        )
                    )

                    # Display user details
                    self.stdout.write('\n--- User Details ---')
                    self.stdout.write(f'Company: {company.name} (Schema: {company.schema_name})')
                    self.stdout.write(f'Username: {user.username}')
                    self.stdout.write(f'Email: {user.email}')
                    self.stdout.write(f'Full Name: {user.get_full_name() or "Not provided"}')
                    self.stdout.write(f'Is Superuser: {user.is_superuser}')
                    self.stdout.write(f'Is Staff: {user.is_staff}')
                    self.stdout.write(f'Is Active: {user.is_active}')
                    
                    # Show access URLs
                    self.stdout.write('\n--- Access Information ---')
                    self.stdout.write(f'Portal URL: http://{company.schema_name}.localhost:8000')
                    if user.is_staff:
                        self.stdout.write(f'Admin URL: http://{company.schema_name}.localhost:8000/admin')
                    
                    self.stdout.write('\n--- Security Note ---')
                    self.stdout.write(
                        f'This user can ONLY access {company.name} tenant. '
                        f'They cannot access other companies.'
                    )

            except Exception as e:
                raise CommandError(f'Failed to create user: {str(e)}')

        # Show summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] User "{username}" successfully created for {company.name} tenant!'
            )
        ) 