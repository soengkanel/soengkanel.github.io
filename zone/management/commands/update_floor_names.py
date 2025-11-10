from django.core.management.base import BaseCommand
from zone.models import Floor


class Command(BaseCommand):
    help = 'Update floor names to F{number} format (F1, F2, F3, etc.)'

    def handle(self, *args, **options):
        floors = Floor.objects.all()
        updated_count = 0
        
        self.stdout.write("Updating floor names to F{number} format...")
        self.stdout.write("-" * 50)
        
        for floor in floors:
            # Generate new name based on floor number - just F{number}
            new_name = f"F{floor.floor_number}"
            
            # Always update to ensure we have the correct format
            old_name = floor.name
            floor.name = new_name
            floor.save()
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated: '{old_name}' -> '{new_name}' (Building: {floor.building.name})"
                )
            )
        
        self.stdout.write("-" * 50)
        self.stdout.write(
            self.style.SUCCESS(f"Total floors updated: {updated_count}")
        )
        self.stdout.write(f"Total floors checked: {floors.count()}")