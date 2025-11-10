"""
Management command to import workers from Excel file
Uses the clean worker_import module
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from zone.worker_import import import_workers_from_excel
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Import workers from Excel file with images'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Path to the Excel file to import'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username to use as created_by (default: admin)'
        )
    
    def handle(self, *args, **options):
        excel_file = options['excel_file']
        username = options['username']
        
        # Validate file exists
        if not os.path.exists(excel_file):
            self.stdout.write(
                self.style.ERROR(f"File not found: {excel_file}")
            )
            return
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User not found: {username}")
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f"Starting import from: {excel_file}")
        )
        
        try:
            # Import workers
            results = import_workers_from_excel(excel_file, user)
            
            # Display results
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nImport completed successfully!"
                )
            )
            self.stdout.write(
                f"✓ Workers created: {results['success_count']}"
            )
            
            if results['error_count'] > 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Errors: {results['error_count']}"
                    )
                )
                for error in results['errors']:
                    self.stdout.write(
                        self.style.ERROR(f"  - {error}")
                    )
            
            # Show created workers
            if results['workers_created']:
                self.stdout.write("\nWorkers created:")
                for worker in results['workers_created'][:5]:  # Show first 5
                    self.stdout.write(
                        f"  • {worker['name']} (ID: {worker['id']}, Row: {worker['row']})"
                    )
                if len(results['workers_created']) > 5:
                    self.stdout.write(
                        f"  ... and {len(results['workers_created']) - 5} more"
                    )
            
            # Show warnings if any
            if results.get('warnings'):
                self.stdout.write(
                    self.style.WARNING("\nWarnings:")
                )
                for warning in results['warnings']:
                    self.stdout.write(f"  ⚠ {warning}")
            
        except Exception as e:

            
            pass
            self.stdout.write(
                self.style.ERROR(f"Import failed: {str(e)}")
            )
            raise