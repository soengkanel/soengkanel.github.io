from django.core.management.base import BaseCommand
from hr.models import Employee
import os

class Command(BaseCommand):
    help = 'Fix employees with missing photo files by clearing the photo field'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually fix the issues (clear photo fields for missing files)',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_issues = options['fix']
        
        if not dry_run and not fix_issues:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify --dry-run to see issues or --fix to fix them'
                )
            )
            return
        
        self.stdout.write('Checking for employees with missing photo files...\n')
        
        issues_found = 0
        fixed_count = 0
        
        for employee in Employee.objects.exclude(photo__isnull=True).exclude(photo=''):
            if employee.photo and employee.photo.name:
                try:
                    # Check if file exists
                    if hasattr(employee.photo, 'path'):
                        file_path = employee.photo.path
                        if not os.path.exists(file_path):
                            issues_found += 1
                            self.stdout.write(
                                f"❌ Employee {employee.employee_id} ({employee.full_name}): "
                                f"Missing photo file: {file_path}"
                            )
                            
                            if fix_issues:
                                # Clear the photo field
                                employee.photo = None
                                employee.save(update_fields=['photo'])
                                fixed_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f"   ✅ Cleared photo field for {employee.employee_id}")
                                )
                    else:
                        issues_found += 1
                        self.stdout.write(
                            f"❌ Employee {employee.employee_id} ({employee.full_name}): "
                            f"Photo field has no path attribute: {employee.photo.name}"
                        )
                        
                        if fix_issues:
                            # Clear the photo field
                            employee.photo = None
                            employee.save(update_fields=['photo'])
                            fixed_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"   ✅ Cleared photo field for {employee.employee_id}")
                            )
                            
                except (ValueError, AttributeError, OSError) as e:

                            
                    pass
                    issues_found += 1
                    self.stdout.write(
                        f"❌ Employee {employee.employee_id} ({employee.full_name}): "
                        f"Error accessing photo: {str(e)}"
                    )
                    
                    if fix_issues:
                        # Clear the photo field
                        employee.photo = None
                        employee.save(update_fields=['photo'])
                        fixed_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"   ✅ Cleared photo field for {employee.employee_id}")
                        )
        
        # Summary
        if issues_found == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ No missing photo files found!'))
        else:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'\n⚠️  Found {issues_found} employees with missing photo files.')
                )
                self.stdout.write(
                    self.style.WARNING('Run with --fix to clear the photo fields for these employees.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Fixed {fixed_count} out of {issues_found} issues.')
                )
                
        self.stdout.write('\nDone!')