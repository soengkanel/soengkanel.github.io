from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from company.models import Company, UserCompanyAccess
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Assign user access to a specific company'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('company_name', type=str, help='Name of the company')
        parser.add_argument(
            '--access-level',
            type=str,
            choices=['read', 'write', 'admin', 'super_admin'],
            default='read',
            help='Access level for the user (default: read)'
        )
        parser.add_argument(
            '--expires-days',
            type=int,
            help='Number of days until access expires (default: permanent)'
        )
        parser.add_argument(
            '--granted-by',
            type=str,
            help='Username of the user granting this access'
        )
        parser.add_argument(
            '--notes',
            type=str,
            help='Notes about this access grant'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update if access already exists'
        )

    def handle(self, *args, **options):
        username = options['username']
        company_name = options['company_name']
        access_level = options['access_level']
        expires_days = options.get('expires_days')
        granted_by_username = options.get('granted_by')
        notes = options.get('notes', '')
        force = options['force']

        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        # Get company
        try:
            company = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            raise CommandError(f'Company "{company_name}" does not exist.')

        # Get granted_by user if specified
        granted_by = None
        if granted_by_username:
            try:
                granted_by = User.objects.get(username=granted_by_username)
            except User.DoesNotExist:
                raise CommandError(f'Granting user "{granted_by_username}" does not exist.')

        # Calculate expiration date
        expires_at = None
        if expires_days:
            expires_at = timezone.now() + timedelta(days=expires_days)

        # Check if access already exists
        try:
            access = UserCompanyAccess.objects.get(user=user, company=company)
            if not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'Access already exists for {user.username} to {company.name}. '
                        f'Current level: {access.access_level}. Use --force to update.'
                    )
                )
                return
            
            # Update existing access
            access.access_level = access_level
            access.expires_at = expires_at
            access.granted_by = granted_by
            access.notes = notes
            access.is_active = True
            access.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated access for {user.username} to {company.name} '
                    f'with {access_level} level.'
                )
            )

        except UserCompanyAccess.DoesNotExist:
            # Create new access
            access = UserCompanyAccess.objects.create(
                user=user,
                company=company,
                access_level=access_level,
                expires_at=expires_at,
                granted_by=granted_by,
                notes=notes,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Granted {access_level} access to {user.username} for {company.name}.'
                )
            )

        # Display access details
        self.stdout.write('\n--- Access Details ---')
        self.stdout.write(f'User: {user.get_full_name() or user.username} ({user.username})')
        self.stdout.write(f'Company: {company.name} (Schema: {company.schema_name})')
        self.stdout.write(f'Access Level: {access.access_level}')
        self.stdout.write(f'Active: {access.is_active}')
        if access.expires_at:
            self.stdout.write(f'Expires: {access.expires_at}')
        else:
            self.stdout.write('Expires: Never')
        if access.granted_by:
            self.stdout.write(f'Granted by: {access.granted_by.username}')
        if access.notes:
            self.stdout.write(f'Notes: {access.notes}')
        
        # Show permissions
        self.stdout.write('\n--- Permissions ---')
        self.stdout.write(f'Can Read: {access.can_read()}')
        self.stdout.write(f'Can Write: {access.can_write()}')
        self.stdout.write(f'Can Admin: {access.can_admin()}')
        self.stdout.write(f'Can Super Admin: {access.can_super_admin()}') 