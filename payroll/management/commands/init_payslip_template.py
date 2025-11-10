from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_tenant_model
from payroll.models import PayslipTemplate


class Command(BaseCommand):
    help = 'Initialize default payslip template for all tenants'

    def handle(self, *args, **options):
        # Get all tenants
        TenantModel = get_tenant_model()
        tenants = TenantModel.objects.exclude(schema_name='public')

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                self.create_template_for_tenant(tenant)

    def create_template_for_tenant(self, tenant, *args, **options):
        # Check if default template already exists
        if PayslipTemplate.objects.filter(is_default=True).exists():
            self.stdout.write(
                self.style.WARNING(f'[{tenant.schema_name}] Default payslip template already exists')
            )
            return

        # Create default payslip template
        header_content = """
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="margin: 0; color: #333;">{{ company.name|default:"Company Name" }}</h1>
            <p style="margin: 5px 0; color: #666;">{{ company.address|default:"Company Address" }}</p>
            <h2 style="margin: 20px 0 10px 0; color: #2563eb;">PAYSLIP</h2>
        </div>
        """

        footer_content = """
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
            <p style="color: #666; font-size: 12px; margin: 5px 0;">
                This is a computer-generated payslip and does not require a signature.
            </p>
            <p style="color: #666; font-size: 12px; margin: 5px 0;">
                For any queries, please contact the HR department.
            </p>
        </div>
        """

        css_styles = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background-color: #f9fafb;
            font-weight: 600;
        }
        .total-row {
            font-weight: bold;
            background-color: #f0fdf4;
        }
        .net-pay {
            font-size: 1.5em;
            color: #16a34a;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background-color: #f0fdf4;
            border-radius: 8px;
        }
        """

        template = PayslipTemplate.objects.create(
            name='Default Payslip Template',
            is_default=True,
            header_content=header_content.strip(),
            footer_content=footer_content.strip(),
            css_styles=css_styles.strip(),
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'[{tenant.schema_name}] Successfully created default payslip template: {template.name}'
            )
        )
