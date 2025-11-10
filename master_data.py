#!/usr/bin/env python3
"""
Master Data Script - Creates sample data for GuanYu System
Works with multi-tenant setup
Creates: Zone 3H, 20 Buildings, 20 Floors per building, HR Department, and Worker Positions
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from company.models import Company

User = get_user_model()

def create_master_data(schema_name=None):
    """Create master data for a specific tenant or first available tenant"""
    
    print("\n" + "=" * 70)
    print("CREATING SAMPLE MASTER DATA")
    print("=" * 70)
    
    # Get tenant
    if schema_name:
        tenant = Company.objects.get(schema_name=schema_name)
    else:
        tenant = Company.objects.first()
    
    if not tenant:
        print("No tenants found. Please create a tenant first.")
        return
    
    print(f"Tenant: {tenant.name} (schema: {tenant.schema_name})")
    
    # Set the schema
    connection.set_schema(tenant.schema_name)
    
    # Import models after setting schema
    from zone.models import Zone, Building, Floor, Department, Position
    
    # Get system user
    system_user = User.objects.filter(is_superuser=True).first()
    if not system_user:
        system_user = User.objects.filter(is_staff=True).first()
    if not system_user:
        system_user = User.objects.first()
    
    if system_user:
        print(f"Using user: {system_user.username}")
    else:
        print("No user found. Creating admin user...")
        system_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    print("-" * 70)
    
    # Statistics
    stats = {
        'zones': 0,
        'buildings': 0,
        'floors': 0,
        'departments': 0,
        'positions': 0
    }
    
    try:
        # ==================== CREATE ZONE 3H ====================
        print("\n[1] Creating Zone 3H...")
        
        zone, created = Zone.objects.get_or_create(
            name='3H',
            defaults={
                'description': 'Zone 3H - Main operational zone',
                'address': 'Zone 3H, Industrial Area',
                'is_active': True,
                'created_by': system_user
            }
        )
        
        if created:
            print(f"   Created Zone: {zone.name}")
            stats['zones'] += 1
        else:
            print(f"   Zone already exists: {zone.name}")
        
        # ==================== CREATE 20 BUILDINGS ====================
        print("\n[2] Creating 20 Buildings (B1-B20)...")
        
        for i in range(1, 21):
            building_name = f"B{i}"
            building_code = f"3H-B{i:02d}"
            
            building, created = Building.objects.get_or_create(
                name=building_name,
                defaults={
                    'code': building_code,
                    'address': f"Building {building_name}, Zone 3H",
                    'total_floors': 20,
                    'zone': zone,
                    'description': f"Building {building_name} in Zone 3H",
                    'is_active': True,
                    'created_by': system_user
                }
            )
            
            if created:
                print(f"   Created Building: {building_name}")
                stats['buildings'] += 1
                
                # Create 20 floors for this building
                for floor_num in range(1, 21):
                    floor_name = f"F{floor_num}"
                    
                    floor, floor_created = Floor.objects.get_or_create(
                        building=building,
                        floor_number=floor_num,
                        defaults={
                            'name': floor_name,
                            'description': f"Floor {floor_num} in {building_name}",
                            'is_active': True,
                            'created_by': system_user
                        }
                    )
                    
                    if floor_created:
                        stats['floors'] += 1
            else:
                print(f"   Building exists: {building_name}")
        
        print(f"   Total floors created: {stats['floors']}")
        
        # ==================== CREATE HR DEPARTMENT ====================
        print("\n[3] Creating HR Department...")
        
        hr_department, created = Department.objects.get_or_create(
            code='HR',
            defaults={
                'name': 'Human Resources',
                'description': 'Human Resources Department',
                'is_active': True,
                'created_by': system_user
            }
        )
        
        if created:
            print(f"   Created Department: {hr_department.name}")
            stats['departments'] += 1
        else:
            print(f"   Department exists: {hr_department.name}")
        
        # ==================== CREATE WORKER POSITIONS ====================
        print("\n[4] Creating Worker Positions...")
        
        positions = [
            ('HR001', 'Staff Online', 3),
            ('HR002', 'Staff Cleaner', 4),
            ('HR003', 'Staff Bodyguard', 3),
            ('HR004', 'Driver', 3),
            ('HR005', 'Translator', 2),
            ('HR006', 'Staff Canteen', 4),
            ('HR007', 'Other Staff', 4),
        ]
        
        for code, name, level in positions:
            position, created = Position.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'department': hr_department,
                    'level': level,
                    'description': f'{name} position',
                    'created_by': system_user
                }
            )
            
            if created:
                print(f"   Created: {code} - {name}")
                stats['positions'] += 1
            else:
                print(f"   Exists: {code} - {name}")
        
        # ==================== SUMMARY ====================
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Zones created:       {stats['zones']}")
        print(f"Buildings created:   {stats['buildings']}")
        print(f"Floors created:      {stats['floors']}")
        print(f"Departments created: {stats['departments']}") 
        print(f"Positions created:   {stats['positions']}")
        
        print("\nData Structure:")
        print(f"  Zone 3H")
        print(f"  - {Building.objects.filter(zone=zone).count()} Buildings (B1-B20)")
        print(f"  - {Floor.objects.filter(building__zone=zone).count()} Total Floors")
        print(f"  - HR Department")
        for pos in Position.objects.filter(department=hr_department).order_by('code'):
            print(f"      - {pos.code}: {pos.name}")
        
        print("\nDone!")
        
    except Exception as e:

        
        pass
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Reset to public schema
        connection.set_schema_to_public()

if __name__ == '__main__':
    # Get schema name from command line if provided
    schema = sys.argv[1] if len(sys.argv) > 1 else None
    create_master_data(schema)