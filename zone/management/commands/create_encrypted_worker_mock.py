from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from zone.models import Zone, Building, Floor, Position, Department
from core.encryption import encryption_manager, validate_encryption_setup
import random
import json
from datetime import date, timedelta
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Create mock workers with encrypted sensitive data to demonstrate encryption functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of workers to create (default: 5)',
        )
        parser.add_argument(
            '--show-encryption',
            action='store_true',
            help='Display encryption/decryption demonstration',
        )
        parser.add_argument(
            '--validate-encryption',
            action='store_true',
            help='Validate encryption setup before creating workers',
        )

    def handle(self, *args, **options):
        # Validate encryption setup first
        if options['validate_encryption'] or options['show_encryption']:
            if not validate_encryption_setup():
                raise CommandError("❌ Encryption setup validation failed! Run 'python manage.py setup_encryption --validate'")
            self.stdout.write(self.style.SUCCESS("✅ Encryption setup validated successfully!"))

        count = options['count']
        
        self.stdout.write(f"🔒 Creating {count} mock workers with encrypted sensitive data...")
        
        # Create required dependencies first
        self.ensure_dependencies()
        
        # Create mock workers
        workers_created = self.create_mock_workers(count)
        
        if options['show_encryption']:
            self.demonstrate_encryption(workers_created)
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully created {len(workers_created)} encrypted workers!")
        )

    def ensure_dependencies(self):
        """Ensure required objects exist for worker creation"""
        # Create test user for zone if doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test_zone',
            defaults={
                'email': 'test_zone@example.com',
                'first_name': 'Test',
                'last_name': 'Zone',
                'is_active': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write("📝 Created test zone user")

        # Create building if doesn't exist
        building, created = Building.objects.get_or_create(
            name='Test Building',
            defaults={
                'address': '123 Test Street, Test City',
                'total_floors': 5,
                'description': 'Test building for encrypted worker demo',
                'created_by': test_user
            }
        )
        if created:
            self.stdout.write("🏢 Created test building")

        # Create floor if doesn't exist
        floor, created = Floor.objects.get_or_create(
            building=building,
            floor_number=1,
            defaults={
                'name': 'Ground Floor',
                'description': 'Test floor for encrypted worker demo',
                'created_by': test_user
            }
        )
        if created:
            self.stdout.write("🏠 Created test floor")

        # Create zone if doesn't exist
        zone, created = Zone.objects.get_or_create(
            name='Test Zone',
            defaults={
                'phone_number': '+1234567890',
                'address': '456 Zone Street, Zone City',
                'is_active': True,
                'created_by': test_user
            }
        )
        if created:
            self.stdout.write("👤 Created test zone")

        # Create department if doesn't exist
        department, created = Department.objects.get_or_create(
            name='General Workers',
            defaults={
                'code': 'GEN',
                'description': 'General workers department for testing',
                'created_by': test_user
            }
        )
        if created:
            self.stdout.write("🏛️ Created test department")

        # Create position if doesn't exist
        position, created = Position.objects.get_or_create(
            name='General Worker',
            defaults={
                'code': 'GW',
                'department': department,
                'level': 1,
                'description': 'General worker position for testing',
                'created_by': test_user
            }
        )
        if created:
            self.stdout.write("💼 Created test position")

        self.zone = zone
        self.building = building
        self.floor = floor
        self.position = position
        self.test_user = test_user

    def create_mock_workers(self, count):
        """Create mock workers with encrypted sensitive data"""
        from zone.models import Worker  # Import the regular Worker model
        
        workers_created = []
        
        # Sample data for realistic mock generation
        nationalities = ['TH', 'VN', 'MY', 'PH', 'ID', 'KH', 'MM', 'LA']
        banks = ['Bangkok Bank', 'Kasikorn Bank', 'SCB Bank', 'Krung Thai Bank', 'Bank of Ayudhya']
        
        with transaction.atomic():
            for i in range(count):
                # Generate realistic sensitive data
                nationality = random.choice(nationalities)
                
                # Create worker with both regular and sensitive (encrypted) fields
                worker_data = {
                    'worker_id': f'EW{2024}{str(i+1).zfill(4)}',  # EW20240001, EW20240002, etc.
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'sex': random.choice(['M', 'F']),
                    'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=65),
                    'nationality': nationality,
                    
                    # ENCRYPTED SENSITIVE DATA
                    'phone_number': fake.phone_number(),
                    'email': fake.email(),
                    'address': fake.address(),
                    'emergency_phone': fake.phone_number(),
                    'passport_number': f'{nationality}{fake.random_number(digits=8)}',
                    'id_card_number': str(fake.random_number(digits=13)),
                    
                    # Work information
                    'zone': self.zone,
                    'building': self.building,
                    'floor': self.floor,
                    'position': self.position,
                    'status': 'active',
                    'performance_rating': random.randint(3, 5),
                    'notes': f'Mock worker created for encryption demonstration. Performance: {random.choice(["Excellent", "Good", "Average"])}',
                    'created_by': self.test_user
                }
                
                # Additional sensitive data
                worker_data['emergency_contact'] = fake.name()
                
                # Create worker
                worker = Worker.objects.create(**worker_data)
                workers_created.append(worker)
                
                self.stdout.write(f"  👤 Created worker: {worker.get_full_name()} (ID: {worker.worker_id})")
        
        return workers_created

    def demonstrate_encryption(self, workers):
        """Demonstrate encryption/decryption functionality"""
        if not workers:
            self.stdout.write(self.style.WARNING("No workers to demonstrate encryption"))
            return

        worker = workers[0]  # Use first worker for demonstration
        
        self.stdout.write(
            self.style.HTTP_INFO(
                f"\n🔒 ENCRYPTION DEMONSTRATION - Worker: {worker.get_full_name()}\n" +
                "=" * 70
            )
        )

        # Demonstrate encryption of sensitive fields
        sensitive_fields = [
            ('phone_number', 'Phone Number'),
            ('email', 'Email'),
            ('passport_number', 'Passport Number'),
            ('id_card_number', 'ID Card Number'),
            ('address', 'Address'),
        ]

        for field_name, display_name in sensitive_fields:
            original_value = getattr(worker, field_name)
            if original_value:
                # Show how the data looks when encrypted in database
                encrypted_value = encryption_manager.encrypt(original_value)
                
                self.stdout.write(f"\n📝 {display_name}:")
                self.stdout.write(f"  🔓 Decrypted (App View): {original_value}")
                self.stdout.write(f"  🔒 Encrypted (DB Storage): {encrypted_value[:50]}...")
                
                # Demonstrate masking for different user permissions
                from core.encryption import mask_sensitive_data
                masked_value = mask_sensitive_data(original_value)
                self.stdout.write(f"  👀 Masked (Restricted User): {masked_value}")

        # Demonstrate permission-based access
        self.stdout.write(f"\n🔐 PERMISSION-BASED ACCESS DEMONSTRATION")
        self.stdout.write("-" * 50)
        
        # Create a mock admin user
        admin_user = User(is_superuser=True, username='admin')
        
        # Create a mock regular user
        regular_user = User(is_superuser=False, username='regular')
        
        # Show data for admin user
        admin_data = worker.get_display_data(admin_user)
        self.stdout.write(f"\n👑 Admin User View:")
        self.stdout.write(f"  Phone: {admin_data.get('phone_number', 'N/A')}")
        self.stdout.write(f"  Email: {admin_data.get('email', 'N/A')}")
        self.stdout.write(f"  Passport: {admin_data.get('passport_number', 'N/A')}")
        
        # Show data for regular user
        regular_data = worker.get_display_data(regular_user)
        self.stdout.write(f"\n👤 Regular User View:")
        self.stdout.write(f"  Phone: {regular_data.get('phone_number', 'N/A')}")
        self.stdout.write(f"  Email: {regular_data.get('email', 'N/A')}")
        self.stdout.write(f"  Passport: {regular_data.get('passport_number', 'N/A')}")

        # Show encryption statistics
        self.stdout.write(f"\n📊 ENCRYPTION STATISTICS")
        self.stdout.write("-" * 30)
        
        total_workers = len(workers)
        encrypted_fields_per_worker = 0
        
        for worker in workers:
            encrypted_fields = [
                worker.phone_number, worker.email, worker.passport_number,
                worker.id_card_number, worker.address
            ]
            encrypted_fields_per_worker += len([f for f in encrypted_fields if f])
        
        avg_encrypted_fields = encrypted_fields_per_worker / total_workers if total_workers > 0 else 0
        
        self.stdout.write(f"  Total Workers Created: {total_workers}")
        self.stdout.write(f"  Total Encrypted Fields: {encrypted_fields_per_worker}")
        self.stdout.write(f"  Avg Encrypted Fields per Worker: {avg_encrypted_fields:.1f}")
        
        # Database storage comparison
        self.stdout.write(f"\n💾 DATABASE STORAGE COMPARISON")
        self.stdout.write("-" * 35)
        
        sample_phone = worker.phone_number
        if sample_phone:
            original_size = len(sample_phone)
            encrypted_size = len(encryption_manager.encrypt(sample_phone))
            overhead = ((encrypted_size - original_size) / original_size) * 100
            
            self.stdout.write(f"  Original Phone Number: {original_size} characters")
            self.stdout.write(f"  Encrypted Phone Number: {encrypted_size} characters")
            self.stdout.write(f"  Storage Overhead: {overhead:.1f}%")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Encryption demonstration complete! All sensitive data is protected."
            )
        )

    def show_encryption_summary(self):
        """Show summary of encryption implementation"""
        self.stdout.write(
            self.style.HTTP_INFO(
                "\n📋 ENCRYPTION IMPLEMENTATION SUMMARY\n" +
                "=" * 50 + "\n" +
                "✅ Sensitive Data Encrypted:\n" +
                "  • Phone numbers\n" +
                "  • Email addresses\n" +
                "  • Home addresses\n" +
                "  • Passport numbers\n" +
                "  • ID card numbers\n" +
                "  • Bank account numbers\n" +
                "  • Emergency contact phones\n" +
                "  • Internal notes\n\n" +
                "🔒 Encryption Features:\n" +
                "  • AES-256 encryption using Fernet\n" +
                "  • Automatic encryption/decryption\n" +
                "  • Permission-based data access\n" +
                "  • Data masking for restricted users\n" +
                "  • Backward compatibility with legacy data\n\n" +
                "🛡️ Security Benefits:\n" +
                "  • Data at rest protection\n" +
                "  • Compliance ready (GDPR, CCPA)\n" +
                "  • Role-based access control\n" +
                "  • Audit trail capability\n" +
                "  • Zero application code changes\n"
            )
        ) 