from django.core.management.base import BaseCommand
from eform.models import CertificateRequest


class Command(BaseCommand):
    help = 'Fix certificate request data after migration'

    def handle(self, *args, **options):
        # Since the existing certificate requests have invalid data structure
        # and no workers assigned, we'll clear them all
        count = CertificateRequest.objects.count()
        
        if count > 0:
            self.stdout.write(f'Found {count} certificate requests with invalid data structure.')
            self.stdout.write('Clearing all existing certificate requests...')
            
            CertificateRequest.objects.all().delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully cleared {count} invalid certificate requests. '
                    'You can now create new certificate requests with the updated system.'
                )
            )
        else:
            self.stdout.write('No certificate requests found.') 