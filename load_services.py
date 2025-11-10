#!/usr/bin/env python
"""
Standalone script to load predefined services into specific tenant schema.
Usage: python load_services.py
"""

import os
import sys
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
    
    with schema_context(tenant_schema):
        # Delete existing services if requested
        if delete_existing:
            existing_count = Service.objects.count()
            if existing_count > 0:
                Service.objects.all().delete()
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
    # Get all tenants
    tenants = Company.objects.exclude(schema_name='public')
    
    if not tenants.exists():
        print("No tenants found in the system.")
        return
    
    print("\nAvailable tenants:")
    for i, tenant in enumerate(tenants, 1):
        print(f"{i}. {tenant.schema_name} - {tenant.name}")
    
    # Ask about deleting existing services
    while True:
        try:
            delete_choice = input("\nDelete existing services before loading new ones? (y/n): ").strip().lower()
            if delete_choice in ['y', 'yes']:
                delete_existing = True
                break
            elif delete_choice in ['n', 'no']:
                delete_existing = False
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            sys.exit(0)
    
    # Ask user to select tenant
    while True:
        try:
            choice = input("\nSelect tenant number (or 'all' for all tenants): ").strip()
            
            if choice.lower() == 'all':
                for tenant in tenants:
                    try:
                        load_services_for_tenant(tenant.schema_name, delete_existing)
                    except Exception as e:
                        print(f"\n[ERROR] Failed to load services for {tenant.schema_name}: {str(e)}")
                break
            else:
                tenant_index = int(choice) - 1
                if 0 <= tenant_index < len(tenants):
                    selected_tenant = tenants[tenant_index]
                    load_services_for_tenant(selected_tenant.schema_name, delete_existing)
                    break
                else:
                    print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'all'.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()