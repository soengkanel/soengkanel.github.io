from django.core.management.base import BaseCommand
from company.models import Group, Company
from datetime import date


class Command(BaseCommand):
    help = 'Create LYP group with KK and OSM companies'

    def handle(self, *args, **options):
        self.stdout.write('Creating LYP group and companies...')
        
        # Create or get the LYP group
        lyp_group, created = Group.objects.get_or_create(
            name='LYP',
            defaults={
                'description': 'LYP Group - Parent company managing multiple subsidiaries',
                'established_date': date(2020, 1, 1),  # You can adjust this date
                'headquarters': 'Malaysia',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'[OK] Created LYP group: {lyp_group.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[OK] LYP group already exists: {lyp_group.name}')
            )
        
        # Create KK company
        kk_company, created = Company.objects.get_or_create(
            name='KK',
            group=lyp_group,
            defaults={
                'company_type': 'corporation',
                'description': 'KK Corporation - Part of LYP Group',
                'established_date': date(2021, 1, 1),  # You can adjust this date
                'country': 'Malaysia',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'[OK] Created KK company: {kk_company.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[OK] KK company already exists: {kk_company.name}')
            )
        
        # Create OSM company
        osm_company, created = Company.objects.get_or_create(
            name='OSM',
            group=lyp_group,
            defaults={
                'company_type': 'corporation',
                'description': 'OSM Corporation - Part of LYP Group',
                'established_date': date(2021, 6, 1),  # You can adjust this date
                'country': 'Malaysia',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'[OK] Created OSM company: {osm_company.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[OK] OSM company already exists: {osm_company.name}')
            )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Group: {lyp_group.name}')
        self.stdout.write(f'  Companies: {lyp_group.total_companies} total')
        for company in lyp_group.companies.all():
            self.stdout.write(f'    - {company.name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Successfully created LYP group with KK and OSM companies!')) 