from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from hr.models import Employee, Department, Position, EmployeeOnboarding, ProbationPeriod, OnboardingTemplate
import random

User = get_user_model()


def assign_user_role(user):
    """Assign 'User' role to the employee"""
    try:
        from user_management.models import Role, UserRoleAssignment
        user_role, created = Role.objects.get_or_create(
            name='User',
            defaults={
                'description': 'Basic employee user with standard permissions',
                'is_active': True
            }
        )
        UserRoleAssignment.objects.get_or_create(
            user=user,
            defaults={
                'role': user_role,
                'is_active': True
            }
        )
        return True
    except:
        return False


class Command(BaseCommand):
    help = 'Creates a test new employee with onboarding record for testing the onboarding portal'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating test new employee with onboarding...'))

        # Generate unique username
        username = 'newemployee'
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'newemployee{counter}'
            counter += 1

        # Create User
        user = User.objects.create_user(
            username=username,
            email=f'{username}@company.com',
            password='test123',  # Simple password for testing
            first_name='John',
            last_name='Newbie'
        )
        self.stdout.write(self.style.SUCCESS(f'[OK] Created user: {username}'))

        # Assign User role
        if assign_user_role(user):
            self.stdout.write(self.style.SUCCESS(f'[OK] Assigned "User" role to {username}'))
        else:
            self.stdout.write(self.style.WARNING('[WARNING] Could not assign User role - user may see admin menus'))

        # Get a department and position
        department = Department.objects.first()
        position = Position.objects.first()

        if not department:
            self.stdout.write(self.style.ERROR('[ERROR] No departments found. Please create at least one department first.'))
            user.delete()
            return

        if not position:
            self.stdout.write(self.style.ERROR('[ERROR] No positions found. Please create at least one position first.'))
            user.delete()
            return

        # Create Employee (recently hired - within last 7 days)
        today = timezone.now().date()
        hire_date = today - timedelta(days=random.randint(1, 7))

        employee = Employee.objects.create(
            user=user,
            employee_id=f'EMP{random.randint(10000, 99999)}',
            first_name='John',
            last_name='Newbie',
            date_of_birth=timezone.now().date() - timedelta(days=365 * 25),  # 25 years old
            gender='M',
            email=f'{username}@company.com',
            phone_number='+855123456789',
            address='123 Main Street, Phnom Penh, Cambodia',
            emergency_contact_name='Jane Newbie',
            emergency_contact_phone='+855987654321',
            hire_date=hire_date,
            department=department,
            position=position,
            employment_status='active',
            employee_type='backoffice',
            work_type='office',
            nationality='KH',
        )
        self.stdout.write(self.style.SUCCESS(f'[OK] Created employee: {employee.get_full_name()} (ID: {employee.employee_id})'))
        self.stdout.write(self.style.SUCCESS(f'  Hired on: {hire_date}'))

        # Get a manager (random employee who is not this new employee)
        manager = Employee.objects.exclude(id=employee.id).filter(
            employment_status='active'
        ).first()

        # Get a buddy (random employee who is not this new employee and not the manager)
        buddy = Employee.objects.exclude(id=employee.id).filter(
            employment_status='active'
        ).exclude(id=manager.id if manager else None).first()

        # Create or get onboarding template
        template, created = OnboardingTemplate.objects.get_or_create(
            name='Standard Employee Onboarding',
            defaults={
                'description': 'Standard onboarding process for new employees',
                'total_duration_days': 30,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Created onboarding template: {template.name}'))

        # Create EmployeeOnboarding
        onboarding = EmployeeOnboarding.objects.create(
            employee=employee,
            template=template,
            start_date=hire_date,
            expected_completion_date=hire_date + timedelta(days=30),
            status='in_progress',
            manager=manager,
            buddy=buddy,
            total_tasks=10,
            completed_tasks=6,  # 60% complete
            notes='Welcome to the team! Please complete your remaining onboarding tasks.',
            created_by=user,
        )
        self.stdout.write(self.style.SUCCESS(f'[OK] Created onboarding record: {onboarding.progress_percentage}% complete'))

        # Create ProbationPeriod
        probation = ProbationPeriod.objects.create(
            employee=employee,
            start_date=hire_date,
            original_end_date=hire_date + timedelta(days=90),
            status='active',
            evaluation_notes='Regular 90-day probation period for new hire.'
        )
        self.stdout.write(self.style.SUCCESS(f'[OK] Created probation period: {probation.start_date} to {probation.original_end_date}'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Test Employee Created Successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Password: test123'))
        self.stdout.write(self.style.SUCCESS(f'Email: {username}@company.com'))
        self.stdout.write(self.style.SUCCESS(f'Employee ID: {employee.employee_id}'))
        self.stdout.write(self.style.SUCCESS(f'Full Name: {employee.get_full_name()}'))
        self.stdout.write(self.style.SUCCESS(f'Department: {department.name}'))
        self.stdout.write(self.style.SUCCESS(f'Position: {position.name}'))
        self.stdout.write(self.style.SUCCESS(f'Hire Date: {hire_date}'))
        self.stdout.write(self.style.SUCCESS(f'Onboarding Progress: {onboarding.progress_percentage}%'))
        if manager:
            self.stdout.write(self.style.SUCCESS(f'Manager: {manager.get_full_name()}'))
        if buddy:
            self.stdout.write(self.style.SUCCESS(f'Onboarding Buddy: {buddy.get_full_name()}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('You can now log in with the above credentials to test the onboarding portal!'))
        self.stdout.write(self.style.WARNING('Access the onboarding page at: /employee/onboarding/'))
