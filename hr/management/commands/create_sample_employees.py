from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from hr.models import Employee, Department, Position
from datetime import date
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Creates sample employee data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing employees before creating new ones',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['clear']:
                self.stdout.write('Clearing existing employees...')
                Employee.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Cleared existing employees'))

            # Create departments
            self.stdout.write('Creating departments...')
            departments = self.create_departments()

            # Create positions
            self.stdout.write('Creating positions...')
            positions = self.create_positions(departments)

            # Create employees
            self.stdout.write('Creating employees...')
            employees = self.create_employees(departments, positions)

            self.stdout.write(self.style.SUCCESS(
                f'\nSuccessfully created:\n'
                f'  - {len(departments)} departments\n'
                f'  - {len(positions)} positions\n'
                f'  - {len(employees)} employees\n'
            ))

            self.stdout.write(self.style.WARNING(
                '\nDefault credentials for all users:\n'
                '  Username: [first_name].[last_name] (lowercase)\n'
                '  Password: password123\n'
                '  Example: lim.theara / password123'
            ))

    def create_departments(self):
        departments_data = [
            ('IT', 'Information Technology', 'IT Department responsible for software and infrastructure'),
            ('HR', 'Human Resources', 'HR Department managing employee relations and recruitment'),
            ('FIN', 'Finance', 'Finance Department handling accounting and budgeting'),
            ('OPS', 'Operations', 'Operations Department managing daily business operations'),
            ('MKT', 'Marketing', 'Marketing Department handling promotions and branding'),
            ('SD', 'Structural Design', 'Structural Design Department for engineering projects'),
        ]

        departments = []
        for code, name, description in departments_data:
            dept, created = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description}
            )
            if created:
                self.stdout.write(f'  Created department: {name}')
            departments.append(dept)

        return departments

    def create_positions(self, departments):
        positions_data = [
            ('DIR', 'Director', 4),
            ('MGR', 'Manager', 3),
            ('SR_DEV', 'Senior Developer', 2),
            ('JR_DEV', 'Junior Developer', 1),
            ('SR_ACCT', 'Senior Accountant', 2),
            ('JR_ACCT', 'Junior Accountant', 1),
            ('HR_MGR', 'HR Manager', 3),
            ('HR_SPEC', 'HR Specialist', 2),
            ('MKT_MGR', 'Marketing Manager', 3),
            ('MKT_EXEC', 'Marketing Executive', 2),
            ('OPS_MGR', 'Operations Manager', 3),
            ('OPS_COORD', 'Operations Coordinator', 1),
            ('SD_DIR', 'Structural Design Director', 4),
            ('ADMIN', 'Administrator', 1),
        ]

        positions = []
        for i, (code, name, level) in enumerate(positions_data):
            # Assign positions to departments in a meaningful way
            if 'Director' in name:
                dept = departments[i % len(departments)]
            elif 'Developer' in name:
                dept = next((d for d in departments if d.code == 'IT'), departments[0])
            elif 'Accountant' in name:
                dept = next((d for d in departments if d.code == 'FIN'), departments[2])
            elif 'HR' in name:
                dept = next((d for d in departments if d.code == 'HR'), departments[1])
            elif 'Marketing' in name:
                dept = next((d for d in departments if d.code == 'MKT'), departments[4])
            elif 'Operations' in name:
                dept = next((d for d in departments if d.code == 'OPS'), departments[3])
            elif 'Structural' in name:
                dept = next((d for d in departments if d.code == 'SD'), departments[5])
            else:
                dept = random.choice(departments)

            pos, created = Position.objects.get_or_create(
                code=code,
                defaults={'name': name, 'department': dept, 'level': level}
            )
            if created:
                self.stdout.write(f'  Created position: {name} in {dept.name}')
            positions.append(pos)

        return positions

    def create_employees(self, departments, positions):
        employees_data = [
            {
                'employee_id': '200070',
                'first_name': 'Lim',
                'last_name': 'Theara',
                'username': 'lim.theara',
                'gender': 'M',
                'nationality': 'KH',
                'phone_number': '+85512345678',
                'email': 'lim.theara@company.com',
                'address': '123 Street A, Phnom Penh',
                'emergency_contact_name': 'Lim Sopheap',
                'emergency_contact_phone': '+85512345679',
                'date_of_birth': date(1990, 5, 15),
                'hire_date': date(2020, 3, 1),
                'salary': Decimal('1500.00'),
                'work_location': 'Head Office',
                'department_code': 'SD',
                'position_code': 'SD_DIR'
            },
            {
                'employee_id': '200071',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'username': 'sarah.johnson',
                'gender': 'F',
                'nationality': 'GB',
                'phone_number': '+85523456789',
                'email': 'sarah.johnson@company.com',
                'address': '456 Street B, Phnom Penh',
                'emergency_contact_name': 'Mike Johnson',
                'emergency_contact_phone': '+85523456790',
                'date_of_birth': date(1988, 8, 22),
                'hire_date': date(2019, 6, 15),
                'salary': Decimal('2000.00'),
                'work_location': 'Head Office',
                'department_code': 'HR',
                'position_code': 'HR_MGR'
            },
            {
                'employee_id': '200072',
                'first_name': 'Michael',
                'last_name': 'Davis',
                'username': 'michael.davis',
                'gender': 'M',
                'nationality': 'CA',
                'phone_number': '+85534567890',
                'email': 'michael.davis@company.com',
                'address': '789 Street C, Phnom Penh',
                'emergency_contact_name': 'Lisa Davis',
                'emergency_contact_phone': '+85534567891',
                'date_of_birth': date(1985, 3, 10),
                'hire_date': date(2018, 1, 10),
                'salary': Decimal('2500.00'),
                'work_location': 'Head Office',
                'department_code': 'FIN',
                'position_code': 'DIR'
            },
            {
                'employee_id': '200073',
                'first_name': 'Emily',
                'last_name': 'Wilson',
                'username': 'emily.wilson',
                'gender': 'F',
                'nationality': 'AU',
                'phone_number': '+85545678901',
                'email': 'emily.wilson@company.com',
                'address': '321 Street D, Phnom Penh',
                'emergency_contact_name': 'James Wilson',
                'emergency_contact_phone': '+85545678902',
                'date_of_birth': date(1992, 11, 30),
                'hire_date': date(2021, 2, 1),
                'salary': Decimal('1200.00'),
                'work_location': 'Branch Office',
                'department_code': 'MKT',
                'position_code': 'MKT_EXEC'
            },
            {
                'employee_id': '200074',
                'first_name': 'David',
                'last_name': 'Brown',
                'username': 'david.brown',
                'gender': 'M',
                'nationality': 'NZ',
                'phone_number': '+85556789012',
                'email': 'david.brown@company.com',
                'address': '654 Street E, Phnom Penh',
                'emergency_contact_name': 'Mary Brown',
                'emergency_contact_phone': '+85556789013',
                'date_of_birth': date(1987, 7, 18),
                'hire_date': date(2020, 8, 15),
                'salary': Decimal('1800.00'),
                'work_location': 'Head Office',
                'department_code': 'IT',
                'position_code': 'SR_DEV'
            },
            {
                'employee_id': '200075',
                'first_name': 'Sophea',
                'last_name': 'Chan',
                'username': 'sophea.chan',
                'gender': 'F',
                'nationality': 'KH',
                'phone_number': '+85567890123',
                'email': 'sophea.chan@company.com',
                'address': '987 Street F, Phnom Penh',
                'emergency_contact_name': 'Dara Chan',
                'emergency_contact_phone': '+85567890124',
                'date_of_birth': date(1993, 4, 25),
                'hire_date': date(2022, 1, 10),
                'salary': Decimal('800.00'),
                'work_location': 'Head Office',
                'department_code': 'OPS',
                'position_code': 'OPS_COORD'
            },
            {
                'employee_id': '200076',
                'first_name': 'Visal',
                'last_name': 'Sok',
                'username': 'visal.sok',
                'gender': 'M',
                'nationality': 'KH',
                'phone_number': '+85578901234',
                'email': 'visal.sok@company.com',
                'address': '147 Street G, Phnom Penh',
                'emergency_contact_name': 'Srey Sok',
                'emergency_contact_phone': '+85578901235',
                'date_of_birth': date(1989, 9, 12),
                'hire_date': date(2019, 11, 1),
                'salary': Decimal('1000.00'),
                'work_location': 'Head Office',
                'department_code': 'IT',
                'position_code': 'JR_DEV'
            },
            {
                'employee_id': '200077',
                'first_name': 'Jennifer',
                'last_name': 'Martinez',
                'username': 'jennifer.martinez',
                'gender': 'F',
                'nationality': 'ES',
                'phone_number': '+85589012345',
                'email': 'jennifer.martinez@company.com',
                'address': '258 Street H, Phnom Penh',
                'emergency_contact_name': 'Carlos Martinez',
                'emergency_contact_phone': '+85589012346',
                'date_of_birth': date(1991, 2, 28),
                'hire_date': date(2021, 5, 15),
                'salary': Decimal('1600.00'),
                'work_location': 'Branch Office',
                'department_code': 'HR',
                'position_code': 'HR_SPEC'
            },
            {
                'employee_id': '200078',
                'first_name': 'Robert',
                'last_name': 'Taylor',
                'username': 'robert.taylor',
                'gender': 'M',
                'nationality': 'US',
                'phone_number': '+85590123456',
                'email': 'robert.taylor@company.com',
                'address': '369 Street I, Phnom Penh',
                'emergency_contact_name': 'Linda Taylor',
                'emergency_contact_phone': '+85590123457',
                'date_of_birth': date(1986, 6, 5),
                'hire_date': date(2018, 9, 1),
                'salary': Decimal('3000.00'),
                'work_location': 'Head Office',
                'department_code': 'OPS',
                'position_code': 'OPS_MGR'
            },
            {
                'employee_id': '200079',
                'first_name': 'Makara',
                'last_name': 'Ly',
                'username': 'makara.ly',
                'gender': 'M',
                'nationality': 'KH',
                'phone_number': '+85501234567',
                'email': 'makara.ly@company.com',
                'address': '741 Street J, Phnom Penh',
                'emergency_contact_name': 'Sophorn Ly',
                'emergency_contact_phone': '+85501234568',
                'date_of_birth': date(1994, 12, 20),
                'hire_date': date(2023, 3, 1),
                'salary': Decimal('600.00'),
                'work_location': 'Branch Office',
                'department_code': 'FIN',
                'position_code': 'JR_ACCT'
            }
        ]

        employees = []
        for emp_data in employees_data:
            # Extract username and position/department codes
            username = emp_data.pop('username')
            dept_code = emp_data.pop('department_code')
            pos_code = emp_data.pop('position_code')

            # Find department and position
            department = next((d for d in departments if d.code == dept_code), departments[0])
            position = next((p for p in positions if p.code == pos_code), positions[0])

            # Create or get user
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'email': emp_data['email'],
                    'is_active': True,
                }
            )

            if user_created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {username}')

            # Create employee
            employee, emp_created = Employee.objects.get_or_create(
                employee_id=emp_data['employee_id'],
                defaults={
                    'user': user,
                    'department': department,
                    'position': position,
                    'employment_status': 'active',
                    **emp_data
                }
            )

            if emp_created:
                self.stdout.write(self.style.SUCCESS(
                    f'  Created employee: {emp_data["first_name"]} {emp_data["last_name"]} '
                    f'(ID: {emp_data["employee_id"]}) - {position.name} at {department.name}'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'  Employee already exists: {emp_data["employee_id"]}'
                ))

            employees.append(employee)

        return employees