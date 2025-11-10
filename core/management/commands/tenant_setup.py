from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from company.models import Company, Domain, Group
import getpass


class Command(BaseCommand):
    help = 'Complete tenant setup - creates groups, tenants, domains, and admin users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Skip creating admin users'
        )
        parser.add_argument(
            '--company-name',
            type=str,
            default='KK Company',
            help='Name for the demo company tenant (default: KK Company)'
        )
        parser.add_argument(
            '--company-domain',
            type=str,
            default='kk.lyp',
            help='Domain for the demo company (default: kk.lyp)'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@localhost',
            help='Admin email (default: admin@localhost)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Complete Tenant Setup'))
        self.stdout.write('=' * 60)

        try:
            with transaction.atomic():
                # Step 1: Create LYP Group
                self.create_lyp_group()
                
                # Step 2: Setup public tenant and domain
                self.setup_public_tenant()
                
                # Step 3: Create demo company tenant
                self.create_demo_company(
                    options['company_name'],
                    options['company_domain']
                )
                
                # Step 4: Create admin users (if not skipped)
                if not options['skip_admin']:
                    self.create_admin_users(
                        options['company_name'],
                        options['admin_username'],
                        options['admin_email']
                    )
                
                # Step 5: Show final status
                self.show_final_status()
                
        except Exception as e:

                
            pass
            self.stdout.write(
                self.style.ERROR(f'ERROR: Setup failed: {str(e)}')
            )
            raise CommandError(f'Tenant setup failed: {str(e)}')

    def create_lyp_group(self):
        """Create the LYP group if it doesn't exist"""
        self.stdout.write('\nStep 1: Creating LYP Group...')
        
        group, created = Group.objects.get_or_create(
            name='LYP',
            defaults={
                'description': 'LYP Group - Main organizational group',
                'is_active': True,
                'headquarters': 'Main Office'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('  SUCCESS: Created LYP Group')
            )
        else:
            self.stdout.write(
                self.style.WARNING('  WARNING: LYP Group already exists')
            )

    def setup_public_tenant(self):
        """Setup public tenant and localhost domain"""
        self.stdout.write('\nStep 2: Setting up Public Tenant...')
        
        # Get the LYP group
        group = Group.objects.get(name='LYP')
        
        # Create public tenant
        public_tenant, created = Company.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'LYP Group Management',
                'group': group,
                'company_type': 'public',
                'description': 'Public tenant for main administration',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('  SUCCESS: Created public tenant')
            )
        else:
            self.stdout.write(
                self.style.WARNING('  WARNING: Public tenant already exists')
            )
        
        # Create localhost domain
        domain, created = Domain.objects.get_or_create(
            domain='localhost',
            defaults={
                'tenant': public_tenant,
                'is_primary': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('  SUCCESS: Created localhost domain mapping')
            )
        else:
            self.stdout.write(
                self.style.WARNING('  WARNING: localhost domain already exists')
            )

    def create_demo_company(self, company_name, company_domain):
        """Create demo company tenant and domain"""
        self.stdout.write(f'\nStep 3: Creating {company_name} Tenant...')
        
        # Get the LYP group
        group = Group.objects.get(name='LYP')
        
        # Generate schema name from company name
        schema_name = company_name.lower().replace(' ', '_').replace('-', '_')
        
        # Create company tenant
        company, created = Company.objects.get_or_create(
            schema_name=schema_name,
            defaults={
                'name': company_name,
                'group': group,
                'company_type': 'private',
                'description': f'{company_name} - Demo tenant for development',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'  SUCCESS: Created {company_name} tenant')
            )
            self.stdout.write(f'    Schema: {schema_name}')
        else:
            self.stdout.write(
                self.style.WARNING(f'  WARNING: {company_name} tenant already exists')
            )
        
        # Create domain mapping
        domain, created = Domain.objects.get_or_create(
            domain=company_domain,
            defaults={
                'tenant': company,
                'is_primary': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'  SUCCESS: Created domain: {company_domain}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'  WARNING: Domain {company_domain} already exists')
            )

    def create_admin_users(self, company_name, admin_username, admin_email):
        """Create admin users for both public and company tenants"""
        self.stdout.write('\nStep 4: Creating Admin Users...')
        
        # Use default password for admin users in Docker environment
        password = 'admin123'  # Default password for Docker setup
        self.stdout.write(f'Using default password for admin users: {password}')
        
        # Create admin for public tenant
        self.create_tenant_admin('public', 'Public Admin', admin_username, admin_email, password)
        
        # Create admin for company tenant
        company = Company.objects.get(name=company_name)
        self.create_tenant_admin(
            company.schema_name, 
            company_name, 
            admin_username, 
            admin_email, 
            password
        )

    def create_tenant_admin(self, schema_name, tenant_name, username, email, password):
        """Create admin user for a specific tenant"""
        with schema_context(schema_name):
            try:
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'  WARNING: Admin user already exists in {tenant_name}')
                    )
                    return
                
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'  SUCCESS: Created admin user in {tenant_name}')
                )
                self.stdout.write(f'    Username: {username}')
                self.stdout.write(f'    Email: {email}')
                
            except Exception as e:

                
                pass
                self.stdout.write(
                    self.style.ERROR(f'  ERROR: Failed to create admin in {tenant_name}: {str(e)}')
                )

    def show_final_status(self):
        """Show final setup status and instructions"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('TENANT SETUP COMPLETE!'))
        self.stdout.write('=' * 60)
        
        # Show all configured domains
        self.stdout.write('\nConfigured Domains:')
        domains = Domain.objects.all().select_related('tenant')
        for domain in domains:
            self.stdout.write(
                f'  - {domain.domain} -> {domain.tenant.name} ({domain.tenant.schema_name})'
            )
        
        # Show access instructions
        self.stdout.write('\nAccess URLs:')
        for domain in domains:
            if domain.tenant.schema_name == 'public':
                self.stdout.write(f'  - Main Admin: http://{domain.domain}:8000/admin')
            else:
                self.stdout.write(f'  - {domain.tenant.name}: http://{domain.domain}:8000')
        
        # Show next steps
        self.stdout.write('\nNext Steps:')
        self.stdout.write('  1. Start your development server: python manage.py runserver')
        self.stdout.write('  2. Add domain entries to your hosts file if needed:')
        self.stdout.write('     127.0.0.1 localhost')
        for domain in domains:
            if domain.domain != 'localhost':
                self.stdout.write(f'     127.0.0.1 {domain.domain}')
        self.stdout.write('  3. Access the admin interfaces using the URLs above')
        
        # Show additional commands
        self.stdout.write('\nUseful Commands:')
        self.stdout.write('  - Generate master data: python manage.py generate_master_data')
        self.stdout.write('  - Create tenant user: python manage.py create_tenant_user --company "Company Name"')
        self.stdout.write('  - Setup tenant schemas: python manage.py setup_tenant_schemas')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Your multi-tenant app is ready to use!'))