from django.core.management.base import BaseCommand
from django.utils import timezone
from hr.models import Employee
from leave.models import LeaveType, LeaveAllocation


class Command(BaseCommand):
    help = 'Allocate leave to employees for the current year'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-id',
            type=int,
            help='Specific employee ID to allocate leave for',
        )
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year,
            help='Year for leave allocation',
        )

    def handle(self, *args, **options):
        year = options['year']
        employee_id = options.get('employee_id')

        # Get employees
        if employee_id:
            employees = Employee.objects.filter(id=employee_id)
        else:
            employees = Employee.objects.filter(employment_status='active')

        if not employees.exists():
            self.stdout.write(self.style.ERROR('No employees found'))
            return

        # Get all active leave types
        leave_types = LeaveType.objects.filter(is_active=True)

        if not leave_types.exists():
            self.stdout.write(self.style.ERROR('No leave types found. Please create leave types first.'))
            return

        # Default allocations
        default_allocations = {
            'AL': 20,  # Annual Leave
            'SL': 15,  # Sick Leave
            'PL': 5,   # Personal Leave
            'ML': 90,  # Maternity Leave
            'PaL': 7,  # Paternity Leave
        }

        allocated_count = 0
        from_date = timezone.datetime(year, 1, 1).date()
        to_date = timezone.datetime(year, 12, 31).date()

        for employee in employees:
            self.stdout.write(f'\nProcessing {employee.full_name}...')

            for leave_type in leave_types:
                # Check if allocation already exists
                existing = LeaveAllocation.objects.filter(
                    employee=employee,
                    leave_type=leave_type,
                    year=year
                ).first()

                if existing:
                    self.stdout.write(f'  - {leave_type.code}: Already allocated ({existing.allocated_days} days)')
                    continue

                # Get default allocation for this leave type
                allocated_days = default_allocations.get(
                    leave_type.code,
                    leave_type.max_days_per_year
                )

                # Create allocation
                allocation = LeaveAllocation.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    allocated_days=allocated_days,
                    used_days=0,
                    carried_forward=0,
                    from_date=from_date,
                    to_date=to_date,
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'  - {leave_type.code}: Allocated {allocated_days} days'
                    )
                )
                allocated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {allocated_count} leave allocations for {employees.count()} employee(s)'
            )
        )
