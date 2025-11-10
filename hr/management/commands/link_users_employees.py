from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hr.models import Employee
from django.db import transaction


class Command(BaseCommand):
    help = 'Link existing users to employees based on matching criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Create user accounts for employees who don\'t have them'
        )
        parser.add_argument(
            '--link-existing',
            action='store_true',
            help='Link existing users to employees based on matching email/name'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        create_users = options['create_users']
        link_existing = options['link_existing']

        if not create_users and not link_existing:
            self.stdout.write(
                self.style.WARNING('Please specify either --create-users or --link-existing')
            )
            return

        if link_existing:
            self.link_existing_users(dry_run)

        if create_users:
            self.create_user_accounts(dry_run)

    def link_existing_users(self, dry_run=False):
        """Link existing users to employees based on matching criteria."""
        self.stdout.write('Linking existing users to employees...\n')

        # Get employees without user accounts
        employees_without_users = Employee.objects.filter(user__isnull=True)

        # Get users without employee records
        users_without_employees = User.objects.filter(employee__isnull=True)

        matched_count = 0

        for employee in employees_without_users:
            # Try to match by email first
            matching_user = None

            if employee.email:
                employee_email = str(employee.email).strip().lower()
                matching_user = users_without_employees.filter(email__iexact=employee_email).first()

            # If no email match, try to match by employee_id as username
            if not matching_user:
                matching_user = users_without_employees.filter(
                    username__iexact=employee.employee_id.lower()
                ).first()

            # If still no match, try to match by full name
            if not matching_user:
                matching_user = users_without_employees.filter(
                    first_name__iexact=employee.first_name,
                    last_name__iexact=employee.last_name
                ).first()

            if matching_user:
                self.stdout.write(
                    f'  Match found: Employee {employee.employee_id} ({employee.get_full_name()}) '
                    f'-> User {matching_user.username} ({matching_user.get_full_name()})'
                )

                if not dry_run:
                    with transaction.atomic():
                        employee.user = matching_user
                        employee.save()

                        # Update user details to match employee
                        matching_user.first_name = employee.first_name
                        matching_user.last_name = employee.last_name
                        if employee.email:
                            matching_user.email = str(employee.email)
                        matching_user.is_active = employee.is_active
                        matching_user.save()

                matched_count += 1

        if dry_run:
            self.stdout.write(
                f'\nDRY RUN: Would have linked {matched_count} user-employee pairs'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully linked {matched_count} user-employee pairs')
            )

    def create_user_accounts(self, dry_run=False):
        """Create user accounts for employees who don't have them."""
        self.stdout.write('\nCreating user accounts for employees...\n')

        employees_without_users = Employee.objects.filter(user__isnull=True)
        created_count = 0

        for employee in employees_without_users:
            self.stdout.write(f'  Creating user for: {employee.employee_id} ({employee.get_full_name()})')

            if not dry_run:
                try:
                    user = employee.create_user_account()
                    self.stdout.write(f'    -> Created user: {user.username}')
                    created_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    -> Failed to create user: {e}')
                    )

        if dry_run:
            self.stdout.write(
                f'\nDRY RUN: Would have created {employees_without_users.count()} user accounts'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} user accounts')
            )

        # Show statistics
        self.show_statistics()

    def show_statistics(self):
        """Show current statistics about user-employee relationships."""
        total_employees = Employee.objects.count()
        employees_with_users = Employee.objects.filter(user__isnull=False).count()
        employees_without_users = Employee.objects.filter(user__isnull=True).count()

        total_users = User.objects.count()
        users_with_employees = User.objects.filter(employee__isnull=False).count()
        users_without_employees = User.objects.filter(employee__isnull=True).count()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('STATISTICS:')
        self.stdout.write('='*50)
        self.stdout.write(f'Total Employees: {total_employees}')
        self.stdout.write(f'  - With User Accounts: {employees_with_users}')
        self.stdout.write(f'  - Without User Accounts: {employees_without_users}')
        self.stdout.write(f'')
        self.stdout.write(f'Total Users: {total_users}')
        self.stdout.write(f'  - With Employee Records: {users_with_employees}')
        self.stdout.write(f'  - Without Employee Records: {users_without_employees}')
        self.stdout.write('='*50)