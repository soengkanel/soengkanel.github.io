"""
Management command to migrate existing EmployeeSalary basic_salary data to SalaryStructureAssignment.

This command should be run ONCE before removing the basic_salary database field from EmployeeSalary.

Usage:
    python manage.py migrate_employee_salary_to_assignments [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date

from hr.models import Employee
from payroll.models import EmployeeSalary, SalaryStructure, SalaryStructureAssignment


class Command(BaseCommand):
    help = 'Migrate existing EmployeeSalary basic_salary data to SalaryStructureAssignment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually creating records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        self.stdout.write('Starting migration of EmployeeSalary to SalaryStructureAssignment...\n')

        # Get or create a default salary structure
        default_structure, created = SalaryStructure.objects.get_or_create(
            name='Default Salary Structure',
            defaults={
                'is_active': True,
                'docstatus': 1,  # Submitted
                'company': 'Default',
            }
        )

        if created:
            if dry_run:
                self.stdout.write(self.style.SUCCESS(
                    '[DRY RUN] Would create default salary structure'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'Created default salary structure: {default_structure.name}'))

        # Get all EmployeeSalary records that have basic_salary > 0
        # Note: If basic_salary field is already removed, this will fail gracefully
        try:
            employee_salaries = EmployeeSalary.objects.all()
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Could not read EmployeeSalary records. '
                f'This is normal if basic_salary field is already removed from database.\n'
                f'Error: {str(e)}'
            ))
            return

        total_count = 0
        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for emp_salary in employee_salaries:
            total_count += 1
            employee = emp_salary.employee

            try:
                # Try to get basic_salary value
                # This will work if field still exists in DB, otherwise will fail
                try:
                    basic_salary_value = emp_salary.__dict__.get('basic_salary', None)
                    if basic_salary_value is None:
                        # Field doesn't exist in DB or is NULL
                        self.stdout.write(
                            f'  Skipping {employee.get_full_name()}: No basic_salary in database'
                        )
                        skipped_count += 1
                        continue

                    basic_salary = Decimal(str(basic_salary_value))
                except (AttributeError, KeyError):
                    # Field has been removed from database
                    self.stdout.write(
                        f'  Skipping {employee.get_full_name()}: basic_salary field removed from DB'
                    )
                    skipped_count += 1
                    continue

                if basic_salary <= 0:
                    self.stdout.write(
                        f'  Skipping {employee.get_full_name()}: basic_salary is {basic_salary}'
                    )
                    skipped_count += 1
                    continue

                # Check if employee already has an active salary structure assignment
                existing_assignment = SalaryStructureAssignment.objects.filter(
                    employee=employee,
                    is_active=True
                ).first()

                if existing_assignment:
                    self.stdout.write(
                        f'  Skipping {employee.get_full_name()}: Already has active assignment '
                        f'(base_salary: {existing_assignment.base_salary})'
                    )
                    skipped_count += 1
                    continue

                # Create salary structure assignment
                if dry_run:
                    self.stdout.write(self.style.WARNING(
                        f'  [DRY RUN] Would create assignment for {employee.get_full_name()}: '
                        f'base_salary={basic_salary}'
                    ))
                else:
                    with transaction.atomic():
                        assignment = SalaryStructureAssignment.objects.create(
                            employee=employee,
                            salary_structure=default_structure,
                            base_salary=basic_salary,
                            from_date=emp_salary.effective_date or date.today(),
                            is_active=True,
                            docstatus=1,  # Submitted (approved)
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'  ✓ Created assignment for {employee.get_full_name()}: '
                            f'base_salary={basic_salary}'
                        ))

                migrated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f'  ✗ Error migrating {employee.get_full_name()}: {str(e)}'
                ))

        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Migration Summary:'))
        self.stdout.write(f'  Total EmployeeSalary records: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'  Successfully migrated: {migrated_count}'))
        self.stdout.write(self.style.WARNING(f'  Skipped (already exists or no salary): {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  Errors: {error_count}'))

        if dry_run:
            self.stdout.write('\n' + self.style.WARNING(
                'This was a DRY RUN. Run without --dry-run to actually create records.'
            ))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('Migration completed!'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('  1. Verify assignments in Django admin or /payroll/salary-structure-assignment/')
            self.stdout.write('  2. Run: python manage.py makemigrations')
            self.stdout.write('  3. Run: python manage.py migrate')
            self.stdout.write('  4. The basic_salary database column will be removed')
