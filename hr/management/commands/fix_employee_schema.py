from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Remove unwanted columns from hr_employee table that exist in database but not in current model'
    
    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        # List of columns that should be removed (exist in DB but not in current model)
        columns_to_remove = [
            'marital_status',
            'department_id', 
            'position_id',
            'user_id',
            'supervisor_id',
            'created_by_id'
        ]
        
        # First, check what columns currently exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'hr_employee' 
            AND table_schema = current_schema()
            ORDER BY ordinal_position
        """)
        current_columns = [row[0] for row in cursor.fetchall()]
        
        self.stdout.write(f"Current columns in hr_employee: {current_columns}")
        
        # Remove each unwanted column if it exists
        for column in columns_to_remove:
            if column in current_columns:
                self.stdout.write(f"Removing column: {column}")
                try:
                    cursor.execute(f'ALTER TABLE hr_employee DROP COLUMN {column} CASCADE;')
                    self.stdout.write(self.style.SUCCESS(f'Successfully removed {column}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to remove {column}: {e}'))
            else:
                self.stdout.write(f"Column {column} not found, skipping")
        
        # Verify the final schema
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'hr_employee' 
            AND table_schema = current_schema()
            ORDER BY ordinal_position
        """)
        final_columns = [row[0] for row in cursor.fetchall()]
        
        self.stdout.write(f"\nFinal columns in hr_employee: {final_columns}")
        self.stdout.write(self.style.SUCCESS("Schema cleanup completed!"))