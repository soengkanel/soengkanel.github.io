from django.core.management.base import BaseCommand
from django.db import transaction
from auditlog.models import LogEntry
from audit_management.models import AuditTrail, AuditSession
from hr.models import EmployeeHistory


class Command(BaseCommand):
    help = 'Clear all audit logs from all tables (LogEntry, AuditTrail, EmployeeHistory, AuditSession)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all audit logs',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will permanently delete ALL audit logs from all tables!\n'
                    'Run with --confirm flag to proceed: python manage.py clear_audit_logs --confirm'
                )
            )
            return

        # Count records before deletion
        logentry_count = LogEntry.objects.count()
        audittrail_count = AuditTrail.objects.count()
        employeehistory_count = EmployeeHistory.objects.count()
        auditsession_count = AuditSession.objects.count()

        total_count = logentry_count + audittrail_count + employeehistory_count + auditsession_count

        self.stdout.write(f'Found {total_count} total audit records:')
        self.stdout.write(f'  - LogEntry (django-auditlog): {logentry_count}')
        self.stdout.write(f'  - AuditTrail (business audit): {audittrail_count}')
        self.stdout.write(f'  - EmployeeHistory (HR events): {employeehistory_count}')
        self.stdout.write(f'  - AuditSession (sessions): {auditsession_count}')

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No audit logs found. Nothing to clear.'))
            return

        # Delete all audit logs in a transaction
        try:
            with transaction.atomic():
                # Clear in order (sessions first, then logs)
                AuditSession.objects.all().delete()
                EmployeeHistory.objects.all().delete()
                AuditTrail.objects.all().delete()
                LogEntry.objects.all().delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully cleared all {total_count} audit log records from all tables!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing audit logs: {str(e)}')
            ) 