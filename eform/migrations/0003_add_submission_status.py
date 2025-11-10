# Add status tracking to FormSubmission
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eform', '0002_create_form_tables'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='formsubmission',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Review'),
                    ('in_review', 'In Review'),
                    ('approved', 'Approved'),
                    ('completed', 'Completed'),
                    ('rejected', 'Rejected'),
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='reviewed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reviewed_form_submissions',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='admin_notes',
            field=models.TextField(blank=True, help_text='Internal notes visible to admin only'),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='response_message',
            field=models.TextField(blank=True, help_text='Message visible to the employee'),
        ),
        # Remove the unique_together constraint to allow multiple submissions
        migrations.AlterUniqueTogether(
            name='formsubmission',
            unique_together=set(),
        ),
    ]
