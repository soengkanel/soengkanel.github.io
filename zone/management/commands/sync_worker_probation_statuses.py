"""
Management command to sync all worker and probation statuses.
This is a one-time operation to fix existing data before automatic sync takes over.
"""
from django.core.management.base import BaseCommand
from zone.models import Worker, WorkerProbationPeriod


class Command(BaseCommand):
    help = 'Synchronize all worker and probation statuses to eliminate mismatches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--direction',
            choices=['probation_to_worker', 'worker_to_probation', 'auto'],
            default='auto',
            help='Direction of synchronization (default: auto - smart choice based on data)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes'
        )

    def handle(self, *args, **options):
        direction = options['direction']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('Starting worker-probation status synchronization...'))
        
        # Find all mismatched records
        mismatched_records = []
        
        for probation in WorkerProbationPeriod.objects.select_related('worker').all():
            if probation.worker.status != probation.status:
                mismatched_records.append(probation)
        
        if not mismatched_records:
            self.stdout.write(self.style.SUCCESS('✅ All records are already synchronized!'))
            return
        
        self.stdout.write(f'Found {len(mismatched_records)} mismatched records')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Show examples
        self.stdout.write('Examples of mismatched records:')
        for i, probation in enumerate(mismatched_records[:5]):
            self.stdout.write(
                f'  {i+1}. {probation.worker.get_full_name()} ({probation.worker.worker_id}) - '
                f'Worker: {probation.worker.get_status_display()} | '
                f'Probation: {probation.get_status_display()}'
            )
        
        if len(mismatched_records) > 5:
            self.stdout.write(f'  ... and {len(mismatched_records) - 5} more records\n')
        
        # Determine sync direction
        if direction == 'auto':
            # Smart choice: prefer probation status for active records, worker status for completed ones
            probation_to_worker_count = 0
            worker_to_probation_count = 0
            
            for probation in mismatched_records:
                if probation.status in ['probation', 'extended'] and probation.worker.status in ['active', 'inactive']:
                    # Probation is more specific for active probation periods
                    probation_to_worker_count += 1
                elif probation.worker.status in ['passed', 'failed', 'terminated'] and probation.status in ['probation', 'extended']:
                    # Worker status is more current for completed probations
                    worker_to_probation_count += 1
                else:
                    # Default to probation status
                    probation_to_worker_count += 1
            
            self.stdout.write(f'Auto-selection: {probation_to_worker_count} → probation to worker, {worker_to_probation_count} → worker to probation')
        
        # Apply changes
        updated_count = 0
        
        for probation in mismatched_records:
            old_worker_status = probation.worker.status
            old_probation_status = probation.status
            
            # Determine what to update for this record
            if direction == 'probation_to_worker':
                sync_direction = 'probation_to_worker'
            elif direction == 'worker_to_probation':
                sync_direction = 'worker_to_probation'
            else:  # auto
                if probation.status in ['probation', 'extended'] and probation.worker.status in ['active', 'inactive']:
                    sync_direction = 'probation_to_worker'
                elif probation.worker.status in ['passed', 'failed', 'terminated'] and probation.status in ['probation', 'extended']:
                    sync_direction = 'worker_to_probation'
                else:
                    sync_direction = 'probation_to_worker'
            
            if not dry_run:
                if sync_direction == 'probation_to_worker':
                    probation.worker.status = probation.status
                    probation.worker.save(update_fields=['status'])
                    action_msg = f'{old_worker_status} → {probation.status} (worker updated)'
                else:
                    probation.status = probation.worker.status
                    probation.save(update_fields=['status'])
                    action_msg = f'{old_probation_status} → {probation.worker.status} (probation updated)'
                
                updated_count += 1
            else:
                if sync_direction == 'probation_to_worker':
                    action_msg = f'{old_worker_status} → {probation.status} (would update worker)'
                else:
                    action_msg = f'{old_probation_status} → {probation.worker.status} (would update probation)'
            
            self.stdout.write(f'  {probation.worker.get_full_name()} ({probation.worker.worker_id}): {action_msg}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nDRY RUN: Would update {len(mismatched_records)} records'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully synchronized {updated_count} records!'))
            self.stdout.write('From now on, all status changes will be automatically synchronized.')