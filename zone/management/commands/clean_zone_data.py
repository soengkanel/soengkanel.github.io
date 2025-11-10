from django.core.management.base import BaseCommand
from zone.models import Zone

class Command(BaseCommand):
    help = 'Clean zone data by removing inactive zones'

    def handle(self, *args, **options):
        # Remove inactive zones
        inactive_zones = Zone.objects.filter(is_active=False)
        count = inactive_zones.count()
        inactive_zones.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} inactive zones')
        ) 