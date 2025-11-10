import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from user_management.models import UserRoleAssignment
import os
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Export all users to CSV file with their details'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output CSV file path (default: users_export_TIMESTAMP.csv)'
        )

    def handle(self, *args, **options):
        # Generate filename if not provided
        if options['output']:
            output_file = options['output']
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'users_export_{timestamp}.csv'
        
        # Get all users
        users = User.objects.all().order_by('id')
        
        # Define default passwords based on the setup_initial_access_control command
        default_passwords = {
            'admin': 'admin123',  # Common default
            'm1': 'manager123',
            'm2': 'manager123',
        }
        
        # Add u1-u15 users with default password
        for i in range(1, 16):
            default_passwords[f'u{i}'] = 'user123'
        
        # Create CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'ID', 
                'Username', 
                'Email', 
                'First Name', 
                'Last Name', 
                'Role',
                'Is Active',
                'Is Staff',
                'Is Superuser',
                'Default Password',
                'Date Joined'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            exported_count = 0
            
            for user in users:
                # Get user's role
                try:
                    role_assignment = UserRoleAssignment.objects.filter(user=user).first()
                    role_name = role_assignment.role.name if role_assignment else 'No Role'
                except:
                    role_name = 'No Role'
                
                # Get default password if it exists
                default_password = default_passwords.get(user.username, 'Password not in defaults')
                
                # Write user data
                writer.writerow({
                    'ID': user.id,
                    'Username': user.username,
                    'Email': user.email,
                    'First Name': user.first_name,
                    'Last Name': user.last_name,
                    'Role': role_name,
                    'Is Active': 'Yes' if user.is_active else 'No',
                    'Is Staff': 'Yes' if user.is_staff else 'No',
                    'Is Superuser': 'Yes' if user.is_superuser else 'No',
                    'Default Password': default_password,
                    'Date Joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else ''
                })
                
                exported_count += 1
                
                # Show progress
                self.stdout.write(f"Exported user: {user.username}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully exported {exported_count} users to {output_file}'
            )
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('EXPORT SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'Total Users Exported: {exported_count}')
        self.stdout.write(f'Output File: {output_file}')
        self.stdout.write(f'File Location: {os.path.abspath(output_file)}')
        self.stdout.write('\nNOTE: Passwords shown are only the default passwords from initial setup.')
        self.stdout.write('If users have changed their passwords, those cannot be recovered.')
        self.stdout.write('='*50)