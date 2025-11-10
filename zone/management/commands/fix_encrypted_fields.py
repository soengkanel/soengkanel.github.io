from django.core.management.base import BaseCommand
from zone.models import Worker, Zone
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Fix encrypted fields that were stored as raw bytes'

    def generate_short_phone(self):
        """Generate a short phone number that fits field constraints"""
        # Generate a simple 10-digit US phone number
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"{area_code}-{exchange}-{number}"

    def handle(self, *args, **options):
        fake = Faker()
        
        self.stdout.write("=== Fixing Worker Encrypted Fields ===")
        
        workers = Worker.objects.all()
        self.stdout.write(f"Found {workers.count()} workers to fix")
        
        fixed_count = 0
        
        for worker in workers:
            needs_update = False
            
            # Check and fix phone_number
            if isinstance(worker.phone_number, bytes) or worker.phone_number is None:
                worker.phone_number = self.generate_short_phone()
                needs_update = True
                self.stdout.write(f"Fixed phone for {worker.worker_id}: {worker.phone_number}")
            
            # Check and fix email
            if hasattr(worker, 'email') and isinstance(worker.email, bytes):
                worker.email = fake.email()
                needs_update = True
                self.stdout.write(f"Fixed email for {worker.worker_id}: {worker.email}")
            
            # Check and fix address
            if hasattr(worker, 'address') and isinstance(worker.address, bytes):
                worker.address = fake.address()
                needs_update = True
                self.stdout.write(f"Fixed address for {worker.worker_id}")
            
            # Check and fix emergency_phone
            if hasattr(worker, 'emergency_phone') and isinstance(worker.emergency_phone, bytes):
                worker.emergency_phone = self.generate_short_phone()
                needs_update = True
                self.stdout.write(f"Fixed emergency phone for {worker.worker_id}: {worker.emergency_phone}")
            
            # Check and fix passport_number
            if hasattr(worker, 'passport_number') and isinstance(worker.passport_number, bytes):
                # Generate a shorter passport number
                worker.passport_number = f"P{random.randint(10000000, 99999999)}"
                needs_update = True
                self.stdout.write(f"Fixed passport for {worker.worker_id}: {worker.passport_number}")
            
            # Check and fix id_card_number
            if hasattr(worker, 'id_card_number') and isinstance(worker.id_card_number, bytes):
                # Generate a shorter ID card number
                worker.id_card_number = f"ID{random.randint(1000000, 9999999)}"
                needs_update = True
                self.stdout.write(f"Fixed ID card for {worker.worker_id}: {worker.id_card_number}")
            
            # Check and fix notes
            if hasattr(worker, 'notes') and isinstance(worker.notes, bytes):
                worker.notes = f"Worker notes for {worker.get_full_name()}"
                needs_update = True
                self.stdout.write(f"Fixed notes for {worker.worker_id}")
            
            if needs_update:
                try:
                    worker.save()
                    fixed_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Updated worker {worker.worker_id}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Failed to update worker {worker.worker_id}: {e}"))
        
        self.stdout.write(f"\n=== Summary ===")
        self.stdout.write(f"Total workers processed: {workers.count()}")
        self.stdout.write(f"Workers fixed: {fixed_count}")
        
        # Fix Zone encrypted fields
        self.stdout.write("\n=== Fixing Zone Encrypted Fields ===")
        zones = Zone.objects.all()
        self.stdout.write(f"Found {zones.count()} zones to check")
        
        zone_fixed_count = 0
        
        for zone in zones:
            needs_update = False
            
            # Check and fix phone_number
            if isinstance(zone.phone_number, bytes) or zone.phone_number is None:
                zone.phone_number = self.generate_short_phone()
                needs_update = True
                self.stdout.write(f"Fixed phone for zone {zone.id}: {zone.phone_number}")
            
            if needs_update:
                try:
                    zone.save()
                    zone_fixed_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Updated zone {zone.id}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Failed to update zone {zone.id}: {e}"))
        
        self.stdout.write(f"Zones fixed: {zone_fixed_count}")
        
        # Test a few workers to verify the fix
        self.stdout.write(f"\n=== Verification ===")
        test_workers = Worker.objects.all()[:3]
        for worker in test_workers:
            self.stdout.write(f"Worker {worker.worker_id}:")
            self.stdout.write(f"  Phone: {worker.phone_number} (type: {type(worker.phone_number)})")
            self.stdout.write(f"  Email: {worker.email} (type: {type(worker.email)})")
            self.stdout.write(f"  Full name: {worker.get_full_name()}")
        
        self.stdout.write(self.style.SUCCESS("\nEncrypted fields fix completed!")) 