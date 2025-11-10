# Generated manually to add PayslipTemplate

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0004_add_overtime_tracking_to_salary_slip'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayslipTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('header_content', models.TextField(help_text='HTML content for payslip header')),
                ('footer_content', models.TextField(help_text='HTML content for payslip footer')),
                ('css_styles', models.TextField(blank=True, help_text='Custom CSS for payslip')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
