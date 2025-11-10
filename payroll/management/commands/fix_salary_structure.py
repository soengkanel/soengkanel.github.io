"""
Fix salary structure to properly calculate earnings and deductions
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from payroll.models import SalaryStructure, SalaryDetail, SalaryComponent
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fix salary structure to ensure proper calculation of earnings and deductions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name',
            default='kk_company'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']

        self.stdout.write(self.style.SUCCESS('\n>> Fixing Salary Structure'))
        self.stdout.write(f'Schema: {schema_name}\n')

        with schema_context(schema_name):
            # Get the standard structure
            structure = SalaryStructure.objects.get(name='Cambodia Standard Salary Structure')

            self.stdout.write(f'Structure: {structure.name}\n')

            # Update BASIC salary component - should use base_salary
            basic_comp = SalaryComponent.objects.get(code='BASIC')
            basic_detail, created = SalaryDetail.objects.get_or_create(
                salary_structure=structure,
                salary_component=basic_comp
            )
            basic_detail.amount = Decimal('0')
            basic_detail.formula = 'base'  # Use base salary
            basic_detail.save()
            self.stdout.write(f'[OK] Fixed BASIC component: formula={basic_detail.formula}')

            # Update HRA (Housing Allowance) - 15% of base
            hra_comp = SalaryComponent.objects.get(code='HRA')
            hra_comp.calculation_type = 'FORMULA'
            hra_comp.formula = 'base * Decimal("0.15")'
            hra_comp.save()

            hra_detail, created = SalaryDetail.objects.get_or_create(
                salary_structure=structure,
                salary_component=hra_comp
            )
            hra_detail.amount = Decimal('0')
            hra_detail.formula = 'base * Decimal("0.15")'
            hra_detail.save()
            self.stdout.write(f'[OK] Fixed HRA component: formula={hra_detail.formula}')

            # Update NSSF formula to use correct variable name
            nssf_comp = SalaryComponent.objects.get(code='NSSF_EMPLOYEE')
            nssf_comp.formula = 'min(gross * Decimal("0.035"), Decimal("9100"))'  # Max NSSF is 260,000 * 0.035 = 9,100
            nssf_comp.save()

            nssf_detail = SalaryDetail.objects.get(
                salary_structure=structure,
                salary_component=nssf_comp
            )
            nssf_detail.formula = ''  # Use component formula
            nssf_detail.save()
            self.stdout.write(f'[OK] Fixed NSSF component: formula={nssf_comp.formula}')

            # Add tax calculation formula
            tax_comp = SalaryComponent.objects.get(code='TAX')
            # Simple progressive tax for now - will be calculated by model method
            tax_comp.formula = ''  # Let the model calculate progressive tax
            tax_comp.save()

            tax_detail = SalaryDetail.objects.get(
                salary_structure=structure,
                salary_component=tax_comp
            )
            tax_detail.formula = ''
            tax_detail.save()
            self.stdout.write(f'[OK] Fixed TAX component')

            self.stdout.write(self.style.SUCCESS('\n[OK] Salary structure fixed!'))
            self.stdout.write('\nComponent summary:')
            for detail in structure.salary_details.all():
                formula = detail.formula or detail.salary_component.formula or '(fixed amount)'
                self.stdout.write(
                    f'  - {detail.salary_component.name}: '
                    f'type={detail.salary_component.calculation_type}, '
                    f'formula={formula}'
                )
