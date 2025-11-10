"""
Fix NSSF and Tax configuration effective dates
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from payroll.models import NSSFConfiguration, TaxSlab
from datetime import date


class Command(BaseCommand):
    help = 'Fix NSSF and Tax configuration effective dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name',
            default='kk_company'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']

        self.stdout.write(self.style.SUCCESS('\n>> Fixing Configuration Dates'))
        self.stdout.write(f'Schema: {schema_name}\n')

        with schema_context(schema_name):
            # Update NSSF configs to start from 2025-01-01
            nssf_count = NSSFConfiguration.objects.filter(is_active=True).update(
                effective_from=date(2025, 1, 1)
            )
            self.stdout.write(f'[OK] Updated {nssf_count} NSSF configurations to effective_from=2025-01-01')

            # Update Tax Slabs to start from 2025-01-01
            tax_count = TaxSlab.objects.filter(is_active=True).update(
                effective_from=date(2025, 1, 1)
            )
            self.stdout.write(f'[OK] Updated {tax_count} Tax slabs to effective_from=2025-01-01')

            self.stdout.write(self.style.SUCCESS('\n[OK] Configuration dates fixed!'))
