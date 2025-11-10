from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from zone.models import Worker, WorkerProbationPeriod, WorkerProbationExtension
from cards.models import WorkerIDCard


class Command(BaseCommand):
    help = 'Create comprehensive probation mock data for showcase with balanced status distribution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all probation data before creating new mock data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reset = options['reset']
        
        self.stdout.write(self.style.SUCCESS('🎭 Comprehensive Probation Mock Data Generator'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 DRY RUN MODE - No changes will be made'))
        
        if reset and not dry_run:
            self.stdout.write(self.style.WARNING('🗑️  Resetting all probation data...'))
            WorkerProbationExtension.objects.all().delete()
            WorkerProbationPeriod.objects.all().delete()
            WorkerIDCard.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ All probation data reset'))
        
        # Get all workers
        all_workers = list(Worker.objects.all())
        total_workers = len(all_workers)
        
        if total_workers == 0:
            self.stdout.write(self.style.ERROR('❌ No workers found!'))
            return
        
        self.stdout.write(f'📊 Found {total_workers} total workers')
        
        # Target distribution for better showcase
        target_completed = 25        # Workers who completed probation
        target_active = 35          # Workers currently on probation  
        target_extended = 8         # Workers with extended probation
        target_ending_soon = 5      # Workers ending in next 7 days
        target_no_probation = total_workers - (target_completed + target_active + target_extended + target_ending_soon)
        
        self.stdout.write('')
        self.stdout.write('🎯 Target Distribution:')
        self.stdout.write(f'   ✅ Completed: {target_completed}')
        self.stdout.write(f'   🟡 Active: {target_active}')
        self.stdout.write(f'   🔄 Extended: {target_extended}')
        self.stdout.write(f'   ⚠️  Ending Soon: {target_ending_soon}')
        self.stdout.write(f'   ⚪ No Probation: {target_no_probation}')
        self.stdout.write('')
        
        # Shuffle workers for random selection
        random.shuffle(all_workers)
        
        counts = {
            'completed': 0,
            'active': 0,
            'extended': 0,
            'ending_soon': 0,
            'cards_created': 0
        }
        
        worker_index = 0
        
        # 1. Create COMPLETED probations
        self.stdout.write('🏁 Creating COMPLETED probations...')
        for i in range(target_completed):
            if worker_index >= total_workers:
                break
            worker = all_workers[worker_index]
            worker_index += 1
            
            # Create completed probation (ended 1-30 days ago, standard 15-day duration)
            days_ago = random.randint(1, 30)
            end_date = date.today() - timedelta(days=days_ago)
            start_date = end_date - timedelta(days=15)  # Standard 15-day probation
            
            if not dry_run:
                probation = WorkerProbationPeriod.objects.create(
                    worker=worker,
                    start_date=start_date,
                    original_end_date=end_date,
                    actual_end_date=end_date,
                    status='completed',
                    evaluation_notes=f'Probation completed successfully. Worker demonstrated excellent performance and commitment.',
                    created_by_id=1  # Assume admin user
                )
                
                # Create ID card for completed probation
                WorkerIDCard.objects.create(
                    worker=worker,
                    status='pending',
                    request_date=timezone.now(),
                    expiry_date=date.today() + timedelta(days=365),
                    notes=f'ID card created after probation completion'
                )
                counts['cards_created'] += 1
            
            counts['completed'] += 1
            self.stdout.write(f'   ✅ {worker.get_full_name()} - Completed {days_ago} days ago')
        
        # 2. Create ACTIVE probations
        self.stdout.write('')
        self.stdout.write('🟡 Creating ACTIVE probations...')
        for i in range(target_active):
            if worker_index >= total_workers:
                break
            worker = all_workers[worker_index]
            worker_index += 1
            
            # Create active probation (started 1-14 days ago, standard 15-day duration)
            days_started = random.randint(1, 14)
            start_date = date.today() - timedelta(days=days_started)
            end_date = start_date + timedelta(days=15)  # Standard 15-day probation
            
            if not dry_run:
                WorkerProbationPeriod.objects.create(
                    worker=worker,
                    start_date=start_date,
                    original_end_date=end_date,
                    status='active',
                    evaluation_notes=f'Worker is progressing well during probation period.',
                    created_by_id=1
                )
            
            counts['active'] += 1
            days_remaining = (end_date - date.today()).days
            self.stdout.write(f'   🟡 {worker.get_full_name()} - {days_remaining} days remaining')
        
        # 3. Create EXTENDED probations
        self.stdout.write('')
        self.stdout.write('🔄 Creating EXTENDED probations...')
        for i in range(target_extended):
            if worker_index >= total_workers:
                break
            worker = all_workers[worker_index]
            worker_index += 1
            
            # Create extended probation - FIXED: Ensure total probation ≤ 30 days (15 default + max 15 extension)
            days_started = random.randint(10, 25)  # Started 10-25 days ago to allow for extensions
            start_date = date.today() - timedelta(days=days_started)
            original_end_date = start_date + timedelta(days=15)  # Standard 15-day probation
            extension_days = random.randint(7, 15)  # Max 15 days extension to reach 30 total
            
            if not dry_run:
                probation = WorkerProbationPeriod.objects.create(
                    worker=worker,
                    start_date=start_date,
                    original_end_date=original_end_date,
                    status='extended',
                    evaluation_notes=f'Probation extended to allow additional time for improvement.',
                    created_by_id=1
                )
                
                # Create extension record
                WorkerProbationExtension.objects.create(
                    probation_period=probation,
                    extension_duration_days=extension_days,
                    reason=random.choice([
                        'Additional training required',
                        'Performance improvement needed',
                        'Skill development in progress',
                        'Adjustment period required'
                    ]),
                    approved_by_id=1,
                    created_by_id=1
                )
            
            counts['extended'] += 1
            new_end_date = original_end_date + timedelta(days=extension_days)
            days_remaining = (new_end_date - date.today()).days
            self.stdout.write(f'   🔄 {worker.get_full_name()} - Extended +{extension_days} days, {days_remaining} remaining')
        
        # 4. Create ENDING SOON probations
        self.stdout.write('')
        self.stdout.write('⚠️  Creating ENDING SOON probations...')
        for i in range(target_ending_soon):
            if worker_index >= total_workers:
                break
            worker = all_workers[worker_index]
            worker_index += 1
            
            # Create probation ending in 1-7 days (standard 15-day duration)
            days_remaining = random.randint(1, 7)
            end_date = date.today() + timedelta(days=days_remaining)
            start_date = end_date - timedelta(days=15)  # Standard 15-day probation
            
            if not dry_run:
                WorkerProbationPeriod.objects.create(
                    worker=worker,
                    start_date=start_date,
                    original_end_date=end_date,
                    status='active',
                    evaluation_notes=f'Worker approaching end of probation period. Final evaluation pending.',
                    created_by_id=1
                )
            
            counts['ending_soon'] += 1
            self.stdout.write(f'   ⚠️  {worker.get_full_name()} - Ending in {days_remaining} days')
        
        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS('✅ MOCK DATA GENERATED SUCCESSFULLY!'))
            self.stdout.write('')
            self.stdout.write('📈 Final Distribution:')
            self.stdout.write(f'   ✅ Completed: {counts["completed"]}')
            self.stdout.write(f'   🟡 Active: {counts["active"]}')
            self.stdout.write(f'   🔄 Extended: {counts["extended"]}')
            self.stdout.write(f'   ⚠️  Ending Soon: {counts["ending_soon"]}')
            self.stdout.write(f'   🆔 ID Cards Created: {counts["cards_created"]}')
            self.stdout.write('')
            self.stdout.write('🎉 Perfect showcase data created!')
        else:
            self.stdout.write(self.style.WARNING('🧪 DRY RUN COMPLETE - No changes made'))
            self.stdout.write('💡 Run without --dry-run to apply changes')
        
        self.stdout.write('')
        self.stdout.write('🔗 Visit these pages to see the results:')
        self.stdout.write('   📋 /zone/probation/ - Probation list with balanced statuses')
        self.stdout.write('   🆔 /cards/worker-id-cards/ - ID cards for completed workers')
        self.stdout.write('   🐛 /cards/debug/probation-status/ - Debug probation status') 