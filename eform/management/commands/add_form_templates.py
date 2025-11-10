from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from eform.models import FormTemplate


class Command(BaseCommand):
    help = 'Add predefined form templates to the eform app'

    def handle(self, *args, **options):
        # Get admin user for templates
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()

        if not admin_user:
            self.stdout.write(self.style.ERROR('No users found in database'))
            return

        templates = [
            {
                'name': 'Dental Claim Form',
                'description': 'Form for employees to submit dental treatment claims and reimbursement requests',
                'category': 'Claims & Reimbursements',
                'template_data': {
                    'fields': [
                        {'label': 'Employee Name', 'field_type': 'text', 'is_required': True, 'order': 1},
                        {'label': 'Employee ID', 'field_type': 'text', 'is_required': True, 'order': 2},
                        {'label': 'Treatment Date', 'field_type': 'date', 'is_required': True, 'order': 3},
                        {'label': 'Dental Clinic Name', 'field_type': 'text', 'is_required': True, 'order': 4},
                        {'label': 'Treatment Type', 'field_type': 'select', 'is_required': True, 'order': 5,
                         'options': ['Cleaning', 'Filling', 'Extraction', 'Root Canal', 'Crown/Bridge', 'Other']},
                        {'label': 'Total Amount', 'field_type': 'number', 'is_required': True, 'order': 6},
                        {'label': 'Claim Amount', 'field_type': 'number', 'is_required': True, 'order': 7},
                        {'label': 'Receipt Upload', 'field_type': 'file', 'is_required': True, 'order': 8},
                        {'label': 'Additional Notes', 'field_type': 'textarea', 'is_required': False, 'order': 9},
                    ]
                }
            },
            {
                'name': 'Medical Claim Form',
                'description': 'Form for employees to submit medical treatment claims and health insurance reimbursements',
                'category': 'Claims & Reimbursements',
                'template_data': {
                    'fields': [
                        {'label': 'Employee Name', 'field_type': 'text', 'is_required': True, 'order': 1},
                        {'label': 'Employee ID', 'field_type': 'text', 'is_required': True, 'order': 2},
                        {'label': 'Treatment Date', 'field_type': 'date', 'is_required': True, 'order': 3},
                        {'label': 'Medical Facility', 'field_type': 'text', 'is_required': True, 'order': 4},
                        {'label': 'Type of Treatment', 'field_type': 'select', 'is_required': True, 'order': 5,
                         'options': ['Outpatient', 'Inpatient', 'Emergency', 'Specialist Visit', 'Laboratory Tests', 'Other']},
                        {'label': 'Diagnosis', 'field_type': 'textarea', 'is_required': True, 'order': 6},
                        {'label': 'Total Medical Cost', 'field_type': 'number', 'is_required': True, 'order': 7},
                        {'label': 'Claim Amount', 'field_type': 'number', 'is_required': True, 'order': 8},
                        {'label': 'Medical Receipt/Invoice', 'field_type': 'file', 'is_required': True, 'order': 9},
                        {'label': 'Doctor\'s Prescription (if any)', 'field_type': 'file', 'is_required': False, 'order': 10},
                        {'label': 'Additional Details', 'field_type': 'textarea', 'is_required': False, 'order': 11},
                    ]
                }
            },
            {
                'name': 'Payment Request Form 001',
                'description': 'Standard form for requesting payment processing and vendor payments',
                'category': 'Financial Requests',
                'template_data': {
                    'fields': [
                        {'label': 'Requester Name', 'field_type': 'text', 'is_required': True, 'order': 1},
                        {'label': 'Department', 'field_type': 'text', 'is_required': True, 'order': 2},
                        {'label': 'Request Date', 'field_type': 'date', 'is_required': True, 'order': 3},
                        {'label': 'Payment Type', 'field_type': 'select', 'is_required': True, 'order': 4,
                         'options': ['Vendor Payment', 'Reimbursement', 'Advance Payment', 'Utility Bill', 'Other']},
                        {'label': 'Payee Name', 'field_type': 'text', 'is_required': True, 'order': 5},
                        {'label': 'Payment Amount', 'field_type': 'number', 'is_required': True, 'order': 6},
                        {'label': 'Payment Method', 'field_type': 'select', 'is_required': True, 'order': 7,
                         'options': ['Bank Transfer', 'Check', 'Cash', 'Other']},
                        {'label': 'Purpose of Payment', 'field_type': 'textarea', 'is_required': True, 'order': 8},
                        {'label': 'Supporting Documents', 'field_type': 'file', 'is_required': True, 'order': 9},
                        {'label': 'Urgency', 'field_type': 'select', 'is_required': True, 'order': 10,
                         'options': ['Normal', 'Urgent', 'Very Urgent']},
                    ]
                }
            },
            {
                'name': 'Resignation Form',
                'description': 'Official employee resignation form with notice period and exit details',
                'category': 'HR Forms',
                'template_data': {
                    'fields': [
                        {'label': 'Employee Name', 'field_type': 'text', 'is_required': True, 'order': 1},
                        {'label': 'Employee ID', 'field_type': 'text', 'is_required': True, 'order': 2},
                        {'label': 'Position', 'field_type': 'text', 'is_required': True, 'order': 3},
                        {'label': 'Department', 'field_type': 'text', 'is_required': True, 'order': 4},
                        {'label': 'Resignation Date', 'field_type': 'date', 'is_required': True, 'order': 5},
                        {'label': 'Last Working Day', 'field_type': 'date', 'is_required': True, 'order': 6},
                        {'label': 'Reason for Resignation', 'field_type': 'select', 'is_required': True, 'order': 7,
                         'options': ['Personal Reasons', 'Career Growth', 'Health Issues', 'Relocation', 'Further Studies', 'Other']},
                        {'label': 'Additional Comments', 'field_type': 'textarea', 'is_required': False, 'order': 8},
                        {'label': 'Willing to serve notice period?', 'field_type': 'radio', 'is_required': True, 'order': 9,
                         'options': ['Yes', 'No', 'Partial']},
                        {'label': 'Exit Interview Preference', 'field_type': 'radio', 'is_required': False, 'order': 10,
                         'options': ['Yes', 'No']},
                    ]
                }
            },
            {
                'name': 'Probation Evaluation Form',
                'description': 'Performance evaluation form for employees during probation period',
                'category': 'HR Forms',
                'template_data': {
                    'fields': [
                        {'label': 'Employee Name', 'field_type': 'text', 'is_required': True, 'order': 1},
                        {'label': 'Employee ID', 'field_type': 'text', 'is_required': True, 'order': 2},
                        {'label': 'Position', 'field_type': 'text', 'is_required': True, 'order': 3},
                        {'label': 'Department', 'field_type': 'text', 'is_required': True, 'order': 4},
                        {'label': 'Probation Start Date', 'field_type': 'date', 'is_required': True, 'order': 5},
                        {'label': 'Evaluation Date', 'field_type': 'date', 'is_required': True, 'order': 6},
                        {'label': 'Supervisor Name', 'field_type': 'text', 'is_required': True, 'order': 7},
                        {'label': 'Work Quality', 'field_type': 'select', 'is_required': True, 'order': 8,
                         'options': ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement']},
                        {'label': 'Attendance & Punctuality', 'field_type': 'select', 'is_required': True, 'order': 9,
                         'options': ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement']},
                        {'label': 'Team Collaboration', 'field_type': 'select', 'is_required': True, 'order': 10,
                         'options': ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement']},
                        {'label': 'Communication Skills', 'field_type': 'select', 'is_required': True, 'order': 11,
                         'options': ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement']},
                        {'label': 'Overall Performance Comments', 'field_type': 'textarea', 'is_required': True, 'order': 12},
                        {'label': 'Recommendation', 'field_type': 'select', 'is_required': True, 'order': 13,
                         'options': ['Confirm Employment', 'Extend Probation', 'Terminate']},
                        {'label': 'Areas for Improvement', 'field_type': 'textarea', 'is_required': False, 'order': 14},
                    ]
                }
            },
            {
                'name': 'Travel Request Form 001',
                'description': 'Business travel request and approval form with travel details',
                'category': 'Travel & Expenses',
                'template_data': {
                    'fields': [
                        {'label': 'Employee Name', 'field_type': 'text', 'is_required': True, 'order': 1},
                        {'label': 'Employee ID', 'field_type': 'text', 'is_required': True, 'order': 2},
                        {'label': 'Department', 'field_type': 'text', 'is_required': True, 'order': 3},
                        {'label': 'Travel Destination', 'field_type': 'text', 'is_required': True, 'order': 4},
                        {'label': 'Travel Purpose', 'field_type': 'textarea', 'is_required': True, 'order': 5},
                        {'label': 'Departure Date', 'field_type': 'date', 'is_required': True, 'order': 6},
                        {'label': 'Return Date', 'field_type': 'date', 'is_required': True, 'order': 7},
                        {'label': 'Travel Type', 'field_type': 'select', 'is_required': True, 'order': 8,
                         'options': ['Domestic', 'International']},
                        {'label': 'Transportation Mode', 'field_type': 'select', 'is_required': True, 'order': 9,
                         'options': ['Flight', 'Train', 'Car', 'Bus', 'Other']},
                        {'label': 'Estimated Budget', 'field_type': 'number', 'is_required': True, 'order': 10},
                        {'label': 'Accommodation Required', 'field_type': 'radio', 'is_required': True, 'order': 11,
                         'options': ['Yes', 'No']},
                        {'label': 'Additional Requirements', 'field_type': 'textarea', 'is_required': False, 'order': 12},
                    ]
                }
            },
        ]

        created_count = 0
        for template_data in templates:
            obj, created = FormTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'category': template_data['category'],
                    'template_data': template_data['template_data'],
                    'created_by': admin_user,
                    'is_public': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'[+] Created template: {template_data["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'[-] Template already exists: {template_data["name"]}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} new templates'))
