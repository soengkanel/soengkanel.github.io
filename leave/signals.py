"""
Signals for automatic leave allocation
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from hr.models import Employee
from leave.models import LeaveType, LeaveAllocation


@receiver(post_save, sender=Employee)
def allocate_leave_to_new_employee(sender, instance, created, **kwargs):
    """
    Automatically allocate leave to newly created employees
    """
    # Skip if employee is being deleted
    if getattr(instance, '_being_deleted', False):
        return

    if created and instance.employment_status == 'active':
        current_year = timezone.now().year
        from_date = timezone.datetime(current_year, 1, 1).date()
        to_date = timezone.datetime(current_year, 12, 31).date()

        # Get all active leave types
        leave_types = LeaveType.objects.filter(is_active=True)

        for leave_type in leave_types:
            # Check if allocation already exists
            if not LeaveAllocation.objects.filter(
                employee=instance,
                leave_type=leave_type,
                year=current_year
            ).exists():
                LeaveAllocation.objects.create(
                    employee=instance,
                    leave_type=leave_type,
                    year=current_year,
                    allocated_days=leave_type.max_days_per_year,
                    used_days=0,
                    carried_forward=0,
                    from_date=from_date,
                    to_date=to_date,
                )
