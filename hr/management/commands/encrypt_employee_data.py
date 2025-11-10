from django.core.management.base import BaseCommand
from django.db import transaction
from hr.models import Employee
from core.encryption import encryption_manager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Encrypt existing employee sensitive data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be encrypted without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Fields that need encryption
        encrypted_fields = [
            'phone_number', 'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'notes'
        ]
        
        employees = Employee.objects.all()
        total_employees = employees.count()
        
        self.stdout.write(f'Found {total_employees} employees to process')
        
        updated_count = 0
        
        with transaction.atomic():
            for i, employee in enumerate(employees, 1):
                updated_fields = []
                
                for field_name in encrypted_fields:
                    value = getattr(employee, field_name)
                    
                    # Only encrypt if value exists and isn't already encrypted
                    if value and not encryption_manager._is_encrypted(str(value)):
                        if not dry_run:
                            # Update the field with encrypted value
                            setattr(employee, field_name, value)  # The field will auto-encrypt on save
                        updated_fields.append(field_name)
                
                if updated_fields:
                    if not dry_run:
                        employee.save(update_fields=updated_fields)
                    updated_count += 1
                    
                    self.stdout.write(
                        f'[{i}/{total_employees}] Employee {employee.employee_id}: '
                        f'{"Would encrypt" if dry_run else "Encrypted"} {", ".join(updated_fields)}'
                    )
                else:
                    self.stdout.write(
                        f'[{i}/{total_employees}] Employee {employee.employee_id}: '
                        f'No encryption needed'
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN COMPLETE: Would encrypt sensitive data for {updated_count} employees'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully encrypted sensitive data for {updated_count} employees'
                )
            )