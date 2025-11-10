from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from audit_management.simple_logger import SimpleAuditLogger
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Create sample audit logs for testing the simplified audit system'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of sample logs to create')

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create test users with proper names
        users = []
        test_users_data = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
            {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'},
            {'username': 'admin_user', 'first_name': 'Admin', 'last_name': 'User', 'email': 'admin@example.com'},
            {'username': 'manager_test', 'first_name': 'Test', 'last_name': 'Manager', 'email': 'manager@example.com'},
        ]
        
        for user_data in test_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            users.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created test user: {user.get_full_name()} ({user.username})'))
        
        if not users:
            # Fallback to any existing user
            users = list(User.objects.all()[:1])
            if not users:
                self.stdout.write(self.style.ERROR('No users found! Please create at least one user first.'))
                return
        
        # Sample models and actions for variety
        sample_data = [
            {'model': 'Employee', 'actions': ['create', 'update', 'delete']},
            {'model': 'Worker', 'actions': ['create', 'update']},
            {'model': 'Department', 'actions': ['create', 'update']},
            {'model': 'Position', 'actions': ['create', 'update']},
            {'model': 'Building', 'actions': ['create', 'update']},
            {'model': 'Zone', 'actions': ['create', 'update']},
        ]
        
        sample_objects = [
            "John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Davis",
            "Engineering Dept", "Sales Team", "Marketing Division", "IT Support",
            "Building A", "Building B", "Zone 1", "Zone 2", "Manager Position"
        ]
        
        sample_descriptions = [
            "Updated employee information",
            "Created new record",
            "Changed status to active",
            "Modified contact details",
            "Updated department assignment",
            "Changed position title",
            "Deleted obsolete record",
            "Added emergency contact",
            "Updated phone number",
            "Modified address information"
        ]
        
        # Create sample logs
        created_logs = 0
        for i in range(count):
            # Randomize timestamp within last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            sample_time = timezone.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Pick random data
            model_data = random.choice(sample_data)
            action = random.choice(model_data['actions'])
            object_name = random.choice(sample_objects)
            description = random.choice(sample_descriptions)
            
            # Pick a random user
            random_user = random.choice(users)
            
            # Create the log
            log = SimpleAuditLogger.log_action(
                user=random_user,
                action=action,
                model_name=model_data['model'],
                object_id=random.randint(1, 1000),
                object_name=object_name,
                description=f"{description} for {object_name}",
                old_values=f"Old value {i}" if action == 'update' else None,
                new_values=f"New value {i}" if action == 'update' else None,
            )
            
            # Override the timestamp
            log.timestamp = sample_time
            log.ip_address = f"192.168.1.{random.randint(1, 255)}"
            log.save()
            
            created_logs += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_logs} sample audit logs')
        )
        
        # Show some stats
        from audit_management.models import SimpleAuditLog
        total_logs = SimpleAuditLog.objects.count()
        self.stdout.write(f'Total audit logs in system: {total_logs}')
        
        # Show recent logs
        recent_logs = SimpleAuditLog.objects.order_by('-timestamp')[:5]
        self.stdout.write('\nRecent audit logs:')
        for log in recent_logs:
            self.stdout.write(f'  • {log.timestamp.strftime("%Y-%m-%d %H:%M")} - {log.user_display} {log.get_action_display().lower()} {log.model_name} "{log.object_name}"')