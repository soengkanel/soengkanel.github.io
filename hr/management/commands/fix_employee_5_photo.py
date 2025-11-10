from django.core.management.base import BaseCommand
from hr.models import Employee
import os

class Command(BaseCommand):
    help = 'Fix the specific photo issue for employee 5'
    
    def handle(self, *args, **options):
        try:
            employee = Employee.objects.get(pk=5)
            self.stdout.write(f'Found employee: {employee.employee_id} - {employee.full_name}')
            
            if employee.photo and employee.photo.name:
                self.stdout.write(f'Current photo: {employee.photo.name}')
                
                # Check if file exists
                file_exists = False
                try:
                    if hasattr(employee.photo, 'path'):
                        file_path = employee.photo.path
                        file_exists = os.path.exists(file_path)
                        self.stdout.write(f'Photo path: {file_path}')
                        self.stdout.write(f'File exists: {file_exists}')
                except (AttributeError, OSError, ValueError) as e:
                    self.stdout.write(f'Error accessing photo path: {e}')
                
                if not file_exists:
                    # Clear the photo field
                    self.stdout.write('Clearing corrupted photo reference...')
                    employee.photo = None
                    employee.save(update_fields=['photo'])
                    self.stdout.write(self.style.SUCCESS('✅ Photo field cleared successfully'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ Photo file exists, no action needed'))
            else:
                self.stdout.write('Employee has no photo reference')
                
        except Employee.DoesNotExist:

                
            pass
            self.stdout.write(self.style.ERROR('❌ Employee with ID 5 not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))