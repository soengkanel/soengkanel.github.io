from django.core.management.base import BaseCommand
from django.db import transaction, models
from django.db.models import Q, Count, F
from zone.models import Worker
from hr.models import Employee

class Command(BaseCommand):
    help = 'Synchronize and validate field consistency across Worker, Employee, and VIP models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix inconsistencies found (default is to only report)',
        )
        parser.add_argument(
            '--model',
            choices=['worker', 'employee', 'vip', 'all'],
            default='all',
            help='Specify which model to check (default: all)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting field synchronization check...'))
        
        models_to_check = []
        if options['model'] in ['worker', 'all']:
            models_to_check.append(('Worker', Worker))
        if options['model'] in ['employee', 'all']:
            models_to_check.append(('Employee', Employee))
        if options['model'] in ['vip', 'all']:
            models_to_check.append(('VIP', VIP))

        for model_name, model_class in models_to_check:
            self.stdout.write(f'\\n=== {model_name} Model Analysis ===')
            self.check_model_consistency(model_name, model_class, options['fix'])

    def check_model_consistency(self, model_name, model_class, fix_issues):
        """Check field consistency for a specific model"""
        total_records = model_class.objects.count()
        issues_found = 0
        issues_fixed = 0

        self.stdout.write(f'Total {model_name} records: {total_records}')

        # Worker-specific checks
        if model_name == 'Worker':
            issues_found, issues_fixed = self.check_worker_fields(model_class, fix_issues)

        # Employee-specific checks  
        elif model_name == 'Employee':
            issues_found, issues_fixed = self.check_employee_fields(model_class, fix_issues)

        elif model_name == 'VIP':
            issues_found, issues_fixed = self.check_vip_fields(model_class, fix_issues)

        # Summary
        if issues_found == 0:
            self.stdout.write(self.style.SUCCESS(f'✓ No field consistency issues found in {model_name} model'))
        else:
            if fix_issues:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Found {issues_found} issues in {model_name} model, fixed {issues_fixed}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Found {issues_found} field consistency issues in {model_name} model')
                )
                self.stdout.write(self.style.NOTICE('Use --fix to automatically resolve these issues'))

    def check_worker_fields(self, Worker, fix_issues):
        """Check Worker model field consistency"""
        issues_found = 0
        issues_fixed = 0

        # Check date of birth field synchronization
        mismatched_dob = Worker.objects.filter(
            dob__isnull=False, 
            date_of_birth__isnull=False
        ).exclude(dob=models.F('date_of_birth'))

        missing_dob = Worker.objects.filter(
            dob__isnull=True, 
            date_of_birth__isnull=False
        )

        missing_date_of_birth = Worker.objects.filter(
            dob__isnull=False, 
            date_of_birth__isnull=True
        )

        dob_issues = mismatched_dob.count() + missing_dob.count() + missing_date_of_birth.count()
        issues_found += dob_issues

        if dob_issues > 0:
            self.stdout.write(f'• Date of birth inconsistencies: {dob_issues}')
            self.stdout.write(f'  - Mismatched dob/date_of_birth: {mismatched_dob.count()}')
            self.stdout.write(f'  - Missing dob field: {missing_dob.count()}')
            self.stdout.write(f'  - Missing date_of_birth field: {missing_date_of_birth.count()}')

            if fix_issues:
                with transaction.atomic():
                    # Fix mismatched: use dob as source of truth
                    for worker in mismatched_dob:
                        worker.date_of_birth = worker.dob
                        worker.save(update_fields=['date_of_birth'])
                        issues_fixed += 1

                    # Fix missing dob: copy from date_of_birth
                    for worker in missing_dob:
                        worker.dob = worker.date_of_birth
                        worker.save(update_fields=['dob'])
                        issues_fixed += 1

                    # Fix missing date_of_birth: copy from dob
                    for worker in missing_date_of_birth:
                        worker.date_of_birth = worker.dob
                        worker.save(update_fields=['date_of_birth'])
                        issues_fixed += 1

        # Check name field synchronization
        empty_name_with_names = Worker.objects.filter(
            models.Q(name__isnull=True) | models.Q(name=''),
            first_name__isnull=False,
            last_name__isnull=False
        ).exclude(first_name='', last_name='')

        name_issues = empty_name_with_names.count()
        issues_found += name_issues

        if name_issues > 0:
            self.stdout.write(f'• Empty name field with available first/last names: {name_issues}')
            
            if fix_issues:
                with transaction.atomic():
                    for worker in empty_name_with_names:
                        worker.name = f"{worker.first_name} {worker.last_name}".strip()
                        worker.save(update_fields=['name'])
                        issues_fixed += 1

        return issues_found, issues_fixed

    def check_employee_fields(self, Employee, fix_issues):
        """Check Employee model field consistency"""
        issues_found = 0
        issues_fixed = 0

        # Employee model has good consistency - only one date_of_birth field
        # Check for any missing critical fields
        missing_email = Employee.objects.filter(
            models.Q(email__isnull=True) | models.Q(email='')
        ).count()

        if missing_email > 0:
            self.stdout.write(f'• Employees with missing email: {missing_email}')
            issues_found += missing_email
            # Note: We don't auto-fix missing emails as they need manual input

        # Check user relationship consistency
        orphaned_employees = Employee.objects.filter(user__isnull=True).count()
        if orphaned_employees > 0:
            self.stdout.write(f'• Employees without linked user accounts: {orphaned_employees}')
            issues_found += orphaned_employees

        return issues_found, issues_fixed

    def check_vip_fields(self, VIP, fix_issues):
        """Check VIP model field consistency"""
        issues_found = 0
        issues_fixed = 0

        # Check for nickname uniqueness issues
        duplicate_nicknames = VIP.objects.values('nickname').annotate(
            count=models.Count('nickname')
        ).filter(count__gt=1, nickname__isnull=False).exclude(nickname='')

        nickname_issues = sum(dup['count'] - 1 for dup in duplicate_nicknames)
        if nickname_issues > 0:
            self.stdout.write(f'• VIPs with duplicate nicknames: {nickname_issues}')
            issues_found += nickname_issues
            # Note: We don't auto-fix duplicate nicknames as they need manual resolution

        # Check for missing required fields
        missing_required = VIP.objects.filter(
            models.Q(first_name__isnull=True) | models.Q(first_name='') |
            models.Q(last_name__isnull=True) | models.Q(last_name='') |
            models.Q(nickname__isnull=True) | models.Q(nickname='')
        ).count()

        if missing_required > 0:
            self.stdout.write(f'• VIPs with missing required fields (name/nickname): {missing_required}')
            issues_found += missing_required

        return issues_found, issues_fixed 