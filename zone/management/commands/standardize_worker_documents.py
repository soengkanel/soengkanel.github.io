import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from zone.models import Worker, Document


class Command(BaseCommand):
    help = 'Standardize worker documents to have exactly 4 types: passport, visa, work permit, and nationality ID'

    def add_arguments(self, parser):
        parser.add_argument(
            '--workers',
            type=int,
            default=None,
            help='Number of workers to process (default: all workers)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear all existing documents before creating new ones'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Standardizing worker documents...'))

        # Get workers to process
        workers = Worker.objects.all()
        if options['workers']:
            workers = workers[:options['workers']]

        if not workers.exists():
            self.stdout.write(
                self.style.ERROR('No workers found. Please create workers first.')
            )
            return

        # Standard document types we want for each worker
        required_document_types = [
            {
                'type': 'passport',
                'display_name': 'Passport',
                'authority': 'Ministry of Interior',
                'prefix': 'P'
            },
            {
                'type': 'visa',
                'display_name': 'Visa',
                'authority': 'Embassy/Consulate',
                'prefix': 'V'
            },
            {
                'type': 'work_permit',
                'display_name': 'Work Permit',
                'authority': 'Ministry of Labour and Vocational Training',
                'prefix': 'WP'
            },
            {
                'type': 'id_card',
                'display_name': 'Nationality ID',
                'authority': 'National Registration Department',
                'prefix': 'ID'
            }
        ]

        total_workers_processed = 0
        total_documents_created = 0
        total_documents_removed = 0

        # Skip created_by field to avoid constraint issues

        for worker in workers:
            self.stdout.write(f"\nProcessing worker: {worker.get_full_name()} ({worker.worker_id})")
            
            # Current documents
            current_docs = worker.documents.all()
            current_count = current_docs.count()
            current_types = [doc.document_type for doc in current_docs]
            
            self.stdout.write(f"  Current documents: {current_count} - {current_types}")

            # Clear existing documents if requested
            if options['clear_existing']:
                removed_count = current_docs.count()
                current_docs.delete()
                total_documents_removed += removed_count
                self.stdout.write(f"  Removed {removed_count} existing documents")
                current_types = []

            # Create missing documents
            documents_created = 0
            for doc_config in required_document_types:
                doc_type = doc_config['type']
                
                # Check if this document type already exists
                if doc_type in current_types:
                    self.stdout.write(f"  ✓ {doc_config['display_name']} already exists")
                    continue

                # Generate document number
                doc_number = self.generate_document_number(doc_config['prefix'], worker.worker_id)
                
                # Generate realistic dates
                issue_date = date.today() - timedelta(days=random.randint(30, 1095))  # 1 month to 3 years ago
                
                # Different validity periods for different document types
                if doc_type == 'passport':
                    validity_days = random.randint(1825, 3650)  # 5-10 years
                elif doc_type == 'visa':
                    validity_days = random.randint(30, 365)     # 1 month to 1 year
                elif doc_type == 'work_permit':
                    validity_days = random.randint(365, 1095)   # 1-3 years
                else:  # id_card
                    validity_days = random.randint(1825, 5475)  # 5-15 years
                
                expiry_date = issue_date + timedelta(days=validity_days)

                try:
                    document = Document.objects.create(
                        worker=worker,
                        document_type=doc_type,
                        document_number=doc_number,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        issuing_authority=doc_config['authority'],
                        notes=f'Standardized {doc_config["display_name"]} document'
                        # Skip created_by to avoid constraint issues
                    )
                    
                    documents_created += 1
                    total_documents_created += 1
                    self.stdout.write(f"  ✓ Created {doc_config['display_name']}: {doc_number}")
                    
                except Exception as e:

                    
                    pass
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Error creating {doc_config['display_name']}: {str(e)}")
                    )

            total_workers_processed += 1
            final_count = worker.documents.count()
            self.stdout.write(f"  Final document count: {final_count}")

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== STANDARDIZATION COMPLETE ==='))
        self.stdout.write(f'Workers processed: {total_workers_processed}')
        self.stdout.write(f'Documents created: {total_documents_created}')
        if options['clear_existing']:
            self.stdout.write(f'Documents removed: {total_documents_removed}')
        
        # Verification
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=== VERIFICATION ==='))
        for worker in workers[:5]:  # Show first 5 workers
            doc_count = worker.documents.count()
            doc_types = [doc.get_document_type_display() for doc in worker.documents.all()]
            self.stdout.write(f'• {worker.get_full_name()}: {doc_count} documents ({", ".join(doc_types)})')
        
        if workers.count() > 5:
            self.stdout.write(f'... and {workers.count() - 5} more workers')

    def generate_document_number(self, prefix, worker_id):
        """Generate a unique document number."""
        if prefix == 'P':  # Passport
            return f'P{random.randint(100000000, 999999999)}'
        elif prefix == 'V':  # Visa
            return f'V{random.randint(100000000, 999999999)}'
        elif prefix == 'WP':  # Work Permit
            return f'WP{worker_id}{random.randint(1000, 9999)}'
        elif prefix == 'ID':  # ID Card
            return f'ID{random.randint(100000000, 999999999)}'
        else:
            return f'{prefix}{random.randint(100000, 999999)}' 