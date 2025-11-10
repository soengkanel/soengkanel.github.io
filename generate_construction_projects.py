"""
Sample Data Generator for On-Site Construction Projects with Payroll-Based Timesheets

This script generates 10 realistic construction project samples with timesheet data
for a Django-based HRMS system.

Usage:
    python manage.py shell < generate_construction_projects.py
    OR
    python generate_construction_projects.py (if running standalone with Django setup)
"""

import os
import django
import sys
from datetime import date, timedelta, datetime
from decimal import Decimal
import random

# Django setup (if running standalone)
if __name__ == '__main__':
    # Add the project directory to sys.path
    project_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_path)

    # Setup Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from project.models import (
    Project, ProjectType, ProjectTeamMember,
    ActivityTypeMaster, Timesheet, TimesheetDetail
)
from hr.models import Employee, Department, Position
from company.models import Company


def create_construction_project_types():
    """Create construction-specific project types"""
    print("\n=== Creating Construction Project Types ===")

    project_types = [
        {'type_name': 'Building Construction', 'description': 'Residential and commercial building construction'},
        {'type_name': 'Infrastructure', 'description': 'Roads, bridges, and public infrastructure'},
        {'type_name': 'Renovation', 'description': 'Building renovation and refurbishment'},
    ]

    created_types = []
    for pt_data in project_types:
        pt, created = ProjectType.objects.get_or_create(
            type_name=pt_data['type_name'],
            defaults={'description': pt_data['description']}
        )
        created_types.append(pt)
        status = "Created" if created else "Exists"
        print(f"  [{status}] {pt.type_name}")

    return created_types


def create_construction_activities():
    """Create construction-specific activity types"""
    print("\n=== Creating Construction Activity Types ===")

    activities = [
        {'name': 'Site Preparation', 'type': 'execution', 'billing_rate': 25.00, 'costing_rate': 18.00, 'billable': True},
        {'name': 'Foundation Work', 'type': 'execution', 'billing_rate': 35.00, 'costing_rate': 25.00, 'billable': True},
        {'name': 'Structural Work', 'type': 'execution', 'billing_rate': 40.00, 'costing_rate': 30.00, 'billable': True},
        {'name': 'Masonry', 'type': 'execution', 'billing_rate': 30.00, 'costing_rate': 22.00, 'billable': True},
        {'name': 'Concrete Pouring', 'type': 'execution', 'billing_rate': 35.00, 'costing_rate': 26.00, 'billable': True},
        {'name': 'Electrical Installation', 'type': 'execution', 'billing_rate': 45.00, 'costing_rate': 32.00, 'billable': True},
        {'name': 'Plumbing Installation', 'type': 'execution', 'billing_rate': 42.00, 'costing_rate': 30.00, 'billable': True},
        {'name': 'Painting & Finishing', 'type': 'execution', 'billing_rate': 28.00, 'costing_rate': 20.00, 'billable': True},
        {'name': 'Site Inspection', 'type': 'review', 'billing_rate': 50.00, 'costing_rate': 35.00, 'billable': True},
        {'name': 'Safety Meeting', 'type': 'meeting', 'billing_rate': 30.00, 'costing_rate': 25.00, 'billable': False},
    ]

    created_activities = []
    for act_data in activities:
        activity, created = ActivityTypeMaster.objects.get_or_create(
            activity_name=act_data['name'],
            defaults={
                'activity_type': act_data['type'],
                'billing_rate': act_data['billing_rate'],
                'costing_rate': act_data['costing_rate'],
                'is_billable': act_data['billable'],
                'is_active': True
            }
        )
        created_activities.append(activity)
        status = "Created" if created else "Exists"
        print(f"  [{status}] {activity.activity_name} (${activity.billing_rate}/hr)")

    return created_activities


def create_sample_employees():
    """Create sample construction workers/employees"""
    print("\n=== Creating Sample Construction Employees ===")

    # Get or create construction department
    dept, _ = Department.objects.get_or_create(
        code='CONST',
        defaults={'name': 'Construction', 'description': 'Construction and On-Site Operations'}
    )

    # Create positions
    positions_data = [
        {'name': 'Site Supervisor', 'code': 'SUP', 'level': 5},
        {'name': 'Foreman', 'code': 'FORE', 'level': 4},
        {'name': 'Skilled Worker', 'code': 'SKILL', 'level': 3},
        {'name': 'General Worker', 'code': 'GEN', 'level': 2},
    ]

    positions = []
    for pos_data in positions_data:
        pos, _ = Position.objects.get_or_create(
            code=pos_data['code'],
            department=dept,
            defaults={'name': pos_data['name'], 'level': pos_data['level']}
        )
        positions.append(pos)

    # Create sample employees
    employees_data = [
        {'first_name': 'Sokha', 'last_name': 'Chan', 'position': positions[0], 'salary': 1200},
        {'first_name': 'Dara', 'last_name': 'Kem', 'position': positions[0], 'salary': 1150},
        {'first_name': 'Bopha', 'last_name': 'Sao', 'position': positions[1], 'salary': 900},
        {'first_name': 'Virak', 'last_name': 'Lim', 'position': positions[1], 'salary': 850},
        {'first_name': 'Sophal', 'last_name': 'Touch', 'position': positions[1], 'salary': 880},
        {'first_name': 'Ratana', 'last_name': 'Pov', 'position': positions[2], 'salary': 650},
        {'first_name': 'Sambath', 'last_name': 'Heng', 'position': positions[2], 'salary': 620},
        {'first_name': 'Rith', 'last_name': 'Chea', 'position': positions[2], 'salary': 640},
        {'first_name': 'Mony', 'last_name': 'Sok', 'position': positions[3], 'salary': 450},
        {'first_name': 'Phalla', 'last_name': 'Meas', 'position': positions[3], 'salary': 430},
        {'first_name': 'Vanna', 'last_name': 'Kong', 'position': positions[3], 'salary': 460},
        {'first_name': 'Thyda', 'last_name': 'Noun', 'position': positions[3], 'salary': 440},
    ]

    created_employees = []
    for emp_data in employees_data:
        # Check if employee already exists
        existing = Employee.objects.filter(
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name']
        ).first()

        if existing:
            created_employees.append(existing)
            print(f"  [Exists] {existing.full_name} - {existing.position.name}")
        else:
            employee = Employee.objects.create(
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                gender='M',
                date_of_birth=date(1990, 1, 1) + timedelta(days=random.randint(0, 7300)),
                nationality='KH',
                address='Phnom Penh, Cambodia',
                emergency_contact_name='Family',
                emergency_contact_phone='+855123456789',
                department=dept,
                position=emp_data['position'],
                employment_status='active',
                employee_type='onsite',
                hire_date=date(2020, 1, 1) + timedelta(days=random.randint(0, 1000)),
                salary=emp_data['salary']
            )
            created_employees.append(employee)
            print(f"  [Created] {employee.full_name} - {employee.position.name} (${employee.salary})")

    return created_employees


def create_construction_projects(project_types, employees):
    """Create 10 sample construction projects"""
    print("\n=== Creating 10 Construction Projects ===")

    # Get or create company
    company, _ = Company.objects.get_or_create(
        name='NextHR Construction Ltd.',
        defaults={
            'address': '123 Build Street, Phnom Penh',
            'phone': '+855123456789',
            'email': 'info@nexthr-const.com'
        }
    )

    projects_data = [
        {
            'name': 'Riverside Apartment Complex',
            'description': '15-story residential building with 120 units along the Mekong River',
            'type': project_types[0],  # Building Construction
            'status': 'in_progress',
            'estimated_cost': 8500000,
            'estimated_hours': 15000,
            'start_offset': -90,
            'duration': 365,
        },
        {
            'name': 'Central Business District Office Tower',
            'description': '22-floor commercial office building in downtown area',
            'type': project_types[0],
            'status': 'in_progress',
            'estimated_cost': 12000000,
            'estimated_hours': 22000,
            'start_offset': -120,
            'duration': 450,
        },
        {
            'name': 'National Highway 6A Extension',
            'description': '25km highway extension with 3 bridges',
            'type': project_types[1],  # Infrastructure
            'status': 'in_progress',
            'estimated_cost': 25000000,
            'estimated_hours': 35000,
            'start_offset': -180,
            'duration': 540,
        },
        {
            'name': 'Shopping Mall Renovation',
            'description': 'Complete renovation of 3-story shopping mall including facade and interiors',
            'type': project_types[2],  # Renovation
            'status': 'in_progress',
            'estimated_cost': 3500000,
            'estimated_hours': 8000,
            'start_offset': -60,
            'duration': 180,
        },
        {
            'name': 'Industrial Warehouse Complex',
            'description': '5 warehouse buildings for logistics operations',
            'type': project_types[0],
            'status': 'in_progress',
            'estimated_cost': 6000000,
            'estimated_hours': 12000,
            'start_offset': -45,
            'duration': 270,
        },
        {
            'name': 'Siem Reap Bridge Construction',
            'description': 'New suspension bridge across Siem Reap river',
            'type': project_types[1],
            'status': 'in_progress',
            'estimated_cost': 15000000,
            'estimated_hours': 18000,
            'start_offset': -150,
            'duration': 400,
        },
        {
            'name': 'School Campus Development',
            'description': 'New international school campus with 4 buildings',
            'type': project_types[0],
            'status': 'in_progress',
            'estimated_cost': 7500000,
            'estimated_hours': 14000,
            'start_offset': -100,
            'duration': 330,
        },
        {
            'name': 'Hotel Modernization Project',
            'description': 'Full renovation and modernization of 8-story hotel',
            'type': project_types[2],
            'status': 'in_progress',
            'estimated_cost': 4200000,
            'estimated_hours': 9500,
            'start_offset': -75,
            'duration': 240,
        },
        {
            'name': 'Water Treatment Facility',
            'description': 'New water treatment and distribution facility',
            'type': project_types[1],
            'status': 'in_progress',
            'estimated_cost': 10000000,
            'estimated_hours': 16000,
            'start_offset': -200,
            'duration': 480,
        },
        {
            'name': 'Residential Villa Development',
            'description': 'Luxury villa community with 25 units',
            'type': project_types[0],
            'status': 'in_progress',
            'estimated_cost': 5800000,
            'estimated_hours': 11000,
            'start_offset': -55,
            'duration': 300,
        },
    ]

    created_projects = []
    today = date.today()

    for idx, proj_data in enumerate(projects_data, 1):
        start_date = today + timedelta(days=proj_data['start_offset'])
        end_date = start_date + timedelta(days=proj_data['duration'])

        # Check if project exists
        existing = Project.objects.filter(project_name=proj_data['name']).first()
        if existing:
            print(f"  [Exists] {existing.project_code} - {existing.project_name}")
            created_projects.append(existing)
            continue

        project = Project.objects.create(
            project_name=proj_data['name'],
            description=proj_data['description'],
            project_type=proj_data['type'],
            company=company,
            status=proj_data['status'],
            priority='high' if idx <= 3 else 'medium',
            expected_start_date=start_date,
            expected_end_date=end_date,
            actual_start_date=start_date,
            estimated_cost=proj_data['estimated_cost'],
            estimated_hours=proj_data['estimated_hours'],
            billing_method='time_and_material',
            is_active=True,
        )

        # Assign project manager (first supervisor)
        project.project_manager = employees[0]

        # Calculate progress based on time elapsed
        days_elapsed = (today - start_date).days
        total_days = proj_data['duration']
        progress = min(100, max(0, (days_elapsed / total_days) * 100))
        project.percent_complete = Decimal(str(round(progress, 2)))
        project.save()

        # Assign team members (4-8 workers per project)
        team_size = random.randint(4, 8)
        team_members = random.sample(employees, team_size)

        for member in team_members:
            ProjectTeamMember.objects.get_or_create(
                project=project,
                employee=member,
                defaults={
                    'allocation_percentage': random.randint(50, 100),
                    'hourly_rate': Decimal(str(random.randint(15, 50))),
                    'start_date': start_date,
                    'is_active': True,
                }
            )

        print(f"  [Created] {project.project_code} - {project.project_name}")
        print(f"            Progress: {project.percent_complete}% | Team: {team_size} workers")
        created_projects.append(project)

    return created_projects


def generate_timesheets(projects, employees, activities):
    """Generate timesheet entries for the last 30 days"""
    print("\n=== Generating Timesheets (Last 30 Days) ===")

    # Get or create company
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(
            name='NextHR Construction Ltd.',
            address='123 Build Street, Phnom Penh'
        )

    today = date.today()
    start_date = today - timedelta(days=30)

    total_timesheets = 0
    total_hours = 0

    # Generate timesheets for each week
    for week_offset in range(0, 5):  # 5 weeks
        week_start = start_date + timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)

        print(f"\n  Week {week_offset + 1}: {week_start} to {week_end}")

        # Select random employees for this week (8-12 employees)
        working_employees = random.sample(employees, random.randint(8, min(12, len(employees))))

        for employee in working_employees:
            # Check if timesheet exists
            existing_timesheet = Timesheet.objects.filter(
                employee=employee,
                start_date=week_start,
                end_date=week_end
            ).first()

            if existing_timesheet:
                continue

            # Create timesheet
            timesheet = Timesheet.objects.create(
                employee=employee,
                company=company,
                start_date=week_start,
                end_date=week_end,
                status='approved',
                per_hour_rate=Decimal(str(random.randint(15, 50)))
            )

            # Generate 4-6 timesheet entries per week
            num_entries = random.randint(4, 6)
            week_hours = 0

            for _ in range(num_entries):
                # Random work day in the week (Monday-Saturday)
                work_day = week_start + timedelta(days=random.randint(0, 5))

                # Random project
                project = random.choice(projects)

                # Random activity
                activity = random.choice(activities)

                # Random hours (6-10 hours per day)
                hours = Decimal(str(round(random.uniform(6, 10), 2)))
                week_hours += float(hours)

                # Calculate billing
                billing_rate = activity.billing_rate or Decimal('30')
                billing_amount = hours * billing_rate
                costing_rate = activity.costing_rate or Decimal('20')
                costing_amount = hours * costing_rate

                # Create timesheet detail
                TimesheetDetail.objects.create(
                    timesheet=timesheet,
                    activity_date=work_day,
                    project=project,
                    activity_type=activity,
                    from_time=datetime.strptime('07:00', '%H:%M').time(),
                    to_time=datetime.strptime(f'{7 + int(hours)}:00', '%H:%M').time(),
                    hours=hours,
                    description=f"{activity.activity_name} on {project.project_name}",
                    is_billable=activity.is_billable,
                    billing_rate=billing_rate,
                    billing_amount=billing_amount,
                    costing_rate=costing_rate,
                    costing_amount=costing_amount,
                )

                total_hours += float(hours)

            # Update timesheet totals
            timesheet.calculate_totals()
            timesheet.submitted_date = week_start
            timesheet.approved_date = week_start + timedelta(days=1)
            timesheet.save()

            total_timesheets += 1
            print(f"    {employee.full_name}: {num_entries} entries, {week_hours:.1f} hours")

    print(f"\n  Total Timesheets Created: {total_timesheets}")
    print(f"  Total Hours Logged: {total_hours:.1f}")

    return total_timesheets


def main():
    """Main execution function"""
    print("="*60)
    print("CONSTRUCTION PROJECT & TIMESHEET DATA GENERATOR")
    print("="*60)

    try:
        # Step 1: Create project types
        project_types = create_construction_project_types()

        # Step 2: Create activity types
        activities = create_construction_activities()

        # Step 3: Create employees
        employees = create_sample_employees()

        # Step 4: Create projects
        projects = create_construction_projects(project_types, employees)

        # Step 5: Generate timesheets
        generate_timesheets(projects, employees, activities)

        print("\n" + "="*60)
        print("DATA GENERATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  - Project Types: {len(project_types)}")
        print(f"  - Activity Types: {len(activities)}")
        print(f"  - Employees: {len(employees)}")
        print(f"  - Projects: {len(projects)}")
        print(f"\nYou can now:")
        print(f"  1. View projects in the Django admin or project list")
        print(f"  2. View timesheets for payroll processing")
        print(f"  3. Generate reports and analytics")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
