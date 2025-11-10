from django.core.management.base import BaseCommand
from django.conf import settings
from billing.models import Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create default card services for billing integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing services with new prices',
        )

    def handle(self, *args, **options):
        update_existing = options['update_existing']

        # Default card services with prices from settings
        services = [
            {
                'name': 'Worker ID Card Reprint',
                'category': 'id_cards',
                'description': 'Service charge for reprinting worker ID card (second print and onwards)',
                'default_price': Decimal(getattr(settings, 'CARD_REPRINT_CHARGE', '5.00')),
            },
            {
                'name': 'Lost Worker ID Card Replacement',
                'category': 'id_cards',
                'description': 'Service charge for replacing lost worker ID card',
                'default_price': Decimal(getattr(settings, 'CARD_LOST_REPLACEMENT_CHARGE', '10.00')),
            },
            {
                'name': 'Damaged Worker ID Card Replacement',
                'category': 'id_cards',
                'description': 'Service charge for replacing damaged worker ID card',
                'default_price': Decimal(getattr(settings, 'CARD_DAMAGED_REPLACEMENT_CHARGE', '5.00')),
            },
            {
                'name': 'Worker ID Card Service',
                'category': 'id_cards',
                'description': 'General worker ID card service charge',
                'default_price': Decimal('5.00'),
            },
        ]

        created_count = 0
        updated_count = 0

        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                category=service_data['category'],
                defaults=service_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created service: {service.name} - ${service.default_price}'
                    )
                )
            elif update_existing:
                # Update the price if different
                if service.default_price != service_data['default_price']:
                    old_price = service.default_price
                    service.default_price = service_data['default_price']
                    service.description = service_data['description']
                    service.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Updated service: {service.name} - '
                            f'${old_price} → ${service.default_price}'
                        )
                    )
                else:
                    self.stdout.write(
                        f'Service already exists: {service.name} - ${service.default_price}'
                    )
            else:
                self.stdout.write(
                    f'Service already exists: {service.name} - ${service.default_price}'
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Services created: {created_count}')
        if update_existing:
            self.stdout.write(f'Services updated: {updated_count}')
        
        # Show all card services
        self.stdout.write('\nAll card services:')
        card_services = Service.objects.filter(category='id_cards', is_active=True)
        for service in card_services:
            self.stdout.write(f'  - {service.name}: ${service.default_price}')

        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nCard services are now ready for billing integration!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nAll card services are already set up.'
                )
            ) 