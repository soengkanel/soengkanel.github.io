#!/usr/bin/env python
"""
Populate default suggestion categories
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from company.models import Company
from suggestions.models import SuggestionCategory

def populate_categories():
    """Create default suggestion categories"""

    categories = [
        {
            'name': 'Workplace Improvement',
            'description': 'Suggestions for improving the workplace environment',
            'icon': 'bi-building',
            'color': 'primary',
            'order': 1
        },
        {
            'name': 'Process Improvement',
            'description': 'Ideas to improve work processes and efficiency',
            'icon': 'bi-gear',
            'color': 'info',
            'order': 2
        },
        {
            'name': 'Technology & Tools',
            'description': 'Suggestions for new tools or technology improvements',
            'icon': 'bi-laptop',
            'color': 'success',
            'order': 3
        },
        {
            'name': 'Employee Benefits',
            'description': 'Ideas for employee benefits and perks',
            'icon': 'bi-gift',
            'color': 'warning',
            'order': 4
        },
        {
            'name': 'Training & Development',
            'description': 'Suggestions for training programs and skill development',
            'icon': 'bi-book',
            'color': 'danger',
            'order': 5
        },
        {
            'name': 'Communication',
            'description': 'Ideas to improve internal communication',
            'icon': 'bi-chat-dots',
            'color': 'secondary',
            'order': 6
        },
        {
            'name': 'Health & Safety',
            'description': 'Health and safety related suggestions',
            'icon': 'bi-shield-check',
            'color': 'success',
            'order': 7
        },
        {
            'name': 'Cost Saving',
            'description': 'Ideas to reduce costs and improve efficiency',
            'icon': 'bi-piggy-bank',
            'color': 'primary',
            'order': 8
        },
        {
            'name': 'Customer Service',
            'description': 'Suggestions to improve customer service',
            'icon': 'bi-people',
            'color': 'info',
            'order': 9
        },
        {
            'name': 'Other',
            'description': 'General suggestions that don\'t fit other categories',
            'icon': 'bi-lightbulb',
            'color': 'secondary',
            'order': 10
        },
    ]

    created_count = 0
    updated_count = 0

    for cat_data in categories:
        category, created = SuggestionCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon'],
                'color': cat_data['color'],
                'order': cat_data['order'],
                'is_active': True
            }
        )

        if created:
            created_count += 1
            print(f"[+] Created category: {category.name}")
        else:
            updated_count += 1
            print(f"[-] Category already exists: {category.name}")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Created: {created_count} categories")
    print(f"  Already existed: {updated_count} categories")
    print(f"  Total: {SuggestionCategory.objects.count()} categories")
    print(f"{'='*60}")

if __name__ == '__main__':
    # Get tenant from command line or use default
    if len(sys.argv) > 1:
        tenant_schema = sys.argv[1]
    else:
        # List available tenants
        tenants = Company.objects.exclude(schema_name='public').all()
        print("Available tenants:")
        for idx, tenant in enumerate(tenants, 1):
            print(f"  {idx}. {tenant.schema_name} - {tenant.name}")

        if not tenants:
            print("No tenants found!")
            sys.exit(1)

        print("\nEnter tenant number or schema name:")
        choice = input("> ").strip()

        # Check if it's a number
        if choice.isdigit():
            tenant_idx = int(choice) - 1
            if 0 <= tenant_idx < len(tenants):
                tenant_schema = tenants[tenant_idx].schema_name
            else:
                print("Invalid tenant number!")
                sys.exit(1)
        else:
            tenant_schema = choice

    print(f"\nPopulating categories for tenant: {tenant_schema}")
    print("="*60)

    with schema_context(tenant_schema):
        populate_categories()
