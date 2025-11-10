from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from zone.models import Worker, WorkerProbationPeriod, WorkerProbationExtension
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Manage worker probation periods and extensions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            help='Action to perform: create, extend, complete, list, demo',
            choices=['create', 'extend', 'complete', 'list', 'demo'],
            default='demo'
        )
        parser.add_argument(
            '--worker-id',
            type=str,
            help='Worker ID for the action'
        )
        parser.add_argument(
            '--duration-days',
            type=int,
            help='Duration in days for probation period or extension',
            default=90
        )
        parser.add_argument(
            '--reason',
            type=str,
            help='Reason for extension'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'demo':
            self.run_demo()
        elif action == 'create':
            self.create_probation(options)
        elif action == 'extend':
            self.extend_probation(options)
        elif action == 'complete':
            self.complete_probation(options)
        elif action == 'list':
            self.list_probations()

    def run_demo(self):
        """Demonstrate probation functionality with existing workers"""
        self.stdout.write(self.style.SUCCESS('=== Worker Probation Management Demo ===\n'))
        
        # Get first worker for demo
        worker = Worker.objects.first()
        if not worker:
            self.stdout.write(self.style.ERROR('No workers found. Please create some workers first.'))
            return
            
        # Get admin user for created_by
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        
        self.stdout.write(f'Using worker: {worker.get_full_name()} ({worker.worker_id})')
        self.stdout.write(f'Admin user: {admin_user.username}\n')
        
        # 1. Create a probation period
        self.stdout.write(self.style.WARNING('1. Creating probation period...'))
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=15)
        
        # Set worker status to probation
        worker.status = 'probation'
        worker.save()
        
        probation = WorkerProbationPeriod.objects.create(
            worker=worker,
            start_date=start_date,
            original_end_date=end_date,
            evaluation_notes='Initial probation period - 15 days',
            created_by=admin_user
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created probation period: {probation}'))
        self.stdout.write(f'  - Start Date: {probation.start_date}')
        self.stdout.write(f'  - Original End Date: {probation.original_end_date}')
        self.stdout.write(f'  - Status: {probation.status}')
        self.stdout.write(f'  - Is Active: {probation.is_active}')
        self.stdout.write(f'  - Days Remaining: {probation.days_remaining}\n')
        
        # 2. Check worker probation properties
        self.stdout.write(self.style.WARNING('2. Checking worker probation properties...'))
        self.stdout.write(f'  - Worker is on probation: {worker.is_on_probation}')
        self.stdout.write(f'  - Probation end date: {worker.probation_end_date}')
        self.stdout.write(f'  - Days remaining: {worker.probation_days_remaining}\n')
        
        # 3. Create an extension
        self.stdout.write(self.style.WARNING('3. Creating probation extension...'))
        extension = WorkerProbationExtension.objects.create(
            probation_period=probation,
            extension_duration_days=15,
            reason='Need additional time for performance evaluation',
            approved_by=admin_user,
            created_by=admin_user
        )
        
        # Refresh probation from database
        probation.refresh_from_db()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created extension: {extension}'))
        self.stdout.write(f'  - Extension Duration: {extension.extension_duration_days} days')
        self.stdout.write(f'  - Reason: {extension.reason}')
        self.stdout.write(f'  - Approved By: {extension.approved_by}')
        self.stdout.write(f'  - Updated Probation Status: {probation.status}')
        self.stdout.write(f'  - New End Date: {probation.actual_end_date}')
        self.stdout.write(f'  - Total Duration: {probation.total_duration_days} days\n')
        
        # 4. List all probation periods
        self.stdout.write(self.style.WARNING('4. Current probation periods...'))
        self.list_probations()
        
        # 5. Complete the probation
        self.stdout.write(self.style.WARNING('5. Completing probation period...'))
        probation.status = 'completed'
        probation.save()
        
        self.stdout.write(self.style.SUCCESS('✓ Probation completed'))
        self.stdout.write(f'  - Final Status: {probation.status}')
        self.stdout.write(f'  - Worker is still on probation: {worker.is_on_probation}\n')
        
        self.stdout.write(self.style.SUCCESS('=== Demo Complete ==='))

    def create_probation(self, options):
        """Create a new probation period for a worker"""
        worker_id = options.get('worker_id')
        duration_days = options.get('duration_days', 15)
        
        if not worker_id:
            self.stdout.write(self.style.ERROR('Worker ID is required for create action'))
            return
            
        try:
            worker = Worker.objects.get(worker_id=worker_id)
        except Worker.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Worker with ID {worker_id} not found'))
            return
        
        # Check if worker already has active probation
        if worker.is_on_probation:
            self.stdout.write(self.style.ERROR(f'Worker {worker.get_full_name()} already has an active probation period'))
            return
        
        admin_user = User.objects.filter(is_superuser=True).first()
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=duration_days)
        
        # Set worker status to probation
        worker.status = 'probation'
        worker.save()
        
        probation = WorkerProbationPeriod.objects.create(
            worker=worker,
            start_date=start_date,
            original_end_date=end_date,
            evaluation_notes=f'Probation period - {duration_days} days',
            created_by=admin_user
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created probation period for {worker.get_full_name()}'))
        self.stdout.write(f'  Duration: {duration_days} days')
        self.stdout.write(f'  End Date: {end_date}')

    def extend_probation(self, options):
        """Extend an existing probation period"""
        worker_id = options.get('worker_id')
        duration_days = options.get('duration_days', 15)
        reason = options.get('reason', 'Extension requested')
        
        if not worker_id:
            self.stdout.write(self.style.ERROR('Worker ID is required for extend action'))
            return
            
        try:
            worker = Worker.objects.get(worker_id=worker_id)
        except Worker.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Worker with ID {worker_id} not found'))
            return
        
        probation = worker.current_probation_period
        if not probation:
            self.stdout.write(self.style.ERROR(f'Worker {worker.get_full_name()} has no active probation period'))
            return
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        extension = WorkerProbationExtension.objects.create(
            probation_period=probation,
            extension_duration_days=duration_days,
            reason=reason,
            approved_by=admin_user,
            created_by=admin_user
        )
        
        probation.refresh_from_db()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Extended probation for {worker.get_full_name()}'))
        self.stdout.write(f'  Extension: {duration_days} days')
        self.stdout.write(f'  New End Date: {probation.actual_end_date}')
        self.stdout.write(f'  Reason: {reason}')

    def complete_probation(self, options):
        """Complete an active probation period"""
        worker_id = options.get('worker_id')
        
        if not worker_id:
            self.stdout.write(self.style.ERROR('Worker ID is required for complete action'))
            return
            
        try:
            worker = Worker.objects.get(worker_id=worker_id)
        except Worker.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Worker with ID {worker_id} not found'))
            return
        
        probation = worker.current_probation_period
        if not probation:
            self.stdout.write(self.style.ERROR(f'Worker {worker.get_full_name()} has no active probation period'))
            return
        
        probation.status = 'completed'
        probation.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Completed probation for {worker.get_full_name()}'))

    def list_probations(self):
        """List all probation periods"""
        probations = WorkerProbationPeriod.objects.select_related('worker').order_by('-start_date')
        
        if not probations.exists():
            self.stdout.write(self.style.WARNING('No probation periods found'))
            return
        
        self.stdout.write(self.style.SUCCESS('Current Probation Periods:'))
        self.stdout.write('-' * 80)
        
        for probation in probations:
            status_color = self.style.SUCCESS if probation.status == 'completed' else self.style.WARNING
            
            self.stdout.write(f'Worker: {probation.worker.get_full_name()} ({probation.worker.worker_id})')
            self.stdout.write(f'  Start: {probation.start_date} | End: {probation.actual_end_date or probation.original_end_date}')
            self.stdout.write(status_color(f'  Status: {probation.status.upper()}'))
            self.stdout.write(f'  Days Remaining: {probation.days_remaining}')
            self.stdout.write(f'  Extensions: {probation.extensions.count()}')
            self.stdout.write('') 