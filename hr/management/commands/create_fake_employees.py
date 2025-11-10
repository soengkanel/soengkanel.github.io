import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hr.models import Employee, Department, Position


class Command(BaseCommand):
    help = 'Create 30 fake employee records for testing'

    def handle(self, *args, **options):
        # First, create some departments if they don't exist
        departments_data = [
            ('Human Resources', 'HR'),
            ('Information Technology', 'IT'),
            ('Finance', 'FIN'),
            ('Marketing', 'MKT'),
            ('Sales', 'SAL'),
            ('Operations', 'OPS'),
            ('Customer Service', 'CS'),
            ('Legal', 'LEG'),
            ('Research & Development', 'RND'),
            ('Administration', 'ADM')
        ]
        
        departments = []
        for dept_name, dept_code in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_code,
                defaults={
                    'name': dept_name,
                    'description': f'{dept_name} Department'
                }
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'Created department: {dept_name} ({dept_code})')

        # Create positions for each department
        positions_data = {
            'Human Resources': ['HR Manager', 'HR Specialist', 'Recruiter', 'HR Assistant'],
            'Information Technology': ['Software Developer', 'System Administrator', 'IT Manager', 'DevOps Engineer', 'QA Tester'],
            'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager', 'Budget Analyst'],
            'Marketing': ['Marketing Manager', 'Digital Marketing Specialist', 'Content Creator', 'Marketing Coordinator'],
            'Sales': ['Sales Manager', 'Sales Representative', 'Account Executive', 'Sales Coordinator'],
            'Operations': ['Operations Manager', 'Operations Specialist', 'Process Analyst'],
            'Customer Service': ['Customer Service Manager', 'Customer Service Representative', 'Support Specialist'],
            'Legal': ['Legal Counsel', 'Legal Assistant', 'Compliance Officer'],
            'Research & Development': ['Research Scientist', 'Product Developer', 'R&D Manager'],
            'Administration': ['Administrative Assistant', 'Office Manager', 'Executive Assistant']
        }

        positions = []
        for dept in departments:
            if dept.name in positions_data:
                for i, pos_name in enumerate(positions_data[dept.name], 1):
                    pos_code = f'{dept.code}-{str(i).zfill(2)}'
                    pos, created = Position.objects.get_or_create(
                        code=pos_code,
                        defaults={
                            'name': pos_name,
                            'department': dept,
                            'description': f'{pos_name} in {dept.name}',
                            'level': i
                        }
                    )
                    positions.append(pos)
                    if created:
                        self.stdout.write(f'Created position: {pos_name} in {dept.name} ({pos_code})')

        # Fake employee data
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica',
            'William', 'Ashley', 'James', 'Amanda', 'Christopher', 'Stephanie', 'Daniel',
            'Melissa', 'Matthew', 'Nicole', 'Anthony', 'Elizabeth', 'Mark', 'Helen',
            'Donald', 'Deborah', 'Steven', 'Rachel', 'Paul', 'Carolyn', 'Andrew', 'Janet'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson'
        ]

        nationalities = [
            'American', 'Canadian', 'British', 'Australian', 'German', 'French',
            'Spanish', 'Italian', 'Japanese', 'Korean', 'Chinese', 'Indian',
            'Brazilian', 'Mexican', 'Dutch', 'Swedish'
        ]

        # Delete existing fake employees (optional - comment out if you want to keep existing data)
        # Employee.objects.filter(username__startswith='emp_').delete()

        created_count = 0
        for i in range(30):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'emp_{first_name.lower()}_{last_name.lower()}_{i+1}'
            email = f'{first_name.lower()}.{last_name.lower()}@company.com'
            employee_id = f'EMP{str(i+1).zfill(4)}'

            # Check if user already exists
            if User.objects.filter(username=username).exists():
                continue

            # Random department and position
            department = random.choice(departments)
            dept_positions = [p for p in positions if p.department == department]
            position = random.choice(dept_positions) if dept_positions else None

            # Random dates
            hire_date = date.today() - timedelta(days=random.randint(30, 1825))  # 1 month to 5 years ago
            birth_date = date.today() - timedelta(days=random.randint(8030, 18250))  # 22 to 50 years old

            # Random salary based on position level
            base_salary = 40000
            if position and 'Manager' in position.name:
                salary = random.randint(70000, 120000)
            elif position and any(title in position.name for title in ['Senior', 'Lead', 'Specialist']):
                salary = random.randint(55000, 85000)
            else:
                salary = random.randint(40000, 65000)

            try:
                # First create the User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='password123'
                )
                
                # Then create the Employee
                employee = Employee.objects.create(
                    user=user,
                    employee_id=employee_id,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=birth_date,
                    gender=random.choice(['M', 'F']),
                    nationality=random.choice(nationalities),
                    marital_status=random.choice(['single', 'married', 'divorced', 'widowed']),
                    phone_number=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    email=email,
                    address=f'{random.randint(100, 9999)} {random.choice(["Main", "Oak", "Pine", "Elm", "Cedar"])} {random.choice(["St", "Ave", "Blvd", "Dr"])}, {random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"])}, {random.choice(["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"])} {random.randint(10000, 99999)}',
                    department=department,
                    position=position,
                    hire_date=hire_date,
                    employment_status=random.choice(['active', 'on_leave', 'suspended', 'terminated']),
                    emergency_contact_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                    emergency_contact_phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    emergency_contact_relationship=random.choice(['Spouse', 'Parent', 'Sibling', 'Friend', 'Partner']),
                    notes=f'Generated fake employee data for testing purposes. Hire date: {hire_date}'
                )
                
                created_count += 1
                self.stdout.write(f'Created employee: {employee.full_name} ({employee.employee_id})')
                
            except Exception as e:

                
                pass
                self.stdout.write(
                    self.style.ERROR(f'Error creating employee {first_name} {last_name}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} fake employees!')
        )
        self.stdout.write(f'Total employees in database: {Employee.objects.count()}') 