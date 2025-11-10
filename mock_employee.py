#!/usr/bin/env python
"""
Mock Employee Data Generator for NextHR
Run this script with: python mock_employee.py
"""

import os
import sys
import django
from datetime import date
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction, connection

def create_mock_employees():
    """Create 10 mock employees with user accounts"""

    # Reset any bad database state
    try:
        connection.close()
    except:
        pass

    employees_data = [
        {
            'username': 'lim.theara',
            'employee_id': '200070',
            'first_name': 'Lim',
            'last_name': 'Theara',
            'email': 'lim.theara@company.com',
            'department': 'Structural Design',
            'position': 'Structural Design Director',
            'salary': 1500.00,
        },
        {
            'username': 'sarah.johnson',
            'employee_id': '200071',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@company.com',
            'department': 'Human Resources',
            'position': 'HR Manager',
            'salary': 2000.00,
        },
        {
            'username': 'michael.davis',
            'employee_id': '200072',
            'first_name': 'Michael',
            'last_name': 'Davis',
            'email': 'michael.davis@company.com',
            'department': 'Finance',
            'position': 'Finance Director',
            'salary': 2500.00,
        },
        {
            'username': 'emily.wilson',
            'employee_id': '200073',
            'first_name': 'Emily',
            'last_name': 'Wilson',
            'email': 'emily.wilson@company.com',
            'department': 'Marketing',
            'position': 'Marketing Executive',
            'salary': 1200.00,
        },
        {
            'username': 'david.brown',
            'employee_id': '200074',
            'first_name': 'David',
            'last_name': 'Brown',
            'email': 'david.brown@company.com',
            'department': 'Information Technology',
            'position': 'Senior Developer',
            'salary': 1800.00,
        },
        {
            'username': 'sophea.chan',
            'employee_id': '200075',
            'first_name': 'Sophea',
            'last_name': 'Chan',
            'email': 'sophea.chan@company.com',
            'department': 'Operations',
            'position': 'Operations Coordinator',
            'salary': 800.00,
        },
        {
            'username': 'visal.sok',
            'employee_id': '200076',
            'first_name': 'Visal',
            'last_name': 'Sok',
            'email': 'visal.sok@company.com',
            'department': 'Information Technology',
            'position': 'Junior Developer',
            'salary': 1000.00,
        },
        {
            'username': 'jennifer.martinez',
            'employee_id': '200077',
            'first_name': 'Jennifer',
            'last_name': 'Martinez',
            'email': 'jennifer.martinez@company.com',
            'department': 'Human Resources',
            'position': 'HR Specialist',
            'salary': 1600.00,
        },
        {
            'username': 'robert.taylor',
            'employee_id': '200078',
            'first_name': 'Robert',
            'last_name': 'Taylor',
            'email': 'robert.taylor@company.com',
            'department': 'Operations',
            'position': 'Operations Manager',
            'salary': 3000.00,
        },
        {
            'username': 'makara.ly',
            'employee_id': '200079',
            'first_name': 'Makara',
            'last_name': 'Ly',
            'email': 'makara.ly@company.com',
            'department': 'Finance',
            'position': 'Junior Accountant',
            'salary': 600.00,
        }
    ]

    print("="*60)
    print(" NextHR - Mock Employee Data Generator")
    print("="*60)
    print()

    created_count = 0
    updated_count = 0
    failed_count = 0

    # Process each employee without transaction wrapping
    for emp_data in employees_data:
        try:
                username = emp_data['username']

                # Create or update Django user
                user, user_created = User.objects.update_or_create(
                    username=username,
                    defaults={
                        'first_name': emp_data['first_name'],
                        'last_name': emp_data['last_name'],
                        'email': emp_data['email'],
                        'is_active': True,
                        'is_staff': False,
                    }
                )

                # Set password for new users
                if user_created:
                    user.set_password('password123')
                    user.save()
                    created_count += 1
                    print(f"[+] Created user: {username:<20} - {emp_data['first_name']} {emp_data['last_name']}")
                else:
                    # Update password for existing users
                    user.set_password('password123')
                    user.save()
                    updated_count += 1
                    print(f"[*] Updated user: {username:<20} - {emp_data['first_name']} {emp_data['last_name']}")

                # Try to create HR employee if the model is available
                try:
                    from hr.models import Employee, Department, Position

                    # Try to find or create department
                    dept = None
                    try:
                        dept, _ = Department.objects.get_or_create(
                            name=emp_data['department'],
                            defaults={'code': emp_data['department'][:3].upper()}
                        )
                    except:
                        pass

                    # Try to find or create position
                    pos = None
                    try:
                        pos, _ = Position.objects.get_or_create(
                            name=emp_data['position'],
                            defaults={
                                'code': emp_data['position'][:5].upper(),
                                'department': dept,
                                'level': 1
                            }
                        )
                    except:
                        pass

                    # Create employee record
                    Employee.objects.update_or_create(
                        employee_id=emp_data['employee_id'],
                        defaults={
                            'user': user,
                            'first_name': emp_data['first_name'],
                            'last_name': emp_data['last_name'],
                            'email': emp_data['email'],
                            'gender': 'M' if emp_data['first_name'] in ['Lim', 'Michael', 'David', 'Visal', 'Robert', 'Makara'] else 'F',
                            'nationality': 'KH' if emp_data['first_name'] in ['Lim', 'Sophea', 'Visal', 'Makara'] else 'US',
                            'phone_number': f'+8551234{emp_data["employee_id"][-4:]}',
                            'address': f'{emp_data["employee_id"][-3:]} Main Street, Phnom Penh',
                            'emergency_contact_name': f'Emergency Contact for {emp_data["first_name"]}',
                            'emergency_contact_phone': f'+8559876{emp_data["employee_id"][-4:]}',
                            'date_of_birth': date(1990, 1, 1),
                            'hire_date': date(2020, 1, 1),
                            'department': dept,
                            'position': pos,
                            'employment_status': 'active',
                            'salary': Decimal(str(emp_data['salary'])),
                            'work_location': 'Head Office',
                        }
                    )
                    print(f"  |-- Employee record created: {emp_data['employee_id']}")
                except ImportError:
                    # HR models not available, skip employee creation
                    pass
                except Exception as e:
                    # Skip if employee table doesn't exist
                    pass
        except Exception as e:
            failed_count += 1
            print(f"[-] Failed to process {emp_data.get('username', 'unknown')}: {str(e)[:50]}")
            # Reset connection on error
            try:
                connection.close()
            except:
                pass

    print()
    print("="*60)
    print(f" Summary")
    print("="*60)
    print(f"  * Users created: {created_count}")
    print(f"  * Users updated: {updated_count}")
    print(f"  * Failed: {failed_count}")
    print(f"  * Total processed: {created_count + updated_count}")
    print()
    print(" Login Credentials:")
    print("-"*60)
    print("  Username format: firstname.lastname")
    print("  Password: password123")
    print()
    print(" Example logins:")
    for i, emp in enumerate(employees_data[:3], 1):
        print(f"  {i}. {emp['username']:<20} / password123")
    print()
    print("="*60)
    print(" [SUCCESS] Mock data generation completed successfully!")
    print("="*60)


if __name__ == '__main__':
    try:
        create_mock_employees()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        print("Please make sure Django is properly configured")
        sys.exit(1)