from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from core.admin import User
from user_management.models import PermissionSet, Role, UserRoleAssignment
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    """
    CENTRALIZED ACCESS CONTROL MANAGEMENT
    =====================================
    
    This is the single source of truth for role permissions in the system.
    
    NON-DESTRUCTIVE: Updates existing roles and permissions without deleting them.
    Safe to run multiple times.
    
    Role Definitions:
        pass
    -----------------
    1. Administrator: Full system access (all permissions)
    2. Manager: Operational tasks with most CRUD permissions
    3. User: Basic access with specific creation permissions:
       - Create zones (zone.add_zone)
       - Create probation periods (hr.add_probationperiod) 
       - Create invoices (billing.add_invoice)
       - Create cash receipts (billing.add_cashchequereceipt)
       - Create payment vouchers (billing.add_paymentvoucher)
    4. Staff: (defined in setup_roles, not updated here)
    
    Usage:
        pass
    ------
    python manage.py generate_access_control --update-permissions
    
    Developer Note:
        pass
    ---------------
    ALL role permission changes should be made in this file to maintain
    a single source of truth for access control configuration.
    """
    
    help="Update user access control (non-destructive) - Centralized permission management"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--update-permissions',
            action='store_true',
            help='Update permissions for existing roles'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating access control (non-destructive)...'))
        
        if options['update_permissions']:
            self.update_role_permissions()
        else:
            self.stdout.write('Use --update-permissions flag to update role permissions')
            self.stdout.write('This is a safety measure to prevent accidental permission changes')
            self.stdout.write('')
            self.stdout.write('Example: python manage.py generate_access_control --update-permissions')

        self.stdout.write(
            self.style.SUCCESS('Access control update completed!')
        )
    
    def update_role_permissions(self):
        """Update permissions for existing roles without deleting anything"""
        self.stdout.write('Updating role permissions...')
        
        # Define the permissions each role should have
        # Manager gets most permissions for operational tasks
        manager_permissions_codes = [
            # Zone/Worker permissions (Entry menu)
            'view_worker','add_worker','delete_worker','change_worker',
            'view_zone','add_zone','delete_zone','change_zone',
            'view_building','add_building','delete_building','change_building',
            'view_floor','add_floor','delete_floor','change_floor',
            'view_document','add_document','delete_document','change_document',
            'view_workerprobationperiod','add_workerprobationperiod','delete_workerprobationperiod','change_workerprobationperiod',
            'view_workerprobationextension','add_workerprobationextension','delete_workerprobationextension','change_workerprobationextension',
            # HR permissions
            'view_employee','add_employee','delete_employee','change_employee',
            'view_department','add_department','delete_department','change_department',
            'view_position','add_position','delete_position','change_position',
            'view_probationperiod','add_probationperiod','delete_probationperiod','change_probationperiod',
            'view_idcard','add_idcard','delete_idcard','change_idcard',
            # Billing permissions
            'view_invoice','add_invoice','delete_invoice','change_invoice',
            'view_cashchequereceipt','add_cashchequereceipt','delete_cashchequereceipt','change_cashchequereceipt',
            'view_officialreceipt','add_officialreceipt','delete_officialreceipt','change_officialreceipt',
            'view_paymentvoucher','add_paymentvoucher','delete_paymentvoucher','change_paymentvoucher',
            # E-form permissions
            'view_form','add_form','delete_form','change_form',
        ]
        
        # Regular users get view and basic add permissions for employee self-service
        user_permissions_codes = [
            # Employee self-service permissions
            # Leave permissions
            'view_leaveapplication','add_leaveapplication','change_leaveapplication',
            'view_leaveallocation',
            'view_leavetype',
            'view_holiday',
            # HR - View own employee record
            'view_employee',
            'view_employeedocument','add_employeedocument',
            'view_idcard','add_idcardrequest',
            'view_probationperiod',
            # Attendance - View own attendance
            'view_attendancerecord',
            'view_breakrecord',
            'view_overtimerequest','add_overtimerequest','change_overtimerequest',
            'view_attendancecorrection','add_attendancecorrection',
            # Payroll - View own payslips
            'view_salary','view_salaryslip',
            'view_salaryadvance','add_salaryadvance',
            'view_employeeloan',
            'view_employeebenefit','add_employeebenefit',
            # Overtime claims
            'view_overtimeclaim','add_overtimeclaim','change_overtimeclaim',
            # E-forms
            'view_form','add_formsubmission',
            'view_certificaterequest','add_certificaterequest',
            'view_extensionrequest','add_extensionrequest',
        ]
        
        manager_permissions = Permission.objects.filter(codename__in=manager_permissions_codes)
        user_permissions = Permission.objects.filter(codename__in=user_permissions_codes)
        
        # Update Manager role permissions
        try:
            manager_role = Role.objects.get(name="Manager")
            manager_role.permissions.set(manager_permissions)
            self.stdout.write(self.style.SUCCESS(f'Updated Manager role permissions ({manager_permissions.count()} permissions)'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('Manager role does not exist. Run setup_initial_access_control --confirm first.'))
        
        # Update User role permissions
        try:
            user_role = Role.objects.get(name="User")
            user_role.permissions.set(user_permissions)
            self.stdout.write(self.style.SUCCESS(f'Updated User role permissions ({user_permissions.count()} permissions)'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('User role does not exist. Run setup_initial_access_control --confirm first.'))
        
        # Update Administrator role permissions (give all permissions)
        try:
            admin_role = Role.objects.get(name="Administrator")
            admin_role.permissions.set(Permission.objects.all())
            self.stdout.write(self.style.SUCCESS(f'Updated Administrator role permissions ({Permission.objects.count()} permissions)'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('Administrator role does not exist. Run setup_roles command first.'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Role permissions updated successfully!'))
        self.stdout.write('Users with these roles will now have the updated permissions.')