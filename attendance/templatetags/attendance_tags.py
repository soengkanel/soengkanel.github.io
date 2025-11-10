from django import template
from django.utils import timezone
from datetime import timedelta
from ..models import AttendanceRecord, BiometricTemplate
from ..utils import get_employee_attendance_summary, get_employee_current_schedule

register = template.Library()


@register.inclusion_tag('attendance/employee_attendance_widget.html')
def employee_attendance_widget(employee):
    """Display attendance widget for employee profile"""
    # Get current month summary
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    summary = get_employee_attendance_summary(employee, start_of_month, today)
    current_schedule = get_employee_current_schedule(employee)

    # Get today's attendance
    today_attendance = AttendanceRecord.objects.filter(
        employee=employee,
        date=today
    ).first()

    # Check biometric enrollment
    has_biometric = BiometricTemplate.objects.filter(employee=employee).exists()

    # Get last 5 attendance records
    recent_records = AttendanceRecord.objects.filter(
        employee=employee
    ).order_by('-date')[:5]

    return {
        'employee': employee,
        'summary': summary,
        'current_schedule': current_schedule,
        'today_attendance': today_attendance,
        'has_biometric': has_biometric,
        'recent_records': recent_records,
    }


@register.simple_tag
def get_attendance_status_badge_class(status):
    """Get CSS class for attendance status badge"""
    status_classes = {
        'present': 'badge-success',
        'late': 'badge-warning',
        'early_leave': 'badge-info',
        'absent': 'badge-danger',
        'half_day': 'badge-secondary',
        'holiday': 'badge-primary',
        'weekend': 'badge-dark',
        'leave': 'badge-info',
    }
    return status_classes.get(status, 'badge-secondary')


@register.filter
def format_duration(hours):
    """Format hours as HH:MM"""
    if not hours:
        return '0:00'

    total_minutes = int(hours * 60)
    hours_part = total_minutes // 60
    minutes_part = total_minutes % 60

    return f"{hours_part}:{minutes_part:02d}"


@register.simple_tag
def employee_attendance_percentage(employee, days=30):
    """Get employee attendance percentage for last N days"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    summary = get_employee_attendance_summary(employee, start_date, end_date)
    return round(summary['attendance_percentage'], 1)


@register.simple_tag
def is_working_day(date, schedule=None):
    """Check if a date is a working day based on schedule"""
    if not schedule:
        return date.weekday() < 5  # Monday to Friday

    day_schedule = schedule.get_day_schedule(date.weekday())
    return day_schedule[0] is not None and day_schedule[1] is not None