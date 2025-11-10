from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from eform.models import Form, FormField


class Command(BaseCommand):
    help = 'Create sample employee request forms'

    def handle(self, *args, **options):
        # Check if tables exist first
        try:
            Form.objects.exists()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Skipping - Form tables do not exist in this schema: {str(e)[:100]}'))
            return

        # Get first admin/superuser
        admin_user = User.objects.filter(is_superuser=True).first()

        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()

        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create an admin user first.'))
            return

        # Delete existing forms (for fresh start)
        Form.objects.all().delete()
        self.stdout.write('Cleared existing forms')

        # 1. Employment Certificate Request Form
        form1 = Form.objects.create(
            title="Employment Certificate Request",
            description="Request an official employment certificate for visa applications, bank loans, housing rental, or other purposes.",
            created_by=admin_user,
            status='published',
            is_public=True,
            allow_multiple_submissions=True,
            require_login=True
        )

        FormField.objects.create(
            form=form1,
            label="Full Name",
            field_type="text",
            help_text="Your full name as per employment records",
            is_required=True,
            order=1
        )

        FormField.objects.create(
            form=form1,
            label="Employee ID",
            field_type="text",
            help_text="Your employee identification number",
            is_required=True,
            order=2
        )

        FormField.objects.create(
            form=form1,
            label="Certificate Type",
            field_type="select",
            options=["Employment Certificate", "Salary Certificate", "Experience Certificate", "Reference Letter", "Service Certificate"],
            help_text="Select the type of certificate you need",
            is_required=True,
            order=3
        )

        FormField.objects.create(
            form=form1,
            label="Purpose",
            field_type="select",
            options=["Visa Application", "Bank Loan Application", "Housing Rental", "New Employment", "Government Requirement", "Personal Use", "Other"],
            help_text="What will you use this certificate for?",
            is_required=True,
            order=4
        )

        FormField.objects.create(
            form=form1,
            label="Include Salary Information",
            field_type="radio",
            options=["Yes", "No"],
            help_text="Do you need salary details included in the certificate?",
            is_required=True,
            order=5
        )

        FormField.objects.create(
            form=form1,
            label="Urgency Level",
            field_type="select",
            options=["Normal (5-7 business days)", "Urgent (2-3 business days)", "Emergency (Same/Next day)"],
            is_required=True,
            order=6
        )

        FormField.objects.create(
            form=form1,
            label="Additional Details",
            field_type="textarea",
            help_text="Provide any additional information, special requirements, or specific text you need in the certificate",
            is_required=False,
            order=7
        )

        self.stdout.write(self.style.SUCCESS(f'Created: {form1.title}'))

        # 2. IT Support Request Form
        form2 = Form.objects.create(
            title="IT Support Request",
            description="Submit requests for IT support, technical issues, software installation, or hardware problems.",
            created_by=admin_user,
            status='published',
            is_public=True,
            allow_multiple_submissions=True,
            require_login=True
        )

        FormField.objects.create(
            form=form2,
            label="Request Category",
            field_type="select",
            options=["Hardware Issue", "Software Installation", "Network/Internet Problem", "Email Issue", "Password Reset", "New Equipment Request", "System Access", "Other"],
            is_required=True,
            order=1
        )

        FormField.objects.create(
            form=form2,
            label="Priority",
            field_type="radio",
            options=["Low - Can wait", "Medium - Affecting work", "High - Cannot work", "Critical - System down"],
            is_required=True,
            order=2
        )

        FormField.objects.create(
            form=form2,
            label="Issue Description",
            field_type="textarea",
            help_text="Describe the issue in detail. Include error messages if any.",
            is_required=True,
            order=3
        )

        FormField.objects.create(
            form=form2,
            label="Equipment/System Affected",
            field_type="text",
            help_text="E.g., Desktop PC, Laptop, Printer, Email, Specific software",
            is_required=True,
            order=4
        )

        FormField.objects.create(
            form=form2,
            label="Contact Phone Number",
            field_type="tel",
            help_text="Your contact number for follow-up",
            is_required=True,
            order=5
        )

        self.stdout.write(self.style.SUCCESS(f'Created: {form2.title}'))

        # 3. Facility/Maintenance Request
        form3 = Form.objects.create(
            title="Facility Maintenance Request",
            description="Report facility issues or request maintenance for office equipment, infrastructure, or workplace conditions.",
            created_by=admin_user,
            status='published',
            is_public=True,
            allow_multiple_submissions=True,
            require_login=True
        )

        FormField.objects.create(
            form=form3,
            label="Request Type",
            field_type="select",
            options=["Air Conditioning", "Electrical", "Plumbing", "Furniture", "Cleaning", "Security", "Lighting", "Building Maintenance", "Other"],
            is_required=True,
            order=1
        )

        FormField.objects.create(
            form=form3,
            label="Location",
            field_type="text",
            help_text="Building, floor, room number, or specific location",
            is_required=True,
            order=2
        )

        FormField.objects.create(
            form=form3,
            label="Issue Description",
            field_type="textarea",
            help_text="Describe the maintenance issue or request in detail",
            is_required=True,
            order=3
        )

        FormField.objects.create(
            form=form3,
            label="Severity",
            field_type="radio",
            options=["Minor - Can wait", "Moderate - Should be fixed soon", "Urgent - Safety or work impact", "Emergency - Immediate attention required"],
            is_required=True,
            order=4
        )

        self.stdout.write(self.style.SUCCESS(f'Created: {form3.title}'))

        # 4. General Feedback/Suggestion Form
        form4 = Form.objects.create(
            title="Employee Feedback & Suggestions",
            description="Share your feedback, ideas, concerns, or suggestions to help improve our workplace.",
            created_by=admin_user,
            status='published',
            is_public=True,
            allow_multiple_submissions=True,
            require_login=True
        )

        FormField.objects.create(
            form=form4,
            label="Feedback Category",
            field_type="select",
            options=["Workplace Environment", "Management & Leadership", "Training & Development", "Compensation & Benefits", "Work-Life Balance", "Communication", "Facilities & Equipment", "General Suggestion", "Other"],
            is_required=True,
            order=1
        )

        FormField.objects.create(
            form=form4,
            label="Your Feedback",
            field_type="textarea",
            help_text="Share your thoughts, concerns, or suggestions in detail",
            is_required=True,
            order=2
        )

        FormField.objects.create(
            form=form4,
            label="Submission Type",
            field_type="radio",
            options=["Anonymous", "Identified (I want to be contacted)"],
            help_text="Choose whether you want to remain anonymous or be identified for follow-up",
            is_required=True,
            order=3
        )

        FormField.objects.create(
            form=form4,
            label="Would you like a response?",
            field_type="radio",
            options=["Yes - via email", "Yes - in-person meeting", "No response needed"],
            is_required=True,
            order=4
        )

        self.stdout.write(self.style.SUCCESS(f'Created: {form4.title}'))

        # 5. Stationery/Supplies Request
        form5 = Form.objects.create(
            title="Office Supplies Request",
            description="Request office supplies, stationery, or equipment needed for your work.",
            created_by=admin_user,
            status='published',
            is_public=True,
            allow_multiple_submissions=True,
            require_login=True
        )

        FormField.objects.create(
            form=form5,
            label="Items Needed",
            field_type="textarea",
            help_text="List the items you need (one per line with quantity)",
            placeholder="Example:\n- Pens (10 pieces)\n- A4 Paper (2 reams)\n- Stapler (1 unit)",
            is_required=True,
            order=1
        )

        FormField.objects.create(
            form=form5,
            label="Reason for Request",
            field_type="text",
            help_text="Brief reason why you need these items",
            is_required=True,
            order=2
        )

        FormField.objects.create(
            form=form5,
            label="When do you need these items?",
            field_type="date",
            help_text="Select the date you need the items by",
            is_required=True,
            order=3
        )

        self.stdout.write(self.style.SUCCESS(f'Created: {form5.title}'))

        # Summary
        total_forms = Form.objects.filter(status='published', is_public=True).count()
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {total_forms} employee request forms'))
        self.stdout.write(self.style.SUCCESS('Employees can now access these forms at: /employee/forms/'))
