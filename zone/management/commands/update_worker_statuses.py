from django.core.management.base import BaseCommand
from django.db import transaction
from zone.models import Worker
from django_tenants.utils import tenant_context
from company.models import Company


class Command(BaseCommand):
    help = 'Update worker statuses to demonstrate unified status system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Specify tenant schema (kk, osm, or all)',
            default='all'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        tenant_filter = options['tenant']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Get tenants to process
        if tenant_filter == 'all':
            tenants = Company.objects.all()
        else:
            tenants = Company.objects.filter(schema_name=tenant_filter)
        
        if not tenants.exists():
            self.stdout.write(self.style.ERROR(f'No tenants found for: {tenant_filter}'))
            return
        
        for tenant in tenants:
            self.stdout.write(f'\n=== Processing Tenant: {tenant.name} ({tenant.schema_name}) ===')
            
            with tenant_context(tenant):
                self.process_tenant_workers(dry_run)
    
    def process_tenant_workers(self, dry_run):
        """Process workers in the current tenant context"""
        
        # Get current status distribution
        total_workers = Worker.objects.count()
        if total_workers == 0:
            self.stdout.write(self.style.WARNING('No workers found in this tenant'))
            return
        
        self.stdout.write(f'Total workers: {total_workers}')
        
        # Show current status distribution
        self.stdout.write('\nCurrent Status Distribution:')
        for status, display in Worker.STATUS_CHOICES:
            count = Worker.objects.filter(status=status).count()
            self.stdout.write(f'  {display}: {count}')
        
        # Example status updates based on conditions
        updates_made = 0
        
        with transaction.atomic():
            # Find workers who completed probation and mark them as 'passed'
            workers_with_completed_probation = Worker.objects.filter(
                probation_periods__status='completed'
            ).distinct()
            
            for worker in workers_with_completed_probation:
                if worker.status == 'active':
                    self.stdout.write(f'  → Setting {worker.get_full_name()} to "Passed" (completed probation)')
                    if not dry_run:
                        worker.status = 'passed'
                        worker.save()
                    updates_made += 1
            
            # Find workers with extended probation
            workers_with_extended_probation = Worker.objects.filter(
                probation_periods__status='extended'
            ).distinct()
            
            for worker in workers_with_extended_probation:
                if worker.status == 'active':
                    self.stdout.write(f'  → Setting {worker.get_full_name()} to "Extended" (probation extended)')
                    if not dry_run:
                        worker.status = 'extended'
                        worker.save()
                    updates_made += 1
            
            # Find workers with failed probation
            workers_with_failed_probation = Worker.objects.filter(
                probation_periods__status='failed'
            ).distinct()
            
            for worker in workers_with_failed_probation:
                if worker.status != 'failed' and worker.status != 'terminated':
                    self.stdout.write(f'  → Setting {worker.get_full_name()} to "Failed" (probation failed)')
                    if not dry_run:
                        worker.status = 'failed'
                        worker.save()
                    updates_made += 1
        
        if dry_run:
            self.stdout.write(f'\nWould update {updates_made} workers')
        else:
            self.stdout.write(f'\nUpdated {updates_made} workers')
            
            # Show new status distribution
            self.stdout.write('\nNew Status Distribution:')
            for status, display in Worker.STATUS_CHOICES:
                count = Worker.objects.filter(status=status).count()
                self.stdout.write(f'  {display}: {count}') 