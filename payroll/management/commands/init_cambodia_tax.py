from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from decimal import Decimal
from payroll.models import TaxSlab, NSSFConfiguration, SalaryComponent


class Command(BaseCommand):
    help = 'Initialize Cambodia tax slabs and NSSF configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing Cambodia tax configuration...'))

        # Create tax slabs based on Cambodia's progressive tax system 2024
        tax_slabs_data = [
            {
                'min_amount': Decimal('0'),
                'max_amount': Decimal('1500000'),
                'tax_rate': Decimal('0'),
                'fixed_tax': Decimal('0'),
            },
            {
                'min_amount': Decimal('1500000'),
                'max_amount': Decimal('2000000'),
                'tax_rate': Decimal('5'),
                'fixed_tax': Decimal('0'),
            },
            {
                'min_amount': Decimal('2000000'),
                'max_amount': Decimal('8500000'),
                'tax_rate': Decimal('10'),
                'fixed_tax': Decimal('25000'),
            },
            {
                'min_amount': Decimal('8500000'),
                'max_amount': Decimal('12500000'),
                'tax_rate': Decimal('15'),
                'fixed_tax': Decimal('675000'),
            },
            {
                'min_amount': Decimal('12500000'),
                'max_amount': None,
                'tax_rate': Decimal('20'),
                'fixed_tax': Decimal('1275000'),
            },
        ]

        self.stdout.write('Creating tax slabs...')
        for slab_data in tax_slabs_data:
            tax_slab, created = TaxSlab.objects.get_or_create(
                min_amount=slab_data['min_amount'],
                max_amount=slab_data['max_amount'],
                defaults={
                    'tax_rate': slab_data['tax_rate'],
                    'fixed_tax': slab_data['fixed_tax'],
                    'effective_from': date.today(),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created: {tax_slab}')
            else:
                self.stdout.write(f'  Exists: {tax_slab}')

        # Create NSSF configurations for Cambodia
        nssf_configs = [
            {
                'contribution_type': 'OCCUPATIONAL_RISK',
                'employee_rate': Decimal('0.8'),
                'employer_rate': Decimal('0.8'),
                'max_salary_cap': Decimal('3000000'),
            },
            {
                'contribution_type': 'HEALTH_CARE',
                'employee_rate': Decimal('2.6'),
                'employer_rate': Decimal('2.6'),
                'max_salary_cap': Decimal('3000000'),
            },
        ]

        self.stdout.write('Creating NSSF configurations...')
        for config_data in nssf_configs:
            nssf_config, created = NSSFConfiguration.objects.get_or_create(
                contribution_type=config_data['contribution_type'],
                defaults={
                    'employee_rate': config_data['employee_rate'],
                    'employer_rate': config_data['employer_rate'],
                    'max_salary_cap': config_data['max_salary_cap'],
                    'effective_from': date.today(),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created: {nssf_config}')
            else:
                self.stdout.write(f'  Exists: {nssf_config}')

        # Create common salary components
        salary_components = [
            {
                'code': 'BASIC',
                'name': 'Basic Salary',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 1,
            },
            {
                'code': 'HOUSE',
                'name': 'Housing Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 2,
            },
            {
                'code': 'TRANSPORT',
                'name': 'Transport Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 3,
            },
            {
                'code': 'MEAL',
                'name': 'Meal Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 4,
            },
            {
                'code': 'PHONE',
                'name': 'Phone Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 5,
            },
            {
                'code': 'SENIORITY',
                'name': 'Seniority Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 6,
            },
            {
                'code': 'OVERTIME',
                'name': 'Overtime Pay',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 7,
            },
            {
                'code': 'BONUS',
                'name': 'Bonus',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_tax_applicable': True,
                'display_order': 8,
            },
            {
                'code': 'TAX',
                'name': 'Salary Tax',
                'component_type': 'DEDUCTION',
                'calculation_type': 'FORMULA',
                'is_tax_applicable': False,
                'display_order': 21,
            },
            {
                'code': 'NSSF_EMP',
                'name': 'NSSF (Employee)',
                'component_type': 'DEDUCTION',
                'calculation_type': 'FORMULA',
                'is_tax_applicable': False,
                'display_order': 22,
            },
            {
                'code': 'ADVANCE',
                'name': 'Salary Advance',
                'component_type': 'DEDUCTION',
                'calculation_type': 'FIXED',
                'is_tax_applicable': False,
                'display_order': 23,
            },
            {
                'code': 'LOAN',
                'name': 'Loan Deduction',
                'component_type': 'DEDUCTION',
                'calculation_type': 'FIXED',
                'is_tax_applicable': False,
                'display_order': 24,
            },
        ]

        self.stdout.write('Creating salary components...')
        for component_data in salary_components:
            component, created = SalaryComponent.objects.get_or_create(
                code=component_data['code'],
                defaults=component_data
            )
            if created:
                self.stdout.write(f'  Created: {component}')
            else:
                self.stdout.write(f'  Exists: {component}')

        self.stdout.write(self.style.SUCCESS('Cambodia tax configuration initialized successfully!'))