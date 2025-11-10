from django.core.management.base import BaseCommand
from company.models import Company, Domain, Group
from django_tenants.utils import schema_context


class Command(BaseCommand):
    help = 'Set up public domain for localhost admin access'

    def handle(self, *args, **options):
        # Get the LYP group
        try:
            lyp_group = Group.objects.get(name='LYP')
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('LYP group not found. Please create it first.')
            )
            return

        # Create or get the public tenant (used for the public schema)
        public_tenant, created = Company.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'LYP Group Management',
                'group': lyp_group,
                'description': 'Public schema for LYP Group management',
                'company_type': 'corporation',
                'country': 'Malaysia'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created public tenant: {public_tenant.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Public tenant already exists: {public_tenant.name}')
            )

        # Create domain for localhost access
        domain, created = Domain.objects.get_or_create(
            domain='localhost',
            defaults={
                'tenant': public_tenant,
                'is_primary': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created domain mapping: localhost -> {public_tenant.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Domain mapping already exists: localhost -> {domain.tenant.name}')
            )

        self.stdout.write(
            self.style.SUCCESS('\n[OK] Public domain setup complete!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now access the admin at: http://localhost:8000/admin')
        ) 