from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils import timezone
from datetime import date, timedelta
import random

from hr.models import Employee
from cards.models import EmployeeIDCard


class Command(BaseCommand):
    help = 'Create 10 employee ID cards for print preview testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of employee ID cards to create (default: 10)',
        )
        parser.add_argument(
            '--status',
            type=str,
            default='approved',
            choices=['pending', 'approved', 'printed', 'active'],
            help='Status for the generated cards (default: approved)',
        )

    def handle(self, *args, **options):
        count = options['count']
        status = options['status']
        
        self.stdout.write(f"🆔 Creating {count} Employee ID Cards...")
        
        # Get employees without ID cards or with fewer than 2 cards
        employees = Employee.objects.annotate(
            card_count=models.Count('employee_id_cards')
        ).filter(
            card_count__lt=2
        ).order_by('?')[:count]
        
        if len(employees) < count:
            self.stdout.write(
                self.style.WARNING(
                    f"Only {len(employees)} employees available without existing cards. "
                    f"Creating cards for {len(employees)} employees."
                )
            )
        
        created_cards = []
        
        with transaction.atomic():
            for i, employee in enumerate(employees):
                # Create employee ID card
                card = EmployeeIDCard.objects.create(
                    employee=employee,
                    card_type=random.choice(['regular', 'temporary', 'contractor']),
                    status=status,
                    issue_date=date.today() if status in ['approved', 'printed', 'active'] else None,
                    expiry_date=date.today() + timedelta(days=365),  # 1 year validity
                    notes=f"Generated for testing - Employee {employee.employee_id}"
                )
                
                # Generate card number if status is approved or higher
                if status in ['approved', 'printed', 'active'] and not card.card_number:
                    card.card_number = f"EID{timezone.now().year}{str(employee.id).zfill(4)}"
                    card.save()
                
                created_cards.append(card)
                
                self.stdout.write(
                    f"  ✅ Created {card.get_card_type_display()} card for {employee.full_name} "
                    f"(ID: {employee.employee_id}) - Status: {card.get_status_display()}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Successfully created {len(created_cards)} Employee ID Cards!"
            )
        )
        
        # Provide URLs for testing
        if created_cards:
            card_ids = [str(card.id) for card in created_cards]
            print_preview_url = f"/cards/employee-id-cards/print-preview/?cards={','.join(card_ids)}"
            
            self.stdout.write("\n📋 Testing URLs:")
            self.stdout.write(f"   🖨️  Print Preview: http://localhost:8000{print_preview_url}")
            self.stdout.write(f"   📝 Employee Cards List: http://localhost:8000/cards/employee-id-cards/")
            
            self.stdout.write("\n📊 Card Details:")
            for card in created_cards:
                self.stdout.write(
                    f"   • {card.employee.full_name} ({card.employee.employee_id}) "
                    f"- {card.get_card_type_display()} - {card.get_status_display()}"
                    f"{' - ' + card.card_number if card.card_number else ''}"
                ) 