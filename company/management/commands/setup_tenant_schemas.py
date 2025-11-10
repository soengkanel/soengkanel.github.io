from django.core.management.base import BaseCommand
from django.core.management import call_command
from company.models import Company, Domain
from django.db import connection


class Command(BaseCommand):
    help = 'Set up tenant schemas for all companies'

    def handle(self, *args, **options):
        self.stdout.write('Setting up tenant schemas...')
        
        companies = Company.objects.all()
        
        for company in companies:
            schema_name = company.schema_name
            self.stdout.write(f'\nProcessing company: {company.name} (schema: {schema_name})')
            
            # Check if schema exists
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                    [schema_name]
                )
                schema_exists = cursor.fetchone() is not None
            
            if not schema_exists:
                self.stdout.write(f'  Creating schema: {schema_name}')
                with connection.cursor() as cursor:
                    cursor.execute(f'CREATE SCHEMA "{schema_name}"')
            else:
                self.stdout.write(f'  Schema {schema_name} already exists')
            
            # Ensure domain exists
            domain_name = f'{schema_name}.localhost'
            domain, created = Domain.objects.get_or_create(
                domain=domain_name,
                tenant=company,
                defaults={'is_primary': True}
            )
            
            if created:
                self.stdout.write(f'  [OK] Created domain: {domain_name}')
            else:
                self.stdout.write(f'  [OK] Domain already exists: {domain_name}')
            
            # Try to migrate this specific tenant
            try:
                self.stdout.write(f'  Migrating schema: {schema_name}')
                call_command('migrate_schemas', '--schema', schema_name, verbosity=0)
                self.stdout.write(
                    self.style.SUCCESS(f'  [OK] Successfully migrated {schema_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [ERROR] Failed to migrate {schema_name}: {str(e)}')
                )
                # Continue with other schemas
                continue
        
        # Show final status
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TENANT SETUP SUMMARY:')
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"
            )
            all_schemas = [row[0] for row in cursor.fetchall()]
        
        self.stdout.write(f'Database schemas: {", ".join(all_schemas)}')
        
        domains = Domain.objects.all()
        self.stdout.write('Configured domains:')
        for domain in domains:
            self.stdout.write(f'  - {domain.domain} -> {domain.tenant.name} ({domain.tenant.schema_name})')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Tenant setup complete!')) 