from django.core.management.base import BaseCommand
from django.utils import timezone
from leave.models import Holiday
from datetime import date


class Command(BaseCommand):
    help = 'Populate Cambodia public holidays for 2025'

    def handle(self, *args, **kwargs):
        year = 2025

        # Cambodia Public Holidays 2025
        holidays_data = [
            {
                'name': 'International New Year Day',
                'date': date(2025, 1, 1),
                'year': 2025,
                'is_optional': False,
                'description': 'International New Year celebration',
            },
            {
                'name': 'Victory Day over Genocide',
                'date': date(2025, 1, 7),
                'year': 2025,
                'is_optional': False,
                'description': 'Victory over the Khmer Rouge regime in 1979',
            },
            {
                'name': 'Khmer New Year Day 1',
                'date': date(2025, 4, 14),
                'year': 2025,
                'is_optional': False,
                'description': 'Khmer New Year - Maha Songkran',
            },
            {
                'name': 'Khmer New Year Day 2',
                'date': date(2025, 4, 15),
                'year': 2025,
                'is_optional': False,
                'description': 'Khmer New Year - Virak Wanabat',
            },
            {
                'name': 'Khmer New Year Day 3',
                'date': date(2025, 4, 16),
                'year': 2025,
                'is_optional': False,
                'description': 'Khmer New Year - Virak Loeurng Sak',
            },
            {
                'name': 'International Labor Day',
                'date': date(2025, 5, 1),
                'year': 2025,
                'is_optional': False,
                'description': 'International Workers Day',
            },
            {
                'name': 'Royal Ploughing Ceremony',
                'date': date(2025, 5, 8),
                'year': 2025,
                'is_optional': False,
                'description': 'Traditional royal ceremony to mark the beginning of the rice-growing season',
            },
            {
                'name': 'Birthday of His Majesty Preah Bat Samdech Preah Boromneath NORODOM SIHAMONI, King of Cambodia',
                'date': date(2025, 5, 13),
                'year': 2025,
                'is_optional': False,
                'description': 'Birthday of King Norodom Sihamoni',
            },
            {
                'name': 'Birthday of His Majesty Preah Bat Samdech Preah Boromneath NORODOM SIHAMONI (Day 2)',
                'date': date(2025, 5, 14),
                'year': 2025,
                'is_optional': False,
                'description': 'Birthday of King Norodom Sihamoni - Day 2',
            },
            {
                'name': 'Birthday of His Majesty Preah Bat Samdech Preah Boromneath NORODOM SIHAMONI (Day 3)',
                'date': date(2025, 5, 15),
                'year': 2025,
                'is_optional': False,
                'description': 'Birthday of King Norodom Sihamoni - Day 3',
            },
            {
                'name': 'Visak Bochea Day',
                'date': date(2025, 5, 12),
                'year': 2025,
                'is_optional': False,
                'description': 'Buddha\'s Birthday, Enlightenment and Passing',
            },
            {
                'name': 'Birthday of Samdech Preah Moha Ksatrey NORODOM MONINEATH SIHANOUK, Queen-Mother of Cambodia',
                'date': date(2025, 6, 18),
                'year': 2025,
                'is_optional': False,
                'description': 'Birthday of Queen Mother Norodom Monineath',
            },
            {
                'name': 'Constitution Day',
                'date': date(2025, 9, 24),
                'year': 2025,
                'is_optional': False,
                'description': 'Anniversary of the Cambodian Constitution',
            },
            {
                'name': 'Pchum Ben Day 1',
                'date': date(2025, 10, 4),
                'year': 2025,
                'is_optional': False,
                'description': 'Ancestors Day - Pchum Ben Festival Day 1',
            },
            {
                'name': 'Pchum Ben Day 2',
                'date': date(2025, 10, 5),
                'year': 2025,
                'is_optional': False,
                'description': 'Ancestors Day - Pchum Ben Festival Day 2',
            },
            {
                'name': 'Pchum Ben Day 3',
                'date': date(2025, 10, 6),
                'year': 2025,
                'is_optional': False,
                'description': 'Ancestors Day - Pchum Ben Festival Day 3',
            },
            {
                'name': 'Commemoration Day of the Death of King-Father NORODOM SIHANOUK',
                'date': date(2025, 10, 15),
                'year': 2025,
                'is_optional': False,
                'description': 'Memorial Day for King Father Norodom Sihanouk',
            },
            {
                'name': 'Independence Day',
                'date': date(2025, 11, 9),
                'year': 2025,
                'is_optional': False,
                'description': 'Cambodia Independence Day from France (1953)',
            },
            {
                'name': 'Water Festival (Bon Om Touk) Day 1',
                'date': date(2025, 11, 5),
                'year': 2025,
                'is_optional': False,
                'description': 'Water Festival - Boat Racing Festival Day 1',
            },
            {
                'name': 'Water Festival (Bon Om Touk) Day 2',
                'date': date(2025, 11, 6),
                'year': 2025,
                'is_optional': False,
                'description': 'Water Festival - Boat Racing Festival Day 2',
            },
            {
                'name': 'Water Festival (Bon Om Touk) Day 3',
                'date': date(2025, 11, 7),
                'year': 2025,
                'is_optional': False,
                'description': 'Water Festival - Boat Racing Festival Day 3',
            },
            {
                'name': 'International Human Rights Day',
                'date': date(2025, 12, 10),
                'year': 2025,
                'is_optional': False,
                'description': 'International Human Rights Day',
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for holiday_data in holidays_data:
            try:
                holiday, created = Holiday.objects.update_or_create(
                    name=holiday_data['name'],
                    date=holiday_data['date'],
                    year=holiday_data['year'],
                    defaults={
                        'is_optional': holiday_data['is_optional'],
                        'description': holiday_data['description'],
                        'applies_to_all': True,
                        'regions': '',
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[+] Created: {holiday.name} on {holiday.date}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'[*] Updated: {holiday.name} on {holiday.date}')
                    )
            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[!] Error creating {holiday_data["name"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Summary ==='
                f'\nCreated: {created_count}'
                f'\nUpdated: {updated_count}'
                f'\nSkipped: {skipped_count}'
                f'\nTotal: {len(holidays_data)}'
            )
        )
