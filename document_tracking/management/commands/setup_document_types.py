from django.core.management.base import BaseCommand
from document_tracking.models import DocumentType


class Command(BaseCommand):
    help = 'Set up default document types with processing times'

    def handle(self, *args, **options):
        document_types = [
            {
                'name': 'Visa Process (Regular)',
                'description': 'Standard visa processing through government building',
                'processing_days': 14,
                'processing_entity': 'building',
                'is_express': False,
                'required_documents': 'Passport, Application form, Photos, Supporting documents',
                'fees': 150.00
            },
            {
                'name': 'Work Permit (Regular)', 
                'description': 'Standard work permit processing through government building',
                'processing_days': 25,
                'processing_entity': 'building',
                'is_express': False,
                'required_documents': 'Employment contract, Medical certificate, Educational certificates',
                'fees': 200.00
            },
            {
                'name': 'Express Visa',
                'description': 'Fast-track visa processing through people\'s office',
                'processing_days': 3,
                'processing_entity': 'people',
                'is_express': True,
                'required_documents': 'Passport, Application form, Photos, Supporting documents, Express fee',
                'fees': 300.00
            },
            {
                'name': 'Express Work Permit',
                'description': 'Fast-track work permit processing through people\'s office',
                'processing_days': 15,
                'processing_entity': 'people',
                'is_express': True,
                'required_documents': 'Employment contract, Medical certificate, Educational certificates, Express fee',
                'fees': 400.00
            },
            {
                'name': 'Passport Renewal',
                'description': 'Passport renewal service',
                'processing_days': 21,
                'processing_entity': 'embassy',
                'is_express': False,
                'required_documents': 'Old passport, Application form, Photos',
                'fees': 100.00
            },
            {
                'name': 'Residence Permit',
                'description': 'Residence permit application',
                'processing_days': 30,
                'processing_entity': 'ministry',
                'is_express': False,
                'required_documents': 'Rental agreement, Financial proof, Application form',
                'fees': 250.00
            },
            {
                'name': 'Business License',
                'description': 'Business registration and licensing',
                'processing_days': 14,
                'processing_entity': 'ministry',
                'is_express': False,
                'required_documents': 'Business plan, Registration documents, Financial statements',
                'fees': 500.00
            }
        ]

        created_count = 0
        updated_count = 0

        for doc_type_data in document_types:
            doc_type, created = DocumentType.objects.get_or_create(
                name=doc_type_data['name'],
                defaults=doc_type_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created document type: {doc_type.name}')
                )
            else:
                # Update existing record with new data
                for key, value in doc_type_data.items():
                    setattr(doc_type, key, value)
                doc_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated document type: {doc_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSetup complete! Created {created_count} new document types, '
                f'updated {updated_count} existing types.'
            )
        ) 