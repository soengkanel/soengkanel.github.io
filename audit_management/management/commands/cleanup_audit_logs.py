"""
Django management command for automated audit log cleanup.
Usage: python manage.py cleanup_audit_logs --days 90
"""

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from audit_management.models import AuditTrail, AuditSession, AuditException
from audit_management.utils import AuditLogger

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up audit logs older than specified days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete logs older than this many days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--include-active-sessions',
            action='store_true',
            help='Also clean up active sessions (use with caution)'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress normal output'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        include_active_sessions = options['include_active_sessions']
        quiet = options['quiet']

        if days < 1:
            raise CommandError('Days must be at least 1')

        cutoff_date = timezone.now() - timedelta(days=days)

        if not quiet:
            self.stdout.write(
                self.style.WARNING(f'Cleaning up audit logs older than {days} days...')
            )
            self.stdout.write(f'Cutoff date: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')

        try:
            with transaction.atomic():
                # Count what will be deleted
                logs_to_delete = AuditTrail.objects.filter(timestamp__lt=cutoff_date)
                logs_count = logs_to_delete.count()

                # Sessions filter
                if include_active_sessions:
                    sessions_to_delete = AuditSession.objects.filter(last_activity__lt=cutoff_date)
                else:
                    sessions_to_delete = AuditSession.objects.filter(
                        last_activity__lt=cutoff_date,
                        is_active=False
                    )
                sessions_count = sessions_to_delete.count()

                exceptions_to_delete = AuditException.objects.filter(timestamp__lt=cutoff_date)
                exceptions_count = exceptions_to_delete.count()

                if not quiet:
                    self.stdout.write(f'Found {logs_count} audit logs to delete')
                    self.stdout.write(f'Found {sessions_count} sessions to delete')
                    self.stdout.write(f'Found {exceptions_count} exceptions to delete')

                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS('DRY RUN: No data was actually deleted')
                    )
                    return

                if logs_count == 0 and sessions_count == 0 and exceptions_count == 0:
                    if not quiet:
                        self.stdout.write(
                            self.style.SUCCESS('No old data found to clean up')
                        )
                    return

                # Perform deletion
                if logs_count > 0:
                    logs_to_delete.delete()
                    if not quiet:
                        self.stdout.write(f'Deleted {logs_count} audit logs')

                if sessions_count > 0:
                    sessions_to_delete.delete()
                    if not quiet:
                        self.stdout.write(f'Deleted {sessions_count} sessions')

                if exceptions_count > 0:
                    exceptions_to_delete.delete()
                    if not quiet:
                        self.stdout.write(f'Deleted {exceptions_count} exceptions')

                # Log this cleanup action
                try:
                    AuditLogger.log_action(
                        user=None,  # System action
                        action_type='delete',
                        resource_type='audit_logs',
                        description=f"Automated cleanup: deleted {logs_count} logs, {sessions_count} sessions, {exceptions_count} exceptions older than {days} days",
                        severity='info',
                        risk_score=20,
                        tags=['automated_cleanup', 'maintenance', 'retention_policy']
                    )
                except Exception as e:
                    # If logging fails, continue
                    pass

                if not quiet:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully cleaned up {logs_count + sessions_count + exceptions_count} records'
                        )
                    )

        except Exception as e:
            raise CommandError(f'Error during cleanup: {e}')

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS('Audit log cleanup completed successfully')
            ) 