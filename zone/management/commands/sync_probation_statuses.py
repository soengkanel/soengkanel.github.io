from django.core.management.base import BaseCommand
from django.db import transaction
from zone.models import Worker, WorkerProbationPeriod


class Command(BaseCommand):
    help = 'Sync worker statuses with their current probation statuses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write("DRY RUN MODE - No changes will be made")
        
        # Find workers with active probation periods but mismatched statuses
        mismatched_workers = []
        
        # Check workers with extended probations but worker status not 'extended'
        extended_probations = WorkerProbationPeriod.objects.filter(
            status='extended'
        ).select_related('worker')
        
        for probation in extended_probations:
            worker = probation.worker
            if worker.status != 'extended':
                mismatched_workers.append((worker, 'extended', probation))
                
        # Check workers with active probations but worker status not 'probation' 
        active_probations = WorkerProbationPeriod.objects.filter(
            status='probation'
        ).select_related('worker')
        
        for probation in active_probations:
            worker = probation.worker
            if worker.status != 'probation':
                # Only update if it's not already extended (extended takes precedence)
                if worker.status != 'extended':
                    mismatched_workers.append((worker, 'probation', probation))
        
        if not mismatched_workers:
            self.stdout.write(
                self.style.SUCCESS('No worker status mismatches found. All statuses are in sync!')
            )
            return
        
        self.stdout.write(f"Found {len(mismatched_workers)} workers with mismatched statuses:")
        
        for worker, target_status, probation in mismatched_workers:
            current_status = worker.status
            self.stdout.write(
                f"  - Worker: {worker.get_full_name()} "
                f"(Current: {current_status} -> Should be: {target_status}) "
                f"[Probation: {probation.start_date} to {probation.original_end_date}]"
            )
        
        if not dry_run:
            with transaction.atomic():
                updated_count = 0
                for worker, target_status, probation in mismatched_workers:
                    old_status = worker.status
                    worker.status = target_status
                    worker.save()
                    updated_count += 1
                    
                    self.stdout.write(
                        f"Updated {worker.get_full_name()}: {old_status} -> {target_status}"
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated {updated_count} worker statuses!')
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {len(mismatched_workers)} worker statuses. '
                    'Run without --dry-run to apply changes.'
                )
            )