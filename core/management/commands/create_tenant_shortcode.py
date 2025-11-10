from django.core.management.base import BaseCommand
from django.db import connection
from company.models import Company, Domain


class Command(BaseCommand):
    help = 'Create or update tenant with shortcode for parameter-based access'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            type=str,
            help='Full name of the tenant/company'
        )
        parser.add_argument(
            'shortcode',
            type=str,
            help='Short code for URL parameter (e.g., kk, osm)'
        )
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Domain for the tenant (default: localhost)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing tenant if it exists'
        )

    def handle(self, *args, **options):
        name = options['name']
        shortcode = options['shortcode'].lower()
        domain = options['domain']
        update = options['update']

        # Check if company exists
        try:
            company = Company.objects.get(schema_name=shortcode)
            if update:
                self.stdout.write(self.style.WARNING(f'Updating existing tenant: {company.name}'))
                company.name = name
                company.save()
            else:
                self.stdout.write(self.style.WARNING(f'Tenant with schema_name {shortcode} already exists'))
                return
        except Company.DoesNotExist:
            # Create new company
            company = Company(
                name=name,
                schema_name=shortcode,
            )
            # Set required fields with defaults
            if not hasattr(company, 'group_id'):
                # Check if group field is required
                from company.models import Group
                default_group = Group.objects.first()
                if default_group:
                    company.group = default_group
                else:
                    # Create a default group if none exists
                    default_group = Group.objects.create(
                        name='Default Group',
                        description='Default group for tenants'
                    )
                    company.group = default_group
            
            company.save()
            self.stdout.write(self.style.SUCCESS(f'Created new tenant: {name} with schema: {shortcode}'))

        # Create or update domain
        domain_obj, created = Domain.objects.get_or_create(
            domain=f'{shortcode}.{domain}',
            defaults={'tenant': company, 'is_primary': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created domain: {shortcode}.{domain}'))
        else:
            self.stdout.write(self.style.WARNING(f'Domain already exists: {shortcode}.{domain}'))

        # Also create a localhost domain for testing
        if domain != 'localhost':
            local_domain, created = Domain.objects.get_or_create(
                domain=f'{shortcode}.localhost',
                defaults={'tenant': company, 'is_primary': False}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created local domain: {shortcode}.localhost'))

        self.stdout.write(self.style.SUCCESS(f'\nTenant setup complete!'))
        self.stdout.write(self.style.SUCCESS(f'Access via domain: http://{shortcode}.{domain}/'))
        self.stdout.write(self.style.SUCCESS(f'Access via parameter: http://{domain}/?tenant={shortcode}'))
        
        # Show how to migrate the schema
        self.stdout.write(self.style.WARNING(f'\nDon\'t forget to migrate the tenant schema:'))
        self.stdout.write(f'python manage.py migrate_schemas --tenant {shortcode}')