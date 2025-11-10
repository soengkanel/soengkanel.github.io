from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cards.models import CardCharge


class Command(BaseCommand):
    help = 'Create invoices for card charges that do not have invoices yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating invoices',
        )
        parser.add_argument(
            '--charge-types',
            nargs='+',
            choices=['reprint', 'lost', 'damaged', 'other'],
            help='Only create invoices for specific charge types',
        )
        parser.add_argument(
            '--min-amount',
            type=float,
            default=0.01,
            help='Minimum charge amount to create invoice (default: 0.01)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        charge_types = options['charge_types']
        min_amount = options['min_amount']

        # Get charges without invoices
        charges_query = CardCharge.objects.filter(
            invoice__isnull=True,
            amount__gte=min_amount
        ).select_related('worker', 'card', 'created_by')

        if charge_types:
            charges_query = charges_query.filter(charge_type__in=charge_types)

        charges = charges_query.order_by('created_at')

        if not charges.exists():
            self.stdout.write(
                self.style.SUCCESS('No charges found that need invoices.')
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f'Found {charges.count()} charges without invoices:'
            )
        )

        created_count = 0
        error_count = 0

        for charge in charges:
            try:
                if dry_run:
                    self.stdout.write(
                        f'  Would create invoice for: {charge.worker} - '
                        f'{charge.get_charge_type_display()} - ${charge.amount}'
                    )
                else:
                    # Create the invoice
                    invoice = charge.create_invoice()
                    created_count += 1
                    self.stdout.write(
                        f'  Created invoice {invoice.invoice_number} for: '
                        f'{charge.worker} - {charge.get_charge_type_display()} - ${charge.amount}'
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  Error creating invoice for {charge.worker} '
                        f'(Charge ID: {charge.id}): {str(e)}'
                    )
                )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDry run complete. Would create {charges.count()} invoices.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nInvoice creation complete. '
                    f'Created: {created_count}, Errors: {error_count}'
                )
            )

        # Show summary of services that will be created/were created
        if not dry_run and created_count > 0:
            self.stdout.write('\nServices created/used:')
            from billing.models import Service
            services = Service.objects.filter(category='id_cards')
            for service in services:
                self.stdout.write(f'  - {service.name}: ${service.default_price}') 