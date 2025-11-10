from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hr.models import Employee


class Command(BaseCommand):
    help = 'Link a user account to an employee profile'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to link')
        parser.add_argument('--employee-id', type=str, help='Employee ID to link to')
        parser.add_argument('--email', type=str, help='Employee email to search by')
        parser.add_argument('--create', action='store_true', help='Create employee profile if not found')

    def handle(self, *args, **options):
        username = options['username']
        employee_id = options.get('employee_id')
        email = options.get('email')
        create = options.get('create', False)

        # Get user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Found user: {user.username} ({user.email})')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return

        # Check if user already has an employee profile
        if hasattr(user, 'employee') and user.employee:
            self.stdout.write(self.style.WARNING(
                f'User already linked to employee: {user.employee.full_name} (ID: {user.employee.employee_id})'
            ))
            return

        # Find employee
        employee = None
        if employee_id:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                self.stdout.write(f'Found employee by ID: {employee.full_name}')
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Employee with ID "{employee_id}" not found'))
        elif email:
            try:
                employee = Employee.objects.get(email=email)
                self.stdout.write(f'Found employee by email: {employee.full_name}')
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Employee with email "{email}" not found'))

        # Create employee if requested
        if not employee and create:
            self.stdout.write('Creating new employee profile...')
            employee = Employee.objects.create(
                first_name=user.first_name or username,
                last_name=user.last_name or '',
                email=user.email,
                user=user
            )
            self.stdout.write(self.style.SUCCESS(
                f'Created employee profile: {employee.full_name} (ID: {employee.employee_id})'
            ))
        elif not employee:
            self.stdout.write(self.style.ERROR(
                'No employee found. Use --create to create a new employee profile, '
                'or specify --employee-id or --email to link to existing employee.'
            ))
            return

        # Link user to employee
        if employee.user:
            self.stdout.write(self.style.WARNING(
                f'Employee already linked to user: {employee.user.username}'
            ))
            response = input('Do you want to overwrite? (yes/no): ')
            if response.lower() != 'yes':
                self.stdout.write('Cancelled')
                return

        employee.user = user
        employee.save()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully linked user "{user.username}" to employee "{employee.full_name}" (ID: {employee.employee_id})'
        ))
