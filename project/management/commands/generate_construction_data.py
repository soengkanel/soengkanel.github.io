"""
Django Management Command: Generate Construction Projects Sample Data

Usage:
    python manage.py generate_construction_data
    python manage.py generate_construction_data --projects 5  # Generate only 5 projects
    python manage.py generate_construction_data --days 60     # Generate timesheets for 60 days
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from datetime import date, timedelta, datetime
from decimal import Decimal
import random

from project.models import (
    Project, ProjectType, ProjectTeamMember,
    ActivityTypeMaster, Timesheet, TimesheetDetail
)
from hr.models import Employee, Department, Position
from company.models import Company

try:
    from django_tenants.utils import get_tenant_model, schema_context
    TENANTS_ENABLED = True
except ImportError:
    TENANTS_ENABLED = False


class Command(BaseCommand):
    help = 'Generate sample construction projects with payroll-based timesheets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            type=int,
            default=10,
            help='Number of projects to generate (default: 10)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of timesheet data to generate (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before generating new data'
        )
        parser.add_argument(
            '--tenant',
            type=str,
            help='Tenant schema name (required for multi-tenant setups)'
        )

    def handle(self, *args, **options):
        num_projects = options['projects']
        num_days = options['days']
        clear_data = options['clear']
        tenant_name = options.get('tenant')

        # Check if multi-tenant and require tenant parameter
        if TENANTS_ENABLED:
            if not tenant_name:
                # List available tenants
                Tenant = get_tenant_model()
                tenants = list(Tenant.objects.exclude(schema_name='public').values_list('schema_name', flat=True))
                self.stdout.write(self.style.ERROR('Error: Multi-tenant setup detected. Please specify a tenant.'))
                self.stdout.write(f'\nAvailable tenants: {", ".join(tenants)}')
                self.stdout.write(f'\nUsage: python manage.py generate_construction_data --tenant <schema_name>')
                return

            # Get tenant
            Tenant = get_tenant_model()
            try:
                tenant = Tenant.objects.get(schema_name=tenant_name)
            except Tenant.DoesNotExist:
                raise CommandError(f'Tenant "{tenant_name}" does not exist')

            self.stdout.write(self.style.WARNING(f'Using tenant: {tenant_name}'))

            # Run within tenant context
            with schema_context(tenant_name):
                self._generate_data(num_projects, num_days, clear_data)
        else:
            self._generate_data(num_projects, num_days, clear_data)

    def _generate_data(self, num_projects, num_days, clear_data):
        """Generate data (tenant-aware)"""
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('CONSTRUCTION PROJECT DATA GENERATOR'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Current schema: {connection.schema_name}\n')

        try:
            with transaction.atomic():
                if clear_data:
                    self.clear_sample_data()

                # Step 1: Create project types
                project_types = self.create_project_types()

                # Step 2: Create activity types
                activities = self.create_activities()

                # Step 3: Create employees
                employees = self.create_employees()

                # Step 4: Create projects
                projects = self.create_projects(project_types, employees, num_projects)

                # Step 5: Generate timesheets
                self.generate_timesheets(projects, employees, activities, num_days)

            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('DATA GENERATION COMPLETED!'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'\nGenerated:')
            self.stdout.write(f'  - {len(projects)} construction projects')
            self.stdout.write(f'  - {len(employees)} employees')
            self.stdout.write(f'  - {num_days} days of timesheet data')

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise CommandError(f'Error generating data: {str(e)}')

    def clear_sample_data(self):
        """Clear existing sample data"""
        self.stdout.write(self.style.WARNING('\nClearing existing sample data...'))

        # Get construction department employees
        try:
            dept = Department.objects.get(code='CONST')
            employees = Employee.objects.filter(department=dept, employee_type='onsite')

            # Delete timesheets for these employees
            timesheet_count = Timesheet.objects.filter(employee__in=employees).count()
            Timesheet.objects.filter(employee__in=employees).delete()
            self.stdout.write(f'  Deleted {timesheet_count} timesheets')

            # Delete project team members
            team_count = ProjectTeamMember.objects.filter(employee__in=employees).count()
            ProjectTeamMember.objects.filter(employee__in=employees).delete()
            self.stdout.write(f'  Deleted {team_count} team assignments')

            # Delete projects (optional - comment out if you want to keep them)
            project_count = Project.objects.filter(
                project_code__startswith='PRJ-2025'
            ).count()
            Project.objects.filter(project_code__startswith='PRJ-2025').delete()
            self.stdout.write(f'  Deleted {project_count} projects')

            # Delete employees
            emp_count = employees.count()
            employees.delete()
            self.stdout.write(f'  Deleted {emp_count} employees')

            self.stdout.write(self.style.SUCCESS('  Sample data cleared'))

        except Department.DoesNotExist:
            self.stdout.write(self.style.WARNING('  No construction department found, skipping clear'))

    def create_project_types(self):
        """Create construction-specific project types"""
        self.stdout.write('\n=== Creating Project Types ===')

        types_data = [
            {'type_name': 'Building Construction', 'description': 'Residential and commercial buildings'},
            {'type_name': 'Infrastructure', 'description': 'Roads, bridges, and public infrastructure'},
            {'type_name': 'Renovation', 'description': 'Building renovation and refurbishment'},
        ]

        created_types = []
        for data in types_data:
            pt, created = ProjectType.objects.get_or_create(
                type_name=data['type_name'],
                defaults={'description': data['description']}
            )
            created_types.append(pt)
            status = self.style.SUCCESS('Created') if created else self.style.WARNING('Exists')
            self.stdout.write(f'  [{status}] {pt.type_name}')

        return created_types

    def create_activities(self):
        """Create construction activity types"""
        self.stdout.write('\n=== Creating Activity Types ===')

        activities_data = [
            {'name': 'Site Preparation', 'type': 'execution', 'rate': 25.00, 'cost': 18.00},
            {'name': 'Foundation Work', 'type': 'execution', 'rate': 35.00, 'cost': 25.00},
            {'name': 'Structural Work', 'type': 'execution', 'rate': 40.00, 'cost': 30.00},
            {'name': 'Masonry', 'type': 'execution', 'rate': 30.00, 'cost': 22.00},
            {'name': 'Concrete Pouring', 'type': 'execution', 'rate': 35.00, 'cost': 26.00},
            {'name': 'Electrical Installation', 'type': 'execution', 'rate': 45.00, 'cost': 32.00},
            {'name': 'Plumbing Installation', 'type': 'execution', 'rate': 42.00, 'cost': 30.00},
            {'name': 'Painting & Finishing', 'type': 'execution', 'rate': 28.00, 'cost': 20.00},
            {'name': 'Site Inspection', 'type': 'review', 'rate': 50.00, 'cost': 35.00},
            {'name': 'Safety Meeting', 'type': 'meeting', 'rate': 30.00, 'cost': 25.00},
        ]

        created = []
        for data in activities_data:
            activity, is_new = ActivityTypeMaster.objects.get_or_create(
                activity_name=data['name'],
                defaults={
                    'activity_type': data['type'],
                    'billing_rate': data['rate'],
                    'costing_rate': data['cost'],
                    'is_billable': True,
                    'is_active': True
                }
            )
            created.append(activity)
            status = self.style.SUCCESS('Created') if is_new else self.style.WARNING('Exists')
            self.stdout.write(f'  [{status}] {activity.activity_name}')

        return created

    def create_employees(self):
        """Create sample construction workers"""
        self.stdout.write('\n=== Creating Employees ===')

        # Get or create department
        dept, _ = Department.objects.get_or_create(
            code='CONST',
            defaults={'name': 'Construction', 'description': 'On-Site Construction'}
        )

        # Create positions
        positions = []
        for pos_data in [
            {'name': 'Site Supervisor', 'code': 'SUP', 'level': 5},
            {'name': 'Foreman', 'code': 'FORE', 'level': 4},
            {'name': 'Skilled Worker', 'code': 'SKILL', 'level': 3},
            {'name': 'General Worker', 'code': 'GEN', 'level': 2},
        ]:
            pos, _ = Position.objects.get_or_create(
                code=pos_data['code'],
                department=dept,
                defaults={'name': pos_data['name'], 'level': pos_data['level']}
            )
            positions.append(pos)

        # Create employees
        employees_data = [
            ('Sokha', 'Chan', positions[0], 1200),
            ('Dara', 'Kem', positions[0], 1150),
            ('Bopha', 'Sao', positions[1], 900),
            ('Virak', 'Lim', positions[1], 850),
            ('Sophal', 'Touch', positions[1], 880),
            ('Ratana', 'Pov', positions[2], 650),
            ('Sambath', 'Heng', positions[2], 620),
            ('Rith', 'Chea', positions[2], 640),
            ('Mony', 'Sok', positions[3], 450),
            ('Phalla', 'Meas', positions[3], 430),
            ('Vanna', 'Kong', positions[3], 460),
            ('Thyda', 'Noun', positions[3], 440),
        ]

        created = []
        for first, last, pos, salary in employees_data:
            emp = Employee.objects.filter(first_name=first, last_name=last).first()
            if not emp:
                emp = Employee.objects.create(
                    first_name=first,
                    last_name=last,
                    gender='M',
                    date_of_birth=date(1990, 1, 1) + timedelta(days=random.randint(0, 7300)),
                    nationality='KH',
                    address='Phnom Penh, Cambodia',
                    emergency_contact_name='Family',
                    emergency_contact_phone='+855123456789',
                    department=dept,
                    position=pos,
                    employment_status='active',
                    employee_type='onsite',
                    hire_date=date(2020, 1, 1),
                    salary=salary
                )
                self.stdout.write(f'  {self.style.SUCCESS("[Created]")} {emp.full_name}')
            else:
                self.stdout.write(f'  {self.style.WARNING("[Exists]")} {emp.full_name}')
            created.append(emp)

        return created

    def create_projects(self, project_types, employees, count):
        """Create construction projects"""
        self.stdout.write(f'\n=== Creating {count} Projects ===')

        # Use the first company (in tenant context, company represents the tenant)
        company = Company.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR('No company found in tenant. Please create a company first.'))
            return []

        projects_data = [
            ('Riverside Apartment Complex', project_types[0], 8500000, 15000, -90, 365),
            ('CBD Office Tower', project_types[0], 12000000, 22000, -120, 450),
            ('Highway Extension', project_types[1], 25000000, 35000, -180, 540),
            ('Shopping Mall Renovation', project_types[2], 3500000, 8000, -60, 180),
            ('Industrial Warehouse', project_types[0], 6000000, 12000, -45, 270),
            ('Bridge Construction', project_types[1], 15000000, 18000, -150, 400),
            ('School Campus', project_types[0], 7500000, 14000, -100, 330),
            ('Hotel Modernization', project_types[2], 4200000, 9500, -75, 240),
            ('Water Treatment Facility', project_types[1], 10000000, 16000, -200, 480),
            ('Villa Development', project_types[0], 5800000, 11000, -55, 300),
        ]

        created = []
        today = date.today()

        for idx, (name, ptype, cost, hours, offset, duration) in enumerate(projects_data[:count], 1):
            existing = Project.objects.filter(project_name=name).first()
            if existing:
                self.stdout.write(f'  {self.style.WARNING("[Exists]")} {existing.project_code}')
                created.append(existing)
                continue

            start = today + timedelta(days=offset)
            end = start + timedelta(days=duration)

            project = Project.objects.create(
                project_name=name,
                description=f'Construction project: {name}',
                project_type=ptype,
                company=company,
                status='in_progress',
                priority='high' if idx <= 3 else 'medium',
                expected_start_date=start,
                expected_end_date=end,
                actual_start_date=start,
                estimated_cost=cost,
                estimated_hours=hours,
                billing_method='time_and_material',
                is_active=True,
                project_manager=employees[0]
            )

            # Calculate progress
            elapsed = (today - start).days
            progress = min(100, max(0, (elapsed / duration) * 100))
            project.percent_complete = Decimal(str(round(progress, 2)))
            project.save()

            # Assign team
            team = random.sample(employees, random.randint(4, 8))
            for member in team:
                ProjectTeamMember.objects.get_or_create(
                    project=project,
                    employee=member,
                    defaults={
                        'allocation_percentage': random.randint(50, 100),
                        'hourly_rate': Decimal(str(random.randint(15, 50))),
                        'start_date': start,
                        'is_active': True
                    }
                )

            self.stdout.write(f'  {self.style.SUCCESS("[Created]")} {project.project_code} - {name}')
            created.append(project)

        return created

    def generate_timesheets(self, projects, employees, activities, days):
        """Generate timesheet data"""
        self.stdout.write(f'\n=== Generating Timesheets ({days} days) ===')

        company = Company.objects.first()
        today = date.today()
        start = today - timedelta(days=days)

        total = 0
        num_weeks = days // 7

        for week in range(num_weeks):
            week_start = start + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)

            workers = random.sample(employees, random.randint(8, len(employees)))

            for emp in workers:
                if Timesheet.objects.filter(employee=emp, start_date=week_start).exists():
                    continue

                # Generate unique timesheet code
                import uuid
                unique_code = f"TS-{week_start.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

                ts = Timesheet.objects.create(
                    employee=emp,
                    company=company,
                    start_date=week_start,
                    end_date=week_end,
                    status='approved',
                    per_hour_rate=Decimal(str(random.randint(15, 50))),
                    timesheet_code=unique_code
                )

                # Generate entries
                for _ in range(random.randint(4, 6)):
                    work_day = week_start + timedelta(days=random.randint(0, 5))
                    project = random.choice(projects)
                    activity = random.choice(activities)
                    hours = Decimal(str(round(random.uniform(6, 10), 2)))

                    billing_rate = Decimal(str(activity.billing_rate or 30))
                    costing_rate = Decimal(str(activity.costing_rate or 20))

                    TimesheetDetail.objects.create(
                        timesheet=ts,
                        activity_date=work_day,
                        project=project,
                        activity_type=activity,
                        from_time=datetime.strptime('07:00', '%H:%M').time(),
                        to_time=datetime.strptime(f'{7 + int(hours)}:00', '%H:%M').time(),
                        hours=hours,
                        description=f'{activity.activity_name} on {project.project_name}',
                        is_billable=activity.is_billable,
                        billing_rate=billing_rate,
                        billing_amount=hours * billing_rate,
                        costing_rate=costing_rate,
                        costing_amount=hours * costing_rate,
                    )

                ts.calculate_totals()
                ts.save()
                total += 1

        self.stdout.write(f'  Created {total} timesheets')
