"""
Recalculate all salary slips to fix missing deductions
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from payroll.models import SalarySlip


class Command(BaseCommand):
    help = 'Recalculate all salary slips to ensure deductions are properly calculated'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name',
            default='kk_company'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']

        self.stdout.write(self.style.SUCCESS('\n>> Recalculating Salary Slips'))
        self.stdout.write(f'Schema: {schema_name}\n')

        with schema_context(schema_name):
            slips = SalarySlip.objects.all()
            total = slips.count()

            self.stdout.write(f'Found {total} salary slips to recalculate\n')

            for i, slip in enumerate(slips, 1):
                try:
                    old_gross = slip.gross_pay
                    old_deduction = slip.total_deduction
                    old_net = slip.net_pay

                    # Recalculate from salary structure
                    slip.calculate_from_salary_structure()

                    self.stdout.write(
                        f'[{i}/{total}] Slip #{slip.id} - {slip.employee.full_name}: '
                        f'Gross: {old_gross:,.0f} -> {slip.gross_pay:,.0f}, '
                        f'Deduction: {old_deduction:,.0f} -> {slip.total_deduction:,.0f}, '
                        f'Net: {old_net:,.0f} -> {slip.net_pay:,.0f}'
                    )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'[{i}/{total}] ERROR on Slip #{slip.id}: {str(e)}'
                    ))

            self.stdout.write(self.style.SUCCESS(f'\n[OK] Recalculated {total} salary slips'))
