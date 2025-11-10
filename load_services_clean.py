#!/usr/bin/env python
"""
Standalone script to load predefined services, with option to delete existing ones first.
Usage: 
  python load_services_clean.py --delete-existing --all
  python load_services_clean.py --delete-existing --tenant kk_company
"""

import os
import sys
import argparse
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from decimal import Decimal
from django_tenants.utils import schema_context
from billing.models import Service
from company.models import Company

def load_services_for_tenant(tenant_schema, delete_existing=False):
    """Load predefined services into a specific tenant schema."""
    
    predefined_services = [
        {
            'service_code': 'SVC001',
            'name': 'Lost VIP ID Card Replacement',
            'category': 'id_cards',
            'default_price': Decimal('10.00'),
            'description': 'Replacement fee for lost VIP ID card',
            'is_active': True
        },
        {
            'service_code': 'SVC002',
            'name': 'Lost Worker ID Card Replacement',
            'category': 'id_cards',
            'default_price': Decimal('10.00'),
            'description': 'Replacement fee for lost Worker ID card',
            'is_active': True
        },
        {
            'service_code': 'SVC003',
            'name': 'VIP ID Card Printing',
            'category': 'id_cards',
            'default_price': Decimal('5.00'),
            'description': 'Printing fee for new VIP ID card',
            'is_active': True
        },
        {
            'service_code': 'SVC004',
            'name': 'Worker ID Card Printing',
            'category': 'id_cards',
            'default_price': Decimal('2.00'),
            'description': 'Printing fee for new Worker ID card',
            'is_active': True
        },
        {
            'service_code': 'SVC005',
            'name': '1 Month Visa',
            'category': 'visas',
            'default_price': Decimal('55.00'),
            'description': '1 Month visa service fee',
            'is_active': True
        },
        {
            'service_code': 'SVC006',
            'name': '1 Year Visa',
            'category': 'visas',
            'default_price': Decimal('300.00'),
            'description': '1 Year visa service fee',
            'is_active': True
        },
        {
            'service_code': 'SVC007',
            'name': '3 Months Visa',
            'category': 'visas',
            'default_price': Decimal('85.00'),
            'description': '3 Months visa service fee',
            'is_active': True
        },
        {
            'service_code': 'SVC008',
            'name': '6 Months Visa',
            'category': 'visas',
            'default_price': Decimal('165.00'),
            'description': '6 Months visa service fee',
            'is_active': True
        },
    ]
    
    print(f"\n{'='*60}")
    print(f"Loading Services for Tenant: {tenant_schema}")
    print(f"{'='*60}\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    deleted_count = 0
    
    with schema_context(tenant_schema):
        # Delete existing services if requested
        if delete_existing:
            existing_count = Service.objects.count()
            if existing_count > 0:
                Service.objects.all().delete()
                deleted_count = existing_count
                print(f"[x] Deleted {existing_count} existing services")
            else:
                print("[i] No existing services to delete")
        
        for service_data in predefined_services:
            try:
                service, created = Service.objects.update_or_create(
                    service_code=service_data['service_code'],
                    defaults={
                        'name': service_data['name'],
                        'category': service_data['category'],
                        'default_price': service_data['default_price'],
                        'description': service_data['description'],
                        'is_active': service_data['is_active']
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"[+] Created: {service_data['service_code']} - {service_data['name']} (${service_data['default_price']})")
                else:
                    updated_count += 1
                    print(f"[*] Updated: {service_data['service_code']} - {service_data['name']} (${service_data['default_price']})")
                    
            except Exception as e:

                    
                pass
                error_count += 1
                print(f"[!] Error with {service_data['service_code']}: {str(e)}")
        
        print(f"\n{'='*60}")
        print("Summary")
        print(f"{'='*60}")
        if delete_existing and deleted_count > 0:
            print(f"Deleted: {deleted_count} services")
        print(f"Created: {created_count} services")
        print(f"Updated: {updated_count} services") 
        print(f"Errors: {error_count} services")
        print(f"Total processed: {created_count + updated_count}/{len(predefined_services)}")
        
        # Display all services
        print(f"\n{'='*60}")
        print("All Services in Database")
        print(f"{'='*60}")
        
        all_services = Service.objects.all().order_by('service_code')
        if all_services.exists():
            print(f"{'Code':<10} {'Name':<35} {'Category':<15} {'Price':<10} {'Status':<10}")
            print("-"*85)
            for service in all_services:
                category_display = dict(Service.CATEGORY_CHOICES).get(service.category, service.category)
                status = "Active" if service.is_active else "Inactive"
                print(f"{service.service_code:<10} {service.name[:35]:<35} {category_display:<15} ${service.default_price:<10.2f} {status:<10}")
        else:
            print("No services found in database.")

def main():
    parser = argparse.ArgumentParser(description='Load predefined services into tenant schemas')
    parser.add_argument('--delete-existing', action='store_true', 
                       help='Delete existing services before loading new ones')
    parser.add_argument('--all', action='store_true', 
                       help='Load services into all tenant schemas')
    parser.add_argument('--tenant', type=str, 
                       help='Load services into specific tenant schema')
    
    args = parser.parse_args()
    
    if not args.all and not args.tenant:
        print("Error: Must specify either --all or --tenant <schema_name>")
        parser.print_help()
        sys.exit(1)
    
    # Get all tenants
    tenants = Company.objects.exclude(schema_name='public')
    
    if not tenants.exists():
        print("No tenants found in the system.")
        return
    
    if args.all:
        print(f"Loading services into all {tenants.count()} tenant(s)...")
        if args.delete_existing:
            print("WARNING: This will delete ALL existing services in ALL tenants!")
            confirm = 'yes'  # Auto-confirm for Docker setup
            print("Auto-confirming for Docker setup...")
            if confirm.lower() != 'yes':
                print("Operation cancelled.")
                return
        
        for tenant in tenants:
            try:
                load_services_for_tenant(tenant.schema_name, args.delete_existing)
            except Exception as e:
                print(f"\n[ERROR] Failed to load services for {tenant.schema_name}: {str(e)}")
    
    elif args.tenant:
        # Check if tenant exists
        try:
            tenant = tenants.get(schema_name=args.tenant)
        except Company.DoesNotExist:
            print(f"Error: Tenant '{args.tenant}' not found.")
            print("Available tenants:")
            for t in tenants:
                print(f"  - {t.schema_name}")
            sys.exit(1)
        
        if args.delete_existing:
            print(f"WARNING: This will delete ALL existing services in tenant '{args.tenant}'!")
            confirm = 'yes'  # Auto-confirm for Docker setup
            print("Auto-confirming for Docker setup...")
            if confirm.lower() != 'yes':
                print("Operation cancelled.")
                return
        
        load_services_for_tenant(tenant.schema_name, args.delete_existing)

if __name__ == "__main__":
    main()