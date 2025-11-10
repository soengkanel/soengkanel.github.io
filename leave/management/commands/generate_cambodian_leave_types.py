"""
Management command to generate leave types based on Cambodian Labor Law
Reference: Cambodia Labor Law 1997 (amended)

Usage:
    python manage.py generate_cambodian_leave_types
    python manage.py generate_cambodian_leave_types --force  # Override existing types
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from leave.models import LeaveType


class Command(BaseCommand):
    help = 'Generate leave types based on Cambodian Labor Law'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing leave types',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creating leave types that already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        skip_existing = options.get('skip_existing', False)

        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('Cambodian Labor Law - Leave Types Generator'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')

        # Define Cambodian leave types based on labor law
        cambodian_leave_types = [
            {
                'name': 'Annual Leave',
                'code': 'ANNUAL',
                'max_days_per_year': 18,
                'carry_forward_allowed': True,
                'max_carry_forward_days': 6,
                'encashment_allowed': True,
                'include_holiday': False,
                'is_paid': True,
                'apply_in_advance_days': 3,
                'maximum_continuous_days': 18,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#28a745',
                'is_active': True,
                'description': 'Annual paid leave: 18 working days per year after 1 year of service (Cambodia Labor Law Article 166)'
            },
            {
                'name': 'Sick Leave',
                'code': 'SICK',
                'max_days_per_year': 365,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': True,
                'is_paid': True,
                'apply_in_advance_days': 0,
                'maximum_continuous_days': 365,
                'minimum_continuous_days': 1,
                'medical_certificate_required': True,
                'medical_certificate_min_days': 3,
                'color': '#dc3545',
                'is_active': True,
                'description': 'Sick leave with medical certificate. First 6 months at full pay, next 6 months at 60% (Article 168)'
            },
            {
                'name': 'Maternity Leave',
                'code': 'MATERNITY',
                'max_days_per_year': 90,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': True,
                'is_paid': True,
                'apply_in_advance_days': 7,
                'maximum_continuous_days': 90,
                'minimum_continuous_days': 90,
                'medical_certificate_required': True,
                'medical_certificate_min_days': 1,
                'color': '#e83e8c',
                'is_active': True,
                'description': 'Maternity leave: 90 days paid leave (50% by employer, 50% by NSSF) - Article 182'
            },
            {
                'name': 'Paternity Leave',
                'code': 'PATERNITY',
                'max_days_per_year': 2,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': False,
                'is_paid': True,
                'apply_in_advance_days': 3,
                'maximum_continuous_days': 2,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#17a2b8',
                'is_active': True,
                'description': 'Paternity leave: 2 days paid leave for birth of child'
            },
            {
                'name': 'Marriage Leave',
                'code': 'MARRIAGE',
                'max_days_per_year': 3,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': False,
                'is_paid': True,
                'apply_in_advance_days': 7,
                'maximum_continuous_days': 3,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#fd7e14',
                'is_active': True,
                'description': 'Special leave for employee marriage: 3 days paid leave'
            },
            {
                'name': 'Bereavement Leave',
                'code': 'BEREAVEMENT',
                'max_days_per_year': 7,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': False,
                'is_paid': True,
                'apply_in_advance_days': 0,
                'maximum_continuous_days': 7,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#6c757d',
                'is_active': True,
                'description': 'Bereavement leave for death of immediate family member: up to 7 days'
            },
            {
                'name': 'Special Circumstances Leave',
                'code': 'SPECIAL',
                'max_days_per_year': 7,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': False,
                'is_paid': True,
                'apply_in_advance_days': 1,
                'maximum_continuous_days': 7,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#6610f2',
                'is_active': True,
                'description': 'Special circumstances leave (religious ceremonies, family events, etc.)'
            },
            {
                'name': 'Unpaid Leave',
                'code': 'UNPAID',
                'max_days_per_year': 365,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': True,
                'is_paid': False,
                'apply_in_advance_days': 7,
                'maximum_continuous_days': 365,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#adb5bd',
                'is_active': True,
                'description': 'Unpaid leave by mutual agreement between employer and employee'
            },
            {
                'name': 'Compensatory Leave',
                'code': 'COMP',
                'max_days_per_year': 52,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': False,
                'is_paid': True,
                'apply_in_advance_days': 1,
                'maximum_continuous_days': 5,
                'minimum_continuous_days': 0.5,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#20c997',
                'is_active': True,
                'description': 'Compensatory time off for overtime work or work on rest days/holidays'
            },
            {
                'name': 'Study Leave',
                'code': 'STUDY',
                'max_days_per_year': 30,
                'carry_forward_allowed': False,
                'max_carry_forward_days': 0,
                'encashment_allowed': False,
                'include_holiday': False,
                'is_paid': False,
                'apply_in_advance_days': 14,
                'maximum_continuous_days': 30,
                'minimum_continuous_days': 1,
                'medical_certificate_required': False,
                'medical_certificate_min_days': 0,
                'color': '#ffc107',
                'is_active': True,
                'description': 'Leave for educational purposes or professional development'
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        try:
            with transaction.atomic():
                for leave_data in cambodian_leave_types:
                    code = leave_data['code']
                    name = leave_data['name']
                    description = leave_data.pop('description', '')

                    try:
                        # Check if leave type exists
                        existing = LeaveType.objects.filter(code=code).first()

                        if existing:
                            if skip_existing:
                                self.stdout.write(
                                    self.style.WARNING(f'[SKIP] {name} ({code}) - already exists')
                                )
                                skipped_count += 1
                                continue
                            elif force:
                                # Update existing
                                for key, value in leave_data.items():
                                    setattr(existing, key, value)
                                existing.save()
                                self.stdout.write(
                                    self.style.SUCCESS(f'[OK] Updated: {name} ({code})')
                                )
                                updated_count += 1
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'[SKIP] {name} ({code}) - already exists (use --force to update)'
                                    )
                                )
                                skipped_count += 1
                        else:
                            # Create new leave type
                            LeaveType.objects.create(**leave_data)
                            self.stdout.write(
                                self.style.SUCCESS(f'[OK] Created: {name} ({code})')
                            )
                            created_count += 1

                        if description:
                            self.stdout.write(f'     {description}')

                    except Exception as e:
                        error_msg = f'[ERROR] {name} ({code}): {str(e)}'
                        self.stdout.write(self.style.ERROR(error_msg))
                        errors.append(error_msg)

        except Exception as e:
            raise CommandError(f'Failed to generate leave types: {str(e)}')

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('Summary'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))
        if errors:
            self.stdout.write(self.style.ERROR(f'Errors: {len(errors)}'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        self.stdout.write('')

        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '[SUCCESS] Leave types generated successfully based on Cambodian Labor Law!'
                )
            )
            self.stdout.write('')
            self.stdout.write('Next steps:')
            self.stdout.write('  1. Review leave types at: http://localhost:8000/leave/types/')
            self.stdout.write('  2. Adjust max days or settings as needed for your organization')
            self.stdout.write('  3. Create leave allocations for employees')
        else:
            self.stdout.write(
                self.style.WARNING(
                    '[WARNING] No changes made. Use --force to update existing leave types.'
                )
            )

        self.stdout.write('')
