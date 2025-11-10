from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hr.models import Employee, EmployeeOnboarding

User = get_user_model()


class Command(BaseCommand):
    help = 'Cleans up duplicate "John Newbie" test employee records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('Searching for duplicate "John Newbie" records...'))
        self.stdout.write(self.style.WARNING('=' * 60))

        # Find all John Newbie employees
        john_newbies = Employee.objects.filter(
            first_name='John',
            last_name='Newbie'
        ).select_related('user').order_by('created_at')

        count = john_newbies.count()

        self.stdout.write(f'\nFound {count} "John Newbie" employee record(s):')
        for i, emp in enumerate(john_newbies, 1):
            onboarding_count = EmployeeOnboarding.objects.filter(employee=emp).count()
            self.stdout.write(
                f'  {i}. Employee ID: {emp.employee_id} | '
                f'User: {emp.user.username} | '
                f'Hired: {emp.hire_date} | '
                f'Onboardings: {onboarding_count}'
            )

        if count <= 1:
            self.stdout.write(self.style.SUCCESS('\n✓ No duplicates found. Nothing to clean up.'))
            return

        # Keep the first one, delete the rest
        employees_to_delete = list(john_newbies[1:])
        keep_employee = john_newbies.first()

        self.stdout.write(f'\n{"[DRY RUN] " if dry_run else ""}Keeping: {keep_employee.employee_id} ({keep_employee.user.username})')
        self.stdout.write(f'{"[DRY RUN] " if dry_run else ""}Deleting {len(employees_to_delete)} duplicate(s)...\n')

        if not dry_run:
            for emp in employees_to_delete:
                user = emp.user
                username = user.username
                emp_id = emp.employee_id

                # Delete onboarding records
                onboarding_count = EmployeeOnboarding.objects.filter(employee=emp).count()
                EmployeeOnboarding.objects.filter(employee=emp).delete()

                # Delete employee (cascades to related records)
                emp.delete()

                # Delete user
                user.delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Deleted employee {emp_id} '
                        f'(user: {username}, {onboarding_count} onboarding record(s))'
                    )
                )

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS(f'✓ Cleanup complete! Deleted {len(employees_to_delete)} duplicate record(s).'))
            self.stdout.write(self.style.SUCCESS(f'✓ Remaining "John Newbie": {keep_employee.employee_id}'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
        else:
            for emp in employees_to_delete:
                onboarding_count = EmployeeOnboarding.objects.filter(employee=emp).count()
                self.stdout.write(
                    f'  Would delete: {emp.employee_id} '
                    f'(user: {emp.user.username}, {onboarding_count} onboarding record(s))'
                )

            self.stdout.write('')
            self.stdout.write(self.style.WARNING('=' * 60))
            self.stdout.write(self.style.WARNING('[DRY RUN] No changes made. Run without --dry-run to actually delete.'))
            self.stdout.write(self.style.WARNING('=' * 60))
