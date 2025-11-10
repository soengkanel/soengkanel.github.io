from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from hr.models import Employee
from .models import AttendanceRecord, EmployeeSchedule, WorkSchedule
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Employee)
def create_default_schedule_assignment(sender, instance, created, **kwargs):
    """Assign default schedule to new employees"""
    # Skip if employee is being deleted
    if getattr(instance, '_being_deleted', False):
        return

    if created:
        try:
            # Find default schedule
            default_schedule = WorkSchedule.objects.filter(
                code='DEFAULT',
                is_active=True
            ).first()

            if default_schedule:
                EmployeeSchedule.objects.create(
                    employee=instance,
                    schedule=default_schedule,
                    effective_from=timezone.now().date()
                )
        except Exception as e:
            pass


@receiver(pre_save, sender=AttendanceRecord)
def calculate_attendance_before_save(sender, instance, **kwargs):
    """Calculate attendance metrics before saving"""
    if instance.clock_in and instance.clock_out:
        instance.calculate_hours()


@receiver(post_save, sender=AttendanceRecord)
def attendance_record_created(sender, instance, created, **kwargs):
    """Handle attendance record creation/update"""
    if created:
        # Check for policy violations
        pass


@receiver(post_save, sender=EmployeeSchedule)
def employee_schedule_assigned(sender, instance, created, **kwargs):
    """Handle employee schedule assignment"""
    if created:
        # Deactivate other active schedules for the same employee
        EmployeeSchedule.objects.filter(
            employee=instance.employee,
            is_active=True
        ).exclude(id=instance.id).update(is_active=False)