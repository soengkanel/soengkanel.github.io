from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from user_management.models import Role

class Command(BaseCommand):
    help = 'Add ID card permissions to User role so regular users can create ID cards'

    def handle(self, *args, **options):
        try:
            # Get or create the User role
            user_role, created = Role.objects.get_or_create(
                name='User',
                defaults={'description': 'Basic user access with ID card creation'}
            )
            
            if created:
                self.stdout.write(f"Created User role")
            else:
                self.stdout.write(f"Found existing User role")

            # Find ID card related permissions
            # Look for permissions with 'idcard' in the codename or related to HR models that handle ID cards
            idcard_permissions = Permission.objects.filter(
                codename__icontains='idcard'
            )
            
            # Also look for HR app permissions that might be related to ID cards
            hr_content_types = ContentType.objects.filter(app_label='hr')
            hr_permissions = Permission.objects.filter(
                content_type__in=hr_content_types,
                codename__in=['add_idcard', 'view_idcard', 'change_idcard', 'delete_idcard']
            )
            
            # Combine both sets of permissions
            all_idcard_permissions = idcard_permissions.union(hr_permissions)
            
            if not all_idcard_permissions.exists():
                self.stdout.write(self.style.WARNING("No ID card permissions found. Creating custom permissions..."))
                
                # Create custom permissions if they don't exist
                # We'll create them on a generic content type or the hr app
                hr_content_type = ContentType.objects.filter(app_label='hr').first()
                if hr_content_type:
                    permission_data = [
                        ('add_idcard', 'Can add ID card'),
                        ('view_idcard', 'Can view ID card'), 
                        ('change_idcard', 'Can change ID card'),
                        ('delete_idcard', 'Can delete ID card'),
                    ]
                    
                    created_permissions = []
                    for codename, name in permission_data:
                        perm, created = Permission.objects.get_or_create(
                            codename=codename,
                            content_type=hr_content_type,
                            defaults={'name': name}
                        )
                        if created:
                            created_permissions.append(perm)
                            self.stdout.write(f"Created permission: {codename}")
                        else:
                            created_permissions.append(perm)
                            self.stdout.write(f"Found existing permission: {codename}")
                    
                    all_idcard_permissions = Permission.objects.filter(id__in=[p.id for p in created_permissions])

            # Add all ID card permissions to the User role
            current_permissions = list(user_role.permissions.all())
            new_permissions = list(all_idcard_permissions)
            
            # Combine existing permissions with new ones
            all_permissions = set(current_permissions + new_permissions)
            user_role.permissions.set(all_permissions)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Added {len(new_permissions)} ID card permissions to User role. "
                    f"User role now has {user_role.permissions.count()} total permissions."
                )
            )
            
            # List the ID card permissions that were added
            self.stdout.write("ID card permissions added:")
            for perm in new_permissions:
                self.stdout.write(f"  - {perm.codename}: {perm.name}")
                
            # Also add some basic permissions that users typically need
            basic_permissions = Permission.objects.filter(
                codename__in=[
                    'view_worker',  # To view workers when creating cards
                    'view_employee', # To view employees when creating cards  
                    'view_building', # To see building info
                    'view_zone',     # To see zone info
                ]
            )
            
            if basic_permissions.exists():
                current_perms = set(user_role.permissions.all())
                current_perms.update(basic_permissions)
                user_role.permissions.set(current_perms)
                self.stdout.write(f"Also added {basic_permissions.count()} basic view permissions")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error setting up User role permissions: {str(e)}")
            )
            raise

        self.stdout.write(
            self.style.SUCCESS("Successfully configured User role with ID card creation permissions!")
        )