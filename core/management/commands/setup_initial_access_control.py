from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from core.admin import User
from user_management.models import PermissionSet, Role, UserRoleAssignment
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    """
    Initial setup command - DESTRUCTIVE! 
    Only run this ONCE during initial system setup.
    This will DELETE all existing roles and recreate them.
    """
    
    help="Initial setup for user access control - WARNING: This is DESTRUCTIVE!"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all existing roles and permissions'
        )
    
    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('WARNING: This command will DELETE all existing roles and user assignments!')
            )
            self.stdout.write('If you are sure you want to continue, run with --confirm flag')
            return
        
        self.stdout.write(
            self.style.WARNING('DELETING all existing roles and permissions...')
        )

        self.create_role()
        self.create_manager()
        self.create_users()
        self.assign_admin_role()
        self.show_login_credentials()

        self.stdout.write(
            self.style.SUCCESS('Successfully generated initial access control data!')
        )
    
    # generate manager
    def create_manager(self):
      
        # self.info(f"Creating managers for  KK Company...")
        self.stdout.write('Creating managers for  KK Company...')

        manager_role = Role.objects.filter(name="Manager").first()

        # self.info(f"Get managers role {manager_role.name}")
        self.stdout.write(f'Get managers role {manager_role.name}')

        managers_data = [
                {
                    'username': 'm1',
                    'email': 'm1@ngt.com.kh',
                    'first_name': 'Manager',
                    'last_name': 'One',
                    'password': 'manager123',
                },
                {
                    'username': 'm2',
                    'email': 'm2@ngt.com.kh',
                    'first_name': 'Manager',
                    'last_name': 'Two',
                    'password': 'manager123'
                },
        ]
            
        created_count = 0
        ## create manager
        for manager in managers_data:
            try:
                manager_created, created = User.objects.get_or_create(
                    username=manager["username"],
                    defaults={
                        'email': manager['email'],
                        'first_name': manager['first_name'],
                        'last_name': manager['last_name'],
                        'is_staff': True,
                        'is_active': True
                    }
                )
            
                if created:
                    manager_created.set_password(manager["password"])
                    manager_created.save()
                    # manager_created.role_assignments.add(manager_role.id)
                    UserRoleAssignment.objects.get_or_create(
                        user=manager_created,
                        role=manager_role,
                        defaults={'is_active': True}
                    )
                    created_count+=1
                    # self.info(f"  Created manager: {manager['username']} ({manager['email']})")
                    self.stdout.write(f"Created manager: {manager['username']} ({manager['email']}) ")
                else:
                    # Ensure existing manager has an active role assignment
                    assignment, created = UserRoleAssignment.objects.get_or_create(
                        user=manager_created,
                        role=manager_role,
                        defaults={'is_active': True}
                    )
                    if not created and not assignment.is_active:
                        assignment.is_active = True
                        assignment.save()
                    # self.info(f"  Manager already exists: {manager['username']}")
                    self.stdout.write(f"Manager already exists: {manager['username']}")

            except Exception as e:
                # self.error(f"Failed to create manager {manager['username']}: {e}")
                self.stdout.write(self.style.ERROR(f"Failed to create manager {manager['username']}: {e}"))
        
        # self.success(f"Created {created_count} new managers")
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new managers"))


    ## generate user
    def create_users(self):
        # self.info(f"Creating users for KK Company...")
        self.stdout.write("Creating users for KK Company...")
        ## get role
        user_role = Role.objects.filter(name="User").first()

        # self.info(f"Get user role {user_role.name}")
        self.stdout.write(f"Get user role {user_role.name}")

        
        created_count = 0
        users_data = []
        
        # Generate 15 users (u1 through u15)
        number_names = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 
                       'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 
                       'Fourteen', 'Fifteen']
        
        for i in range(1, 16):
            users_data.append({
                'username': f'u{i}',
                'email': f'u{i}@ngt.com.kh',
                'first_name': 'User',
                'last_name': number_names[i-1] if i <= len(number_names) else str(i),
                'password': 'user123'
            })
            
        for user in users_data:
            try:
                user_created, created = User.objects.get_or_create(
                    username=user["username"],
                    defaults={
                        'email': user['email'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'is_staff': True,
                        'is_active': True
                    }
                )
            
                if created:
                    user_created.set_password(user["password"])
                    user_created.save()
                    UserRoleAssignment.objects.get_or_create(
                        user=user_created,
                        role=user_role,
                        defaults={'is_active': True}
                    )
                    created_count+=1
                    self.stdout.write(f"Created user: {user['username']} ({user['email']}) ")
                else:
                    # Ensure existing user has an active role assignment
                    assignment, created = UserRoleAssignment.objects.get_or_create(
                        user=user_created,
                        role=user_role,
                        defaults={'is_active': True}
                    )
                    if not created and not assignment.is_active:
                        assignment.is_active = True
                        assignment.save()
                    self.stdout.write(f"User already exists: {user['username']}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create user {user['username']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new users"))


    def assign_admin_role(self):
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                admin_role, created = Role.objects.get_or_create(
                    name="Admin",
                    defaults={'description': "Full system administrator"}
                )
                
                if created:
                    # Give admin role all permissions
                    admin_role.permissions.set(Permission.objects.all())
                    
                # Assign admin role to superuser
                UserRoleAssignment.objects.get_or_create(
                    user=admin_user,
                    role=admin_role,
                    defaults={'is_active': True}
                )
                self.stdout.write(f"Assigned Admin role to {admin_user.username}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to assign admin role: {e}"))

    def show_login_credentials(self):
        self.stdout.write(self.style.SUCCESS('\n=== LOGIN CREDENTIALS ==='))
        self.stdout.write('Managers:')
        self.stdout.write('  Username: m1, Password: manager123')
        self.stdout.write('  Username: m2, Password: manager123')
        self.stdout.write('')
        self.stdout.write('Users (15 users):')
        for i in range(1, 16):
            self.stdout.write(f'  Username: u{i}, Password: user123')
        self.stdout.write('')

        
    ## genrate defaul roles
    def create_role(self):
        
        # WARNING: This deletes all roles!
        Role.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted all existing roles!'))
        
        self.create_permission_set()
        
        roles_data = [
            {
                "name":"Admin",
                "description":"Manage all functions and feature of system and Admin Panal"
            },
             {
                "name":"Manager",
                "description":"Manage all functions and feature of system"
            },
             {
                "name":"User",
                "description":"Can access functions and feature base on manager has assigned"
            }
        ]
    
        manager_permissions =  Permission.objects.filter(codename__in=['view_zone','add_zone','delete_zone','change_zone',
                                                                   'view_worker','add_worker','delete_worker','change_worker',
                                                                   'view_workerprobationperiod','add_workerprobationperiod','delete_workerprobationperiod','change_workerprobationperiod',
                                                                   'view_idcard','add_idcard','delete_idcard','change_idcard',
                                                                   'view_document','add_document','delete_document','change_document',
                                                                   'view_form','add_form','delete_form','change_form',
                                                                   'view_invoice','add_invoice','delete_invoice','change_invoice',
                                                                   'view_employee','add_employee','delete_employee','change_employee',
                                                                   'view_worker_report','add_worker_report','delete_worker_report','change_worker_report',
                                                                   'view_department','add_department','delete_department','change_department',
                                                                   'view_position','add_position','delete_position','change_position',
                                                                   'view_user','add_user','change_user','delete_user',
                                                                   'view_role','add_role','change_role','delete_role',
                                                                   'view_permissionset','add_permissionset','change_permissionset','delete_permissionset',
                                                                   'view_userroleassignment','add_userroleassignment','change_userroleassignment','delete_userroleassignment'])
        
        user_permissions =  Permission.objects.filter(codename__in=['view_worker','add_worker','delete_worker','change_worker',
                                                                   'view_workerprobationperiod','add_workerprobationperiod','delete_workerprobationperiod','change_workerprobationperiod',
                                                                   'view_idcard','add_idcard','delete_idcard','change_idcard',
                                                                   'view_document','add_document','delete_document','change_document',
                                                                   'view_form','add_form','delete_form','change_form',
                                                                   'view_invoice','add_invoice','delete_invoice','change_invoice',
                                                                   'view_employee','add_employee','delete_employee','change_employee',
                                                                   'view_worker_report','add_worker_report','delete_worker_report','change_worker_report',
                                                                   'view_department','view_position'])
        
        created_count = 0
        
        for role in roles_data:
            
            created = Role.objects.create(
                name=role["name"],
                description=role["description"]
            )
            
            if created:
                if created.name == "User":
                    created.permissions.add(*user_permissions)
                else:
                    created.permissions.add(*manager_permissions)
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Role {created_count} created'))
        
    ## generate permission set
    def create_permission_set(self):
        
        self.create_permissions()
           
        PermissionSet.objects.all().delete()
       
        zone_permissions = Permission.objects.filter(codename__in=['view_zone','add_zone','delete_zone','change_zone'])
        worker_permissions = Permission.objects.filter(codename__in=['view_worker','add_worker','delete_worker','change_worker'])
        probation_permissions = Permission.objects.filter(codename__in=['view_workerprobationperiod','add_workerprobationperiod','delete_workerprobationperiod','change_workerprobationperiod'])
        idcard_permissions = Permission.objects.filter(codename__in=['view_idcard','add_idcard','delete_idcard','change_idcard'])
        document_permissions = Permission.objects.filter(codename__in=['view_document','add_document','delete_document','change_document'])
        eform_permissions = Permission.objects.filter(codename__in=['view_form','add_form','delete_form','change_form'])
        billing_permissions = Permission.objects.filter(codename__in=['view_invoice','add_invoice','delete_invoice','change_invoice'])
        employee_permissions =Permission.objects.filter(codename__in=['view_employee','add_employee','delete_employee','change_employee'])
        wroker_report_permissions = Permission.objects.filter(codename__in=['view_worker_report','add_worker_report','delete_worker_report','change_worker_report'])
        # Settings permissions removed - no Setting model exists
        hr_permissions = Permission.objects.filter(codename__in=['view_department','add_department','delete_department','change_department','view_position','add_position','delete_position','change_position'])
        user_management_permissions = Permission.objects.filter(codename__in=['view_user','add_user','change_user','delete_user','view_role','add_role','change_role','delete_role','view_permissionset','add_permissionset','change_permissionset','delete_permissionset','view_userroleassignment','add_userroleassignment','change_userroleassignment','delete_userroleassignment'])
        
        if not worker_permissions :
            self.stdout.write(self.style.ERROR('No worker permissions found. Cannot create permission set.'))
            return
    
        permission_sets_data = [
            {"name":"Zone",
             "description":"Zone Management",
             "is_system_set":True,
             "permissions":zone_permissions
             },
            {"name":"Probation", 
             "description":"Worker Probation Management",
             "is_system_set":True,
             "permissions":probation_permissions
             },
            {"name":"Worker",
             "description":"Worker Management", 
             "is_system_set":True,
             "permissions":worker_permissions
             },
            {"name":"Id Card",
             "description":"ID Card Management", 
             "is_system_set":True,
             "permissions":idcard_permissions
             },
            {"name":"Document", 
             "description":"Document Management",
             "is_system_set":True,
             "permissions":document_permissions
             },
            {"name":"EForm",
             "description":"Electronic Forms", 
             "is_system_set":True,
             "permissions":eform_permissions
             },
            {"name":"Billing",
             "description":"Billing Management", 
             "is_system_set":True,
             "permissions":billing_permissions
             },
            {"name":"Employee",
             "description":"Employee Management", 
             "is_system_set":True,
             "permissions":employee_permissions
             },
            {"name":"Worker Reports",
             "description":"Worker Reports", 
             "is_system_set":True,
             "permissions":wroker_report_permissions
             },
            {"name":"HR",
             "description":"Human Resources - Departments and Positions", 
             "is_system_set":True,
             "permissions":hr_permissions
             },
            {"name":"User Management",
             "description":"User, Role and Permission Management", 
             "is_system_set":True,
             "permissions":user_management_permissions
             }
        ]
        
        created_count = 0
        for permission_set in permission_sets_data:
            if permission_set['permissions'].exists():
                created_permission_set = PermissionSet.objects.create(
                    name=permission_set["name"],
                    description=permission_set["description"],
                    is_system_set=permission_set["is_system_set"]
                )
                
                created_permission_set.permissions.add(*permission_set['permissions'])
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'No permissions found for {permission_set["name"]}, skipping...'))
                
        self.stdout.write(self.style.SUCCESS(f'Permission set {created_count} created'))

    ## generate permissions
    def create_permissions(self):
        permissions_data = {
            "zone": ["zone", "worker", "workerprobationperiod"],
            "hr": ["employee", "idcard", "department", "position"],
            "cards": ["idcard"],
            "document_tracking": ["document"],
            "eform": ["form"],
            "billing": ["invoice"],
            "core": ["worker_report"],
            "auth": ["user"],
            "user_management": ["role", "permissionset", "userroleassignment"]
        }

        created_count = 0
        
        for app, models in permissions_data.items():
            for model in models:
                try:
                    content_type = ContentType.objects.get(app_label=app, model=model)
                    
                    for action in ['add', 'change', 'delete', 'view']:
                        codename = f"{action}_{model}"
                        permission, created = Permission.objects.get_or_create(
                            codename=codename,
                            content_type=content_type,
                            defaults={'name': f'Can {action} {model}'}
                        )
                        if created:
                            created_count += 1
                except ContentType.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'ContentType not found for {app}.{model}, skipping...'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating permission for {app}.{model}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Permission {created_count} created'))