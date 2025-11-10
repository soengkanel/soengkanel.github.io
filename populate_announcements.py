#!/usr/bin/env python
"""
Populate sample announcements for testing
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from django.utils import timezone
from company.models import Company
from announcements.models import Announcement
from django.contrib.auth.models import User


def populate_announcements():
    """Create sample announcements"""

    announcements_data = [
        {
            'title': 'Welcome to the New Announcement System!',
            'content': '''We are excited to introduce our new company announcement system!

This platform will help us keep everyone informed about important company news, updates, and events.

Features include:
- Real-time notifications
- Priority levels for urgent announcements
- Comment and discussion capabilities
- Acknowledgment tracking for important notices

Please check this page regularly for updates!''',
            'summary': 'New announcement system launched with enhanced features for better communication',
            'priority': 'high',
            'is_pinned': True,
            'target_audience': 'all',
        },
        {
            'title': 'Upcoming Company Holiday - End of Year Break',
            'content': '''Dear Team,

Please note that the company will be closed for the end-of-year holidays from December 25th to January 1st.

The office will reopen on January 2nd. All urgent matters during this period should be directed to the emergency contact provided in your handbook.

Wishing everyone a wonderful holiday season!''',
            'summary': 'Company closure for end-of-year holidays announced',
            'priority': 'normal',
            'target_audience': 'all',
            'expiry_date': timezone.now() + timedelta(days=60),
        },
        {
            'title': 'New Employee Benefits Program',
            'content': '''We are pleased to announce enhancements to our employee benefits program!

Starting next month, all employees will have access to:
- Enhanced health insurance coverage
- Flexible work arrangements
- Professional development allowance ($1,000/year)
- Wellness program membership

More details will be shared in individual meetings with HR next week.''',
            'summary': 'Enhanced employee benefits program with health, flexibility, and development perks',
            'priority': 'high',
            'target_audience': 'all',
            'require_acknowledgment': True,
        },
        {
            'title': 'IT System Maintenance This Weekend',
            'content': '''IMPORTANT: Scheduled IT maintenance this Saturday

Our IT systems will undergo scheduled maintenance this Saturday from 10 PM to 2 AM.

During this time:
- Email services may be intermittent
- VPN access will be unavailable
- Internal systems will be offline

Please plan accordingly and save your work before the maintenance window.

Thank you for your understanding.''',
            'summary': 'Scheduled IT maintenance will affect systems this weekend',
            'priority': 'urgent',
            'target_audience': 'all',
            'expiry_date': timezone.now() + timedelta(days=7),
        },
        {
            'title': 'Team Building Event Next Month',
            'content': '''Save the date for our annual team building event!

When: Next month (exact date TBA)
Where: Riverside Convention Center
Activities: Team challenges, workshops, and networking

This is a great opportunity to connect with colleagues across departments. More details coming soon!

RSVP will be required - watch for the sign-up link.''',
            'summary': 'Annual team building event scheduled for next month',
            'priority': 'normal',
            'target_audience': 'all',
        },
    ]

    created_count = 0
    try:
        # Try to get the first superuser
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("Warning: No superuser found. Creating announcements without created_by user.")
    except:
        admin_user = None

    for data in announcements_data:
        announcement, created = Announcement.objects.get_or_create(
            title=data['title'],
            defaults={
                **data,
                'created_by': admin_user,
                'publish_date': timezone.now(),
                'is_active': True,
            }
        )

        if created:
            created_count += 1
            print(f"[+] Created: {announcement.title}")
        else:
            print(f"[-] Already exists: {announcement.title}")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Created: {created_count} announcements")
    print(f"  Already existed: {len(announcements_data) - created_count} announcements")
    print(f"  Total: {Announcement.objects.count()} announcements")
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

    print(f"\nPopulating announcements for tenant: {tenant_schema}")
    print("="*60)

    with schema_context(tenant_schema):
        populate_announcements()
