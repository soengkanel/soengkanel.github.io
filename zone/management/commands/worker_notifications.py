from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from zone.models import Worker, WorkerProbationPeriod, Document
from core.models import Notification
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create web notifications for worker probation and document expiry'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='all',
            choices=['all', 'probation', 'documents', 'test'],
            help='Type of notifications to create',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Number of days ahead to check for expiring items (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating notifications',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specific user ID to send test notifications to',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.days_ahead = options['days_ahead']
        self.test_user_id = options.get('user_id')
        
        if options['mode'] == 'test':
            self.create_test_notifications()
        elif options['mode'] == 'probation':
            self.check_probation_periods()
        elif options['mode'] == 'documents':
            self.check_document_expiry()
        else:
            self.check_probation_periods()
            self.check_document_expiry()

    def create_test_notifications(self):
        """Create test notifications to verify system functionality"""
        if not self.test_user_id:
            self.stdout.write(self.style.ERROR('User ID is required for test mode'))
            return
        
        try:
            test_user = User.objects.get(id=self.test_user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {self.test_user_id} not found'))
            return

        self.stdout.write(self.style.SUCCESS('=== CREATING TEST NOTIFICATIONS ==='))
        
        if self.dry_run:
            self.stdout.write('[DRY RUN] Would create test notifications for:')
            self.stdout.write(f'  User: {test_user.get_full_name()} ({test_user.username})')
            return

        try:
            # Create test probation notification
            probation_notification = Notification.objects.create(
                title='[TEST] Probation Ending Soon - John Doe',
                message='This is a test probation notification. Worker John Doe (WKR2024001) probation period ends in 3 days.',
                notification_type='probation_ending',
                priority='high',
                recipient=test_user,
                action_url='/zone/probation/',
                action_text='View Probations',
                expires_at=timezone.now() + timedelta(days=7)
            )

            # Create test document expiry notification
            document_notification = Notification.objects.create(
                title='[TEST] Document Expiring Soon - John Doe',
                message='This is a test document notification. Worker John Doe (WKR2024001) Work Permit expires in 3 days.',
                notification_type='document_expiring',
                priority='critical',
                recipient=test_user,
                action_url='/zone/workers/',
                action_text='View Workers',
                expires_at=timezone.now() + timedelta(days=7)
            )

            self.stdout.write(self.style.SUCCESS(f'✓ Test notifications created for {test_user.username}'))
            self.stdout.write(f'  - Probation notification ID: {probation_notification.id}')
            self.stdout.write(f'  - Document notification ID: {document_notification.id}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to create test notifications: {str(e)}'))

    def check_probation_periods(self):
        """Check for probation periods ending soon or overdue"""
        self.stdout.write(self.style.SUCCESS('=== CHECKING PROBATION PERIODS ==='))
        
        today = timezone.now().date()
        
        # Find probation periods ending soon
        ending_soon = WorkerProbationPeriod.objects.filter(
            status__in=['active', 'extended'],
        ).select_related('worker', 'worker__zone', 'worker__zone__created_by')
        
        notifications_created = 0
        overdue_count = 0
        ending_soon_count = 0
        
        for period in ending_soon:
            days_remaining = period.get_days_remaining()
            
            # Skip if not within our notification window
            if days_remaining > self.days_ahead:
                continue
                
            worker = period.worker
            
            # Determine notification type
            if days_remaining <= 0:
                overdue_count += 1
            else:
                ending_soon_count += 1
            
            # Get recipients
            recipients = self.get_notification_recipients(worker)
            
            for recipient in recipients:
                try:
                    # Check if we already have a recent notification for this
                    recent_notification = Notification.objects.filter(
                        recipient=recipient,
                        notification_type__in=['probation_ending', 'probation_overdue'],
                        related_object_type='worker_probation',
                        related_object_id=period.id,
                        created_at__gte=timezone.now() - timedelta(days=1)
                    ).exists()
                    
                    if recent_notification:
                        continue  # Skip if already notified recently
                    
                    if self.dry_run:
                        self.stdout.write(f'[DRY RUN] Would create probation notification for {recipient.username}:')
                        self.stdout.write(f'  Worker: {worker.get_full_name()} ({worker.worker_id})')
                        self.stdout.write(f'  Days remaining: {days_remaining}')
                        continue
                    
                    # Create notification
                    notification = Notification.create_probation_notification(
                        worker=worker,
                        probation_period=period,
                        recipient=recipient,
                        days_remaining=days_remaining
                    )
                    notifications_created += 1
                    
                    self.stdout.write(f'✓ Created probation notification for {recipient.username} about {worker.get_full_name()}')
                    
                except Exception as e:

                    
                    pass
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to create probation notification for {worker.get_full_name()}: {str(e)}')
                    )
        
        self.stdout.write(f'Probation Summary:')
        self.stdout.write(f'  • Overdue probations: {overdue_count}')
        self.stdout.write(f'  • Ending soon: {ending_soon_count}')
        self.stdout.write(f'  • Notifications created: {notifications_created}')

    def check_document_expiry(self):
        """Check for documents expiring soon"""
        self.stdout.write(self.style.SUCCESS('=== CHECKING DOCUMENT EXPIRY ==='))
        
        today = timezone.now().date()
        target_date = today + timedelta(days=self.days_ahead)
        
        # Find documents expiring soon
        expiring_docs = Document.objects.filter(
            expiry_date__lte=target_date,
            expiry_date__gte=today - timedelta(days=30)  # Include already expired docs up to 30 days
        ).select_related('worker', 'worker__zone', 'worker__zone__created_by')
        
        notifications_created = 0
        expired_count = 0
        expiring_count = 0
        
        for document in expiring_docs:
            days_remaining = (document.expiry_date - today).days
            
            if days_remaining <= 0:
                expired_count += 1
            else:
                expiring_count += 1
            
            worker = document.worker
            recipients = self.get_notification_recipients(worker)
            
            for recipient in recipients:
                try:
                    # Check if we already have a recent notification for this document
                    recent_notification = Notification.objects.filter(
                        recipient=recipient,
                        notification_type__in=['document_expiring', 'document_expired'],
                        related_object_type='worker_document',
                        related_object_id=document.id,
                        created_at__gte=timezone.now() - timedelta(days=1)
                    ).exists()
                    
                    if recent_notification:
                        continue  # Skip if already notified recently
                    
                    if self.dry_run:
                        self.stdout.write(f'[DRY RUN] Would create document expiry notification for {recipient.username}:')
                        self.stdout.write(f'  Worker: {worker.get_full_name()} ({worker.worker_id})')
                        self.stdout.write(f'  Document: {document.get_document_type_display()}')
                        self.stdout.write(f'  Days remaining: {days_remaining}')
                        continue
                    
                    # Create notification
                    notification = Notification.create_document_expiry_notification(
                        worker=worker,
                        document=document,
                        recipient=recipient,
                        days_remaining=days_remaining
                    )
                    notifications_created += 1
                    
                    self.stdout.write(f'✓ Created document expiry notification for {recipient.username} about {worker.get_full_name()}')
                    
                except Exception as e:

                    
                    pass
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to create document expiry notification for {worker.get_full_name()}: {str(e)}')
                    )
        
        self.stdout.write(f'Document Expiry Summary:')
        self.stdout.write(f'  • Expired documents: {expired_count}')
        self.stdout.write(f'  • Expiring soon: {expiring_count}')
        self.stdout.write(f'  • Notifications created: {notifications_created}')

    def get_notification_recipients(self, worker):
        """Get list of users who should receive notifications for this worker"""
        recipients = []
        
        # Add zone/manager if exists
        if worker.zone and worker.zone.created_by:
            recipients.append(worker.zone.created_by)
        
        # Add building managers (if any)
        if worker.building:
            # You can extend this to include building managers if you have that model
            pass
        
        # Add HR team (staff users)
        hr_users = User.objects.filter(is_staff=True)
        recipients.extend(hr_users)
        
        # Remove duplicates
        unique_recipients = list(set(recipients))
        
        return unique_recipients

 