from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hr.models import Employee, Department, Position
from hr.utils import encrypt_field, decrypt_field
from datetime import date, timedelta
import uuid

class Command(BaseCommand):
    help = 'Creates mock worker data with encrypted fields'

    def handle(self, *args, **kwargs):
        # Create a test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()

        # Create a test department if it doesn't exist
        department, created = Department.objects.get_or_create(
            name='IT Department',
            defaults={
                'code': 'IT',
                'description': 'Information Technology Department',
                'created_by': test_user
            }
        )

        # Create a test position if it doesn't exist
        position, created = Position.objects.get_or_create(
            name='Software Developer',
            defaults={
                'code': 'DEV001',
                'department': department,
                'description': 'Software Development Position',
                'level': 1,
                'created_by': test_user
            }
        )

        # Create a test user for worker 1
        user1, created = User.objects.get_or_create(
            username='mock_worker1',
            defaults={
                'email': 'mock_worker1@example.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user1.set_password('testpass123')
            user1.save()

        # Create a test user for worker 2
        user2, created = User.objects.get_or_create(
            username='mock_worker2',
            defaults={
                'email': 'mock_worker2@example.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user2.set_password('testpass123')
            user2.save()

        # Create mock worker 1
        worker1 = Employee.objects.create(
            user=user1,
            employee_id=f'EMP{uuid.uuid4().hex[:6].upper()}',
            first_name='John',
            last_name='Doe',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            nationality='US',
            marital_status='single',
            phone_number='+1234567890',
            email='john.doe@example.com',
            address='123 Main St, City, Country',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='+1987654321',
            emergency_contact_relationship='Sister',
            department=department,
            position=position,
            employment_status='active',
            hire_date=date.today() - timedelta(days=365),
            id_card_number='ID123456',
            passport_number='P123456789',
            tax_id='T123456789',
            bank_account='B123456789',
            bank_name='Test Bank',
            skills='Python, Django, React',
            education='Bachelor in Computer Science',
            certifications='AWS Certified Developer',
            notes='Senior developer with 5 years experience',
            created_by=test_user
        )

        # Create mock worker 2
        worker2 = Employee.objects.create(
            user=user2,
            employee_id=f'EMP{uuid.uuid4().hex[:6].upper()}',
            first_name='Jane',
            last_name='Smith',
            gender='F',
            date_of_birth=date(1992, 6, 15),
            nationality='UK',
            marital_status='married',
            phone_number='+44123456789',
            email='jane.smith@example.com',
            address='456 High St, London, UK',
            emergency_contact_name='John Smith',
            emergency_contact_phone='+44987654321',
            emergency_contact_relationship='Husband',
            department=department,
            position=position,
            employment_status='active',
            hire_date=date.today() - timedelta(days=180),
            id_card_number='ID789012',
            passport_number='P987654321',
            tax_id='T987654321',
            bank_account='B987654321',
            bank_name='UK Bank',
            skills='Java, Spring Boot, Angular',
            education='Master in Software Engineering',
            certifications='Oracle Certified Professional',
            notes='Full-stack developer with 3 years experience',
            created_by=test_user
        )

        self.stdout.write(self.style.SUCCESS('Successfully created mock workers'))
        
        # Display the encrypted fields for verification
        self.stdout.write('\nVerifying encryption:')
        self.stdout.write('\nWorker 1:')
        self.stdout.write(f'ID Card Number (encrypted): {worker1.id_card_number}')
        self.stdout.write(f'Passport Number (encrypted): {worker1.passport_number}')
        self.stdout.write(f'Tax ID (encrypted): {worker1.tax_id}')
        self.stdout.write(f'Bank Account (encrypted): {worker1.bank_account}')
        
        self.stdout.write('\nWorker 2:')
        self.stdout.write(f'ID Card Number (encrypted): {worker2.id_card_number}')
        self.stdout.write(f'Passport Number (encrypted): {worker2.passport_number}')
        self.stdout.write(f'Tax ID (encrypted): {worker2.tax_id}')
        self.stdout.write(f'Bank Account (encrypted): {worker2.bank_account}') 