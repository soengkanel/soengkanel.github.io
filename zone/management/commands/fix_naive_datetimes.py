"""
Management command to fix naive datetime values in the database.
Converts all naive datetime values to timezone-aware values.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = 'Fix naive datetime values in created_at fields by making them timezone-aware'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Import models that have created_at fields
        from zone.models import Worker
        from hr.models import Employee
        from cards.models import CardPrintingHistory, EmployeeCardPrintingHistory
        
        models_to_check = [
            ('Worker', Worker),
            ('Employee', Employee),
            ('CardPrintingHistory', CardPrintingHistory),
            ('EmployeeCardPrintingHistory', EmployeeCardPrintingHistory),
        ]
        
        total_fixed = 0
        
        for model_name, model_class in models_to_check:
            self.stdout.write(f'Checking {model_name}...')
            
            # Get all records
            all_records = model_class.objects.all()
            fixed_count = 0
            
            for record in all_records:
                if hasattr(record, 'created_at') and record.created_at:
                    # Check if the datetime is naive
                    if timezone.is_naive(record.created_at):
                        if not dry_run:
                            # Make it timezone-aware using the default timezone
                            aware_dt = timezone.make_aware(record.created_at)
                            record.created_at = aware_dt
                            record.save(update_fields=['created_at'])
                        
                        fixed_count += 1
                        self.stdout.write(
                            f'  Fixed {model_name} ID {record.pk}: '
                            f'{record.created_at} -> {timezone.make_aware(record.created_at) if not dry_run else "would be made aware"}'
                        )
            
            if fixed_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  Fixed {fixed_count} records in {model_name}')
                )
            else:
                self.stdout.write(f'  No naive datetimes found in {model_name}')
            
            total_fixed += fixed_count
        
        # Also check for any other DateTimeFields that might have naive values
        self.stdout.write('\nChecking other datetime fields...')
        
        # Check Worker model's other datetime fields
        worker_datetime_fields = ['updated_at']
        for field_name in worker_datetime_fields:
            workers = Worker.objects.all()
            fixed = 0
            for worker in workers:
                field_value = getattr(worker, field_name, None)
                if field_value and timezone.is_naive(field_value):
                    if not dry_run:
                        setattr(worker, field_name, timezone.make_aware(field_value))
                        worker.save(update_fields=[field_name])
                    fixed += 1
            
            if fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  Fixed {fixed} Worker.{field_name} fields')
                )
                total_fixed += fixed
        
        # Check Employee model's other datetime fields
        employee_datetime_fields = ['updated_at']
        for field_name in employee_datetime_fields:
            employees = Employee.objects.all()
            fixed = 0
            for employee in employees:
                field_value = getattr(employee, field_name, None)
                if field_value and timezone.is_naive(field_value):
                    if not dry_run:
                        setattr(employee, field_name, timezone.make_aware(field_value))
                        employee.save(update_fields=[field_name])
                    fixed += 1
            
            if fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  Fixed {fixed} Employee.{field_name} fields')
                )
                total_fixed += fixed
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN: Would fix {total_fixed} naive datetime values')
            )
        else:
            if total_fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Successfully fixed {total_fixed} naive datetime values!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('\n✅ No naive datetime values found - all good!')
                )