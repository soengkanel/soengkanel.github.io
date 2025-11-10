from django.core.management.base import BaseCommand
from django.db import transaction
from company.models import Group, Company
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create mock data for groups and companies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--groups',
            type=int,
            default=5,
            help='Number of groups to create (default: 5)'
        )
        parser.add_argument(
            '--companies-per-group',
            type=int,
            default=3,
            help='Average number of companies per group (default: 3)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing groups and companies before creating new ones'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing groups and companies...')
            Company.objects.all().delete()
            Group.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data.'))

        groups_count = options['groups']
        companies_per_group = options['companies_per_group']

        self.stdout.write(f'Creating {groups_count} groups with approximately {companies_per_group} companies each...')

        group_names = [
            'Tech Holdings Group',
            'Global Manufacturing Corp',
            'Financial Services Alliance',
            'Healthcare Innovations Group',
            'Renewable Energy Consortium',
            'Retail & Commerce Group',
            'Transportation Solutions Group',
            'Media & Entertainment Corp',
            'Real Estate Development Group',
            'Education & Training Alliance'
        ]

        company_types = [choice[0] for choice in Company.COMPANY_TYPES]
        
        cities = [
            'Kuala Lumpur', 'Johor Bahru', 'Penang', 'Petaling Jaya',
            'Shah Alam', 'Ipoh', 'Seremban', 'Melaka', 'Kota Kinabalu',
            'Kuching', 'Cyberjaya', 'Putrajaya'
        ]

        states = [
            'Selangor', 'Kuala Lumpur', 'Johor', 'Penang', 'Perak',
            'Negeri Sembilan', 'Melaka', 'Sabah', 'Sarawak', 'Pahang'
        ]

        with transaction.atomic():
            groups_created = 0
            companies_created = 0

            for i in range(groups_count):
                # Create group
                group_name = group_names[i % len(group_names)]
                if i >= len(group_names):
                    group_name = f"{group_name} {i - len(group_names) + 2}"

                group = Group.objects.create(
                    name=group_name,
                    description=f"A leading {group_name.lower()} focused on innovation and growth.",
                    established_date=date.today() - timedelta(days=random.randint(365, 3650)),
                    headquarters=f"{random.choice(cities)}, Malaysia",
                    website=f"https://www.{group_name.lower().replace(' ', '').replace('&', 'and')}.com",
                    phone_number=f"+60{random.randint(10000000, 99999999)}",
                    email=f"info@{group_name.lower().replace(' ', '').replace('&', 'and')}.com",
                    is_active=random.choice([True, True, True, False])  # 75% chance of being active
                )
                groups_created += 1

                # Create companies for this group
                num_companies = random.randint(
                    max(1, companies_per_group - 2),
                    companies_per_group + 2
                )
                
                for j in range(num_companies):
                    company_suffixes = ['Sdn Bhd', 'Bhd', 'Technologies', 'Solutions', 'Services', 'Industries', 'Corp']
                    company_name = f"{group_name.split()[0]} {random.choice(company_suffixes)}"
                    if j > 0:
                        company_name = f"{group_name.split()[0]} {random.choice(company_suffixes)} {j + 1}"

                    city = random.choice(cities)
                    state = random.choice(states)

                    company = Company.objects.create(
                        name=company_name,
                        group=group,
                        company_type=random.choice(company_types),
                        registration_number=f"ROC{random.randint(100000000, 999999999)}",
                        tax_id=f"TAX{random.randint(1000000, 9999999)}",
                        description=f"{company_name} is a subsidiary of {group.name} specializing in innovative solutions.",
                        established_date=group.established_date + timedelta(days=random.randint(30, 1000)),
                        address=f"{random.randint(1, 999)} Jalan {random.choice(['Ampang', 'Bukit Bintang', 'Raja Chulan', 'Tun Razak', 'Sultan Ismail'])}",
                        city=city,
                        state_province=state,
                        postal_code=f"{random.randint(10000, 99999)}",
                        country='Malaysia',
                        website=f"https://www.{company_name.lower().replace(' ', '').replace('&', 'and')}.com",
                        phone_number=f"+60{random.randint(10000000, 99999999)}",
                        email=f"contact@{company_name.lower().replace(' ', '').replace('&', 'and')}.com",
                        is_active=random.choice([True, True, True, True, False])  # 80% chance of being active
                    )
                    companies_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {groups_created} groups and {companies_created} companies.'
            )
        ) 