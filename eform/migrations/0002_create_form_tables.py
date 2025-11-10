# Manual migration to create Form tables
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eform', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('is_public', models.BooleanField(default=False)),
                ('allow_multiple_submissions', models.BooleanField(default=True)),
                ('collect_email', models.BooleanField(default=False)),
                ('require_login', models.BooleanField(default=False)),
                ('submission_deadline', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_forms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=200)),
                ('field_type', models.CharField(choices=[('text', 'Text Input'), ('textarea', 'Textarea'), ('email', 'Email'), ('number', 'Number'), ('date', 'Date'), ('time', 'Time'), ('datetime', 'Date and Time'), ('select', 'Select Dropdown'), ('radio', 'Radio Button'), ('checkbox', 'Checkbox'), ('file', 'File Upload'), ('url', 'URL'), ('tel', 'Phone'), ('range', 'Range Slider'), ('color', 'Color Picker')], max_length=20)),
                ('help_text', models.TextField(blank=True)),
                ('is_required', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('options', models.JSONField(blank=True, default=list)),
                ('min_length', models.PositiveIntegerField(blank=True, null=True)),
                ('max_length', models.PositiveIntegerField(blank=True, null=True)),
                ('min_value', models.FloatField(blank=True, null=True)),
                ('max_value', models.FloatField(blank=True, null=True)),
                ('pattern', models.CharField(blank=True, help_text='Regex pattern for validation', max_length=500)),
                ('default_value', models.TextField(blank=True)),
                ('css_class', models.CharField(blank=True, max_length=200)),
                ('placeholder', models.CharField(blank=True, max_length=200)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='eform.form')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('data', models.JSONField(default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='eform.form')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.CreateModel(
            name='FormTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(max_length=100)),
                ('template_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_public', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
