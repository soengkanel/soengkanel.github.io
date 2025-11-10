"""
Management command to initialize or update payroll settings
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context
from payroll.models import PayrollSettings


class Command(BaseCommand):
    help = 'Initialize or update payroll settings including currency configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name (e.g., kk_company)',
            default='kk_company'
        )
        parser.add_argument(
            '--currency',
            type=str,
            choices=['USD', 'KHR', 'EUR', 'GBP', 'JPY', 'CNY', 'THB', 'VND'],
            help='Currency code to set',
            default='USD'
        )
        parser.add_argument(
            '--symbol',
            type=str,
            help='Currency symbol (e.g., $, ៛)',
            default=None
        )
        parser.add_argument(
            '--position',
            type=str,
            choices=['before', 'after'],
            help='Currency symbol position',
            default='before'
        )
        parser.add_argument(
            '--decimals',
            type=int,
            choices=[0, 2],
            help='Number of decimal places',
            default=2
        )

    def handle(self, *args, **options):
        schema_name = options['schema']
        currency = options['currency']
        position = options['position']
        decimals = options['decimals']

        # Currency symbols mapping
        currency_symbols = {
            'USD': '$',
            'KHR': '៛',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CNY': '¥',
            'THB': '฿',
            'VND': '₫',
        }

        symbol = options['symbol'] if options['symbol'] else currency_symbols.get(currency, '$')

        self.stdout.write(self.style.SUCCESS(f'\n>> Initializing Payroll Settings for schema: {schema_name}'))

        try:
            with schema_context(schema_name):
                # Get or create settings
                settings, created = PayrollSettings.objects.get_or_create(pk=1)

                if created:
                    self.stdout.write(self.style.SUCCESS('[+] Created new PayrollSettings'))
                else:
                    self.stdout.write(self.style.WARNING('[!] PayrollSettings already exists, updating...'))

                # Update settings
                settings.base_currency = currency
                settings.currency_symbol = symbol
                settings.currency_position = position
                settings.decimal_places = decimals
                settings.use_thousand_separator = True
                settings.save()

                self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Payroll Settings configured:'))
                self.stdout.write(f'  * Currency: {settings.base_currency}')
                try:
                    self.stdout.write(f'  * Symbol: {settings.currency_symbol}')
                except UnicodeEncodeError:
                    self.stdout.write(f'  * Symbol: [Unicode symbol - {settings.base_currency}]')
                self.stdout.write(f'  * Position: {settings.currency_position}')
                self.stdout.write(f'  * Decimal Places: {settings.decimal_places}')
                self.stdout.write(f'  * Thousand Separator: {settings.use_thousand_separator}')

                # Show example formatting
                self.stdout.write(self.style.SUCCESS('\n[+] Example formatting:'))
                test_amount = 1234567.89
                try:
                    formatted = settings.format_currency(test_amount)
                    self.stdout.write(f'  * {test_amount} => {formatted}')
                except UnicodeEncodeError:
                    formatted_no_symbol = f"{test_amount:,.{settings.decimal_places}f}"
                    self.stdout.write(f'  * {test_amount} => {settings.base_currency} {formatted_no_symbol}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] Failed to initialize settings: {str(e)}'))
            raise
