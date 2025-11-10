from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from project.models import Project, ProjectTeamMember, ProjectType
from hr.models import Employee, Department
from company.models import Company, Group


class Command(BaseCommand):
    help = 'Create test data for project management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        try:
            # Get or create a group first
            group, created = Group.objects.get_or_create(
                name='Test Group',
                defaults={
                    'description': 'Test group for project management demo',
                }
            )
            self.stdout.write(f'Group: {group.name}')

            # Get or create a company
            company, created = Company.objects.get_or_create(
                name='Test Company',
                defaults={
                    'schema_name': 'test_company',
                    'group': group,
                }
            )
            self.stdout.write(f'Company: {company.name}')

            # Get or create a department
            department, created = Department.objects.get_or_create(
                name='IT Department',
                defaults={'code': 'IT'}
            )

            # Get or create a project type
            project_type, created = ProjectType.objects.get_or_create(
                type_name='Web Development',
                defaults={'description': 'Web application development projects'}
            )

            # Create or get a test user
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')

            # Create or get employee
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': 'EMP001',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'gender': 'M',
                    'date_of_birth': date(1990, 1, 1),
                    'nationality': 'KH',
                    'address': 'Test Address',
                    'emergency_contact_name': 'Emergency Contact',
                    'emergency_contact_phone': '0123456789',
                    'department': department,
                    'hire_date': date.today(),
                }
            )
            if created:
                self.stdout.write(f'Created employee: {employee}')

            # Create test projects
            projects_data = [
                {
                    'project_name': 'E-commerce Platform',
                    'description': 'Building an online shopping platform',
                    'project_code': 'ECOM001',
                },
                {
                    'project_name': 'Mobile App Development',
                    'description': 'Creating a mobile application for customer engagement',
                    'project_code': 'MOB001',
                },
                {
                    'project_name': 'Website Redesign',
                    'description': 'Redesigning company website with modern UI/UX',
                    'project_code': 'WEB001',
                },
            ]

            for project_data in projects_data:
                project, created = Project.objects.get_or_create(
                    project_code=project_data['project_code'],
                    defaults={
                        'project_name': project_data['project_name'],
                        'description': project_data['description'],
                        'project_type': project_type,
                        'company': company,
                        'department': department,
                        'project_manager': employee,
                        'expected_start_date': date.today(),
                        'expected_end_date': date.today() + timedelta(days=90),
                        'status': 'in_progress',
                        'priority': 'medium',
                        'estimated_hours': 200,
                        'estimated_cost': 50000,
                        'created_by': user,
                    }
                )
                if created:
                    self.stdout.write(f'Created project: {project}')

                # Assign employee to project
                team_member, created = ProjectTeamMember.objects.get_or_create(
                    project=project,
                    employee=employee,
                    defaults={
                        'role': 'Developer',
                        'allocation_percentage': 80,
                        'hourly_rate': 25,
                        'start_date': date.today(),
                    }
                )
                if created:
                    self.stdout.write(f'Assigned {employee} to {project}')

            self.stdout.write(
                self.style.SUCCESS('Successfully created test data!')
            )
            self.stdout.write('Test user credentials: testuser / testpass123')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test data: {e}')
            )