from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from datetime import datetime, timedelta, date
from .models import AttendanceRecord, BiometricTemplate, WorkSchedule, EmployeeSchedule


def get_employee_attendance_summary(employee, start_date=None, end_date=None):
    """Get attendance summary for an employee"""
    if not start_date:
        start_date = timezone.now().date().replace(day=1)  # First day of current month
    if not end_date:
        end_date = timezone.now().date()

    records = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=start_date,
        date__lte=end_date
    )

    total_days = (end_date - start_date).days + 1
    present_days = records.filter(status__in=['present', 'late', 'early_leave']).count()
    absent_days = records.filter(status='absent').count()
    late_days = records.filter(status='late').count()
    total_hours = records.aggregate(total=Sum('total_hours'))['total'] or 0
    overtime_hours = records.aggregate(total=Sum('overtime_hours'))['total'] or 0

    return {
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'total_hours': total_hours,
        'overtime_hours': overtime_hours,
        'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0,
    }


def get_employee_current_schedule(employee):
    """Get employee's current active schedule"""
    today = timezone.now().date()
    schedule = EmployeeSchedule.objects.filter(
        employee=employee,
        effective_from__lte=today,
        employment_status='active'
    ).filter(
        Q(effective_to__gte=today) | Q(effective_to__isnull=True)
    ).select_related('schedule').first()

    return schedule.schedule if schedule else None


def check_employee_biometric_enrollment(employee):
    """Check if employee has biometric templates enrolled"""
    return BiometricTemplate.objects.filter(employee=employee).exists()


def get_employee_last_attendance(employee):
    """Get employee's last attendance record"""
    return AttendanceRecord.objects.filter(employee=employee).order_by('-date').first()


def calculate_working_days(start_date, end_date, schedule=None):
    """Calculate working days based on schedule"""
    if not schedule:
        # Assume Monday to Friday if no schedule
        working_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # Monday=0, Friday=4
                working_days += 1
            current += timedelta(days=1)
        return working_days

    working_days = 0
    current = start_date
    while current <= end_date:
        day_schedule = schedule.get_day_schedule(current.weekday())
        if day_schedule[0] and day_schedule[1]:  # Has both start and end time
            working_days += 1
        current += timedelta(days=1)

    return working_days


def get_attendance_alerts(employee, days_back=30):
    """Get attendance alerts for employee"""
    start_date = timezone.now().date() - timedelta(days=days_back)
    end_date = timezone.now().date()

    records = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=start_date,
        date__lte=end_date
    )

    alerts = []

    # Check for excessive late arrivals
    late_count = records.filter(status='late').count()
    if late_count > 5:
        alerts.append({
            'type': 'warning',
            'message': f'Employee has been late {late_count} times in the last {days_back} days'
        })

    # Check for absences
    absent_count = records.filter(status='absent').count()
    if absent_count > 3:
        alerts.append({
            'type': 'error',
            'message': f'Employee has been absent {absent_count} times in the last {days_back} days'
        })

    # Check for missing punch records
    incomplete_records = records.filter(
        Q(clock_in__isnull=True) | Q(clock_out__isnull=True)
    ).exclude(status__in=['absent', 'leave', 'holiday'])

    if incomplete_records.exists():
        alerts.append({
            'type': 'info',
            'message': f'Employee has {incomplete_records.count()} incomplete attendance records'
        })

    return alerts


def generate_employee_attendance_report(employee, start_date, end_date):
    """Generate detailed attendance report for employee"""
    records = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    summary = get_employee_attendance_summary(employee, start_date, end_date)
    schedule = get_employee_current_schedule(employee)
    alerts = get_attendance_alerts(employee)

    return {
        'employee': employee,
        'start_date': start_date,
        'end_date': end_date,
        'records': records,
        'summary': summary,
        'schedule': schedule,
        'alerts': alerts,
        'biometric_enrolled': check_employee_biometric_enrollment(employee),
    }


def auto_create_absence_records(date=None):
    """Auto-create absence records for employees who didn't clock in"""
    if date is None:
        date = timezone.now().date()

    from hr.models import Employee

    # Get all active employees
    employees = Employee.objects.filter(employment_status='active')

    created_count = 0
    for employee in employees:
        # Check if attendance record already exists
        if not AttendanceRecord.objects.filter(employee=employee, date=date).exists():
            # Get employee's schedule for the date
            schedule = get_employee_current_schedule(employee)

            # Check if it's a working day
            if schedule:
                day_schedule = schedule.get_day_schedule(date.weekday())
                if day_schedule[0] and day_schedule[1]:  # Has working hours
                    AttendanceRecord.objects.create(
                        employee=employee,
                        date=date,
                        schedule=schedule,
                        status='absent'
                    )
                    created_count += 1

    return created_count


def sync_employee_biometric_templates(employee, device):
    """Sync employee's biometric templates to a specific device"""
    from .biometric_utils import get_biometric_service

    templates = BiometricTemplate.objects.filter(employee=employee, device=device)
    service = get_biometric_service()

    synced_count = 0
    for template in templates:
        try:
            success = service.enroll_fingerprint(
                device.device_id,
                int(employee.employee_id),
                template.template_data.encode(),
                template.finger_index
            )
            if success:
                synced_count += 1
        except Exception:
            continue

    return synced_count