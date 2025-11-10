from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import BiometricDevice, AttendanceRecord
from attendance.biometric_utils import get_biometric_service
from hr.models import Employee
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync attendance data from all biometric devices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--device-id',
            type=str,
            help='Sync only specific device ID'
        )
        parser.add_argument(
            '--clear-logs',
            action='store_true',
            help='Clear device logs after sync'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving data'
        )

    def handle(self, *args, **options):
        device_id = options.get('device_id')
        clear_logs = options.get('clear_logs', False)
        dry_run = options.get('dry_run', False)

        if device_id:
            devices = BiometricDevice.objects.filter(device_id=device_id, status='active')
        else:
            devices = BiometricDevice.objects.filter(status='active')

        if not devices.exists():
            self.stdout.write(
                self.style.WARNING('No active biometric devices found')
            )
            return

        service = get_biometric_service()
        total_synced = 0

        for device in devices:
            self.stdout.write(f'Syncing device: {device.name} ({device.device_id})')

            try:
                # Register device if not already registered
                service.add_device(
                    device.device_id,
                    device.ip_address,
                    device.port,
                    device.device_type
                )

                # Sync attendance logs
                logs = service.sync_attendance(device.device_id)
                synced_count = 0

                for log in logs:
                    try:
                        # Find employee by ID
                        try:
                            employee = Employee.objects.get(employee_id=log['user_id'])
                        except Employee.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(f"Employee {log['user_id']} not found, skipping")
                            )
                            continue

                        attendance_date = log['timestamp'].date()

                        if not dry_run:
                            # Get or create attendance record
                            attendance, created = AttendanceRecord.objects.get_or_create(
                                employee=employee,
                                date=attendance_date,
                                defaults={
                                    'schedule': self.get_employee_schedule(employee, attendance_date)
                                }
                            )

                            # Update clock times based on log type
                            if log['type'] == 'clock_in':
                                if not attendance.clock_in or attendance.clock_in > log['timestamp']:
                                    attendance.clock_in = log['timestamp']
                                    attendance.clock_in_device = device

                            elif log['type'] == 'clock_out':
                                if not attendance.clock_out or attendance.clock_out < log['timestamp']:
                                    attendance.clock_out = log['timestamp']
                                    attendance.clock_out_device = device

                            attendance.save()

                        synced_count += 1

                        self.stdout.write(
                            f"  Processed: {employee.full_name} - {log['timestamp']}"
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing log: {e}")
                        )

                if not dry_run:
                    # Update device last sync time
                    device.last_sync = timezone.now()
                    device.save()

                    # Clear device logs if requested
                    if clear_logs:
                        device_conn = service.get_device(device.device_id)
                        if hasattr(device_conn, 'clear_attendance_logs'):
                            device_conn.clear_attendance_logs()

                total_synced += synced_count

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Device {device.name}: {synced_count} records synced"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to sync device {device.name}: {e}")
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would have synced {total_synced} records")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Sync completed: {total_synced} records synced")
            )

    def get_employee_schedule(self, employee, date):
        """Get employee's active schedule for a specific date"""
        from attendance.models import EmployeeSchedule
        from django.db.models import Q

        schedule = EmployeeSchedule.objects.filter(
            employee=employee,
            effective_from__lte=date,
            is_active=True
        ).filter(
            Q(effective_to__gte=date) | Q(effective_to__isnull=True)
        ).select_related('schedule').first()

        return schedule.schedule if schedule else None