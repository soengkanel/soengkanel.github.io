"""
Management command to load predefined services into the database.
Usage: python manage.py load_predefined_services
For specific tenant: python manage.py load_predefined_services --schema tenant_name
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from django.db import connection
from django_tenants.utils import schema_context, get_tenant_model


class Command(BaseCommand):
    help = 'Load predefined service charges into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Schema name to load services into. If not specified, loads into all tenant schemas.',
        )
        parser.add_argument(
            '--all-tenants',
            action='store_true',
            help='Load services into all tenant schemas',
        )

    def handle(self, *args, **options):
        from billing.models import Service
        
        schema_name = options.get('schema')
        all_tenants = options.get('all_tenants')
        
        if schema_name:
            # Load into specific schema
            self.load_services_for_schema(schema_name, Service)
        elif all_tenants:
            # Load into all tenant schemas
            TenantModel = get_tenant_model()
            for tenant in TenantModel.objects.all():
                self.stdout.write(self.style.SUCCESS(f'\nProcessing tenant: {tenant.schema_name}'))
                self.load_services_for_schema(tenant.schema_name, Service)
        else:
            # Try to get current schema
            current_schema = connection.schema_name
            if current_schema and current_schema != 'public':
                self.load_services_for_schema(current_schema, Service)
            else:
                self.stdout.write(self.style.ERROR(
                    'No schema specified. Use --schema <schema_name> or --all-tenants option.'
                ))
                self.stdout.write(self.style.WARNING(
                    'Example: python manage.py load_predefined_services --schema tenant1'
                ))
                return
    
    def load_services_for_schema(self, schema_name, Service):
        from django_tenants.utils import schema_context
        
        with schema_context(schema_name):
            # Define predefined services
            predefined_services = [
                {
                'service_code': 'SVC001',
                'name': 'Lost VIP ID Card Replacement',
                'category': 'id_cards',
                'default_price': Decimal('10.00'),
                'description': 'Replacement fee for lost VIP ID card',
                'is_active': True
            },
            {
                'service_code': 'SVC002',
                'name': 'Lost Worker ID Card Replacement',
                'category': 'id_cards',
                'default_price': Decimal('10.00'),
                'description': 'Replacement fee for lost Worker ID card',
                'is_active': True
            },
            {
                'service_code': 'SVC003',
                'name': 'VIP ID Card Printing',
                'category': 'id_cards',
                'default_price': Decimal('5.00'),
                'description': 'Printing fee for new VIP ID card',
                'is_active': True
            },
            {
                'service_code': 'SVC004',
                'name': 'Worker ID Card Printing',
                'category': 'id_cards',
                'default_price': Decimal('2.00'),
                'description': 'Printing fee for new Worker ID card',
                'is_active': True
            },
            {
                'service_code': 'SVC005',
                'name': '1 Month',
                'category': 'visas',
                'default_price': Decimal('55.00'),
                'description': '1 Month visa service fee',
                'is_active': True
            },
            {
                'service_code': 'SVC006',
                'name': '1 Year',
                'category': 'visas',
                'default_price': Decimal('300.00'),
                'description': '1 Year visa service fee',
                'is_active': True
            },
            {
                'service_code': 'SVC007',
                'name': '3 Months',
                'category': 'visas',
                'default_price': Decimal('85.00'),
                'description': '3 Months visa service fee',
                'is_active': True
            },
            {
                'service_code': 'SVC008',
                'name': '6 Months',
                'category': 'visas',
                'default_price': Decimal('165.00'),
                'description': '6 Months visa service fee',
                'is_active': True
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Loading Predefined Services'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        for service_data in predefined_services:
            service_code = service_data['service_code']
            
            try:
                # Check if service already exists
                service, created = Service.objects.update_or_create(
                    service_code=service_code,
                    defaults={
                        'name': service_data['name'],
                        'category': service_data['category'],
                        'default_price': service_data['default_price'],
                        'description': service_data['description'],
                        'is_active': service_data['is_active']
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[+] Created: {service_code} - {service_data["name"]} (${service_data["default_price"]})')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'[*] Updated: {service_code} - {service_data["name"]} (${service_data["default_price"]})')
                    )

            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[!] Error with {service_code}: {str(e)}')
                )

        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} services'))
        self.stdout.write(self.style.WARNING(f'Updated: {updated_count} services'))
        if skipped_count > 0:
            self.stdout.write(self.style.ERROR(f'Skipped: {skipped_count} services'))
        self.stdout.write(self.style.SUCCESS(f'Total processed: {created_count + updated_count}/{len(predefined_services)}'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        # Display all active services
        self.stdout.write(self.style.SUCCESS('\nActive Services in Database:'))
        self.stdout.write(self.style.SUCCESS('-'*60))
        
        active_services = Service.objects.filter(is_active=True).order_by('service_code')
        
        if active_services.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f'{"Code":<10} {"Name":<35} {"Category":<15} {"Price":<10}'
                )
            )
            self.stdout.write(self.style.SUCCESS('-'*60))
            
            for service in active_services:
                category_display = dict(Service.CATEGORY_CHOICES).get(service.category, service.category)
                self.stdout.write(
                    f'{service.service_code:<10} {service.name[:35]:<35} {category_display:<15} ${service.default_price:<10.2f}'
                )
        else:
            self.stdout.write(self.style.WARNING('No active services found.'))

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Predefined services loaded successfully!'))