from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from user_management.models import Role, UserRoleAssignment

class Command(BaseCommand):
    help = 'Set up default roles and assign role to specified user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='User email to assign admin role')

    def handle(self, *args, **options):
        # Create default roles
        roles_data = [
            {
                'name': 'Administrator',
                'description': 'Full system access with all permissions',
            },
            {
                'name': 'Manager', 
                'description': 'Management access with most permissions',
            },
            {
                'name': 'Staff',
                'description': 'Standard staff access',
            },
            {
                'name': 'User',
                'description': 'Basic user access',
            }
        ]

        created_roles = []
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                created_roles.append(role.name)
                self.stdout.write(f"Created role: {role.name}")
            else:
                self.stdout.write(f"Role already exists: {role.name}")

        # If email provided, assign Administrator role
        if options['email']:
            try:
                user = User.objects.get(email=options['email'])
                admin_role = Role.objects.get(name='Administrator')
                
                # Get or create role assignment
                role_assignment, created = UserRoleAssignment.objects.get_or_create(
                    user=user,
                    defaults={'assigned_by': user}  # Self-assigned for admin
                )
                
                # Assign admin role
                role_assignment.role = admin_role
                role_assignment.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f"Assigned Administrator role to {user.username} ({user.email})")
                )
                
                # Add all permissions to Administrator role
                all_permissions = Permission.objects.all()
                admin_role.permissions.set(all_permissions)
                self.stdout.write(f"Added {all_permissions.count()} permissions to Administrator role")
                
            except User.DoesNotExist:

                
                pass
                self.stdout.write(
                    self.style.ERROR(f"User with email {options['email']} not found")
                )
            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR("Administrator role not found")
                )

        self.stdout.write(self.style.SUCCESS("Role setup completed!")) 