from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.db import connection
from zone.models import Zone, Building, Department, Position
from hr.models import Department as HRDepartment, Position as HRPosition
from billing.models import Service

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate comprehensive master data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing master data before creating new data',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output of what is being created',
        )

    def handle(self, *args, **options):
        # Check if we're in the public schema - skip if so
        schema_name = connection.schema_name if hasattr(connection, 'schema_name') else 'unknown'
        if schema_name == 'public':
            self.stdout.write(
                self.style.WARNING('Skipping master data generation for public schema (not applicable)')
            )
            return
            
        self.verbose = options['verbose']
        
        if options['clear']:
            self.clear_existing_data()
        
        with transaction.atomic():
            # Get or create admin user for created_by fields
            admin_user = self.get_or_create_admin_user()
            
            # Generate master data in correct order (dependencies first)
            self.create_zones(admin_user)
            self.create_buildings(admin_user)
            self.create_zone_departments(admin_user)
            self.create_zone_positions(admin_user)
            self.create_hr_departments()
            self.create_hr_positions()
            self.create_billing_services()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully generated master data!')
        )
        self.stdout.write('You can now use the system with pre-populated master data.')

    def clear_existing_data(self):
        """Clear existing master data"""
        self.stdout.write('Clearing existing master data...')
        
        # Clear in reverse dependency order
        Position.objects.all().delete()
        HRPosition.objects.all().delete()
        Department.objects.all().delete()
        HRDepartment.objects.all().delete()
        Building.objects.all().delete()
        Zone.objects.all().delete()
        Service.objects.all().delete()
        
        self.stdout.write(self.style.WARNING('Cleared existing master data'))

    def get_or_create_admin_user(self):
        """Get or create an admin user for created_by fields"""
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            if self.verbose:
                self.stdout.write(f'Created admin user: {admin_user.username}')
        
        return admin_user

    def create_zones(self, admin_user):
        """Create sample zones"""
        zones_data = [
            {
                'name': 'Industrial Zone A',
                'phone_number': '+855-12-345-678',
                'address': 'Phnom Penh Special Economic Zone, Cambodia',
            },
            {
                'name': 'Industrial Zone B',
                'phone_number': '+855-12-345-679',
                'address': 'Sihanoukville Special Economic Zone, Cambodia',
            },
            {
                'name': 'Commercial Zone',
                'phone_number': '+855-12-345-680',
                'address': 'Central Business District, Phnom Penh',
            },
            {
                'name': 'Residential Zone',
                'phone_number': '+855-12-345-681',
                'address': 'Chamkarmon District, Phnom Penh',
            },
            {
                'name': 'Mixed Development Zone',
                'phone_number': '+855-12-345-682',
                'address': 'Daun Penh District, Phnom Penh',
            },
        ]
        
        created_count = 0
        for zone_data in zones_data:
            zone_data['created_by'] = admin_user
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'Created zone: {zone.name}')
        
        self.stdout.write(f'Zones: {created_count} created, {Zone.objects.count()} total')

    def create_buildings(self, admin_user):
        """Create sample buildings"""
        zones = list(Zone.objects.all())
        if not zones:
            self.stdout.write(self.style.ERROR('No zones found. Cannot create buildings.'))
            return
        
        buildings_data = [
            # Industrial Zone A buildings
            {
                'name': 'Factory Building A1',
                'code': 'FA1',
                'zone': zones[0] if len(zones) > 0 else zones[0],
                'address': '123 Industrial Street, Zone A',
                'total_floors': 3,
                'description': 'Main production facility with administrative offices',
            },
            {
                'name': 'Warehouse A2',
                'code': 'WA2',
                'zone': zones[0] if len(zones) > 0 else zones[0],
                'address': '125 Industrial Street, Zone A',
                'total_floors': 2,
                'description': 'Storage and distribution center',
            },
            # Industrial Zone B buildings
            {
                'name': 'Manufacturing Plant B1',
                'code': 'MB1',
                'zone': zones[1] if len(zones) > 1 else zones[0],
                'address': '456 Factory Road, Zone B',
                'total_floors': 4,
                'description': 'Advanced manufacturing facility',
            },
            # Commercial Zone buildings
            {
                'name': 'Office Tower C1',
                'code': 'OTC1',
                'zone': zones[2] if len(zones) > 2 else zones[0],
                'address': '789 Business Avenue, CBD',
                'total_floors': 15,
                'description': 'Premium office space for corporate tenants',
            },
            {
                'name': 'Retail Complex C2',
                'code': 'RC2',
                'zone': zones[2] if len(zones) > 2 else zones[0],
                'address': '790 Shopping Street, CBD',
                'total_floors': 5,
                'description': 'Mixed-use retail and office complex',
            },
            # Residential Zone buildings
            {
                'name': 'Residential Tower R1',
                'code': 'RT1',
                'zone': zones[3] if len(zones) > 3 else zones[0],
                'address': '321 Home Street, Chamkarmon',
                'total_floors': 20,
                'description': 'High-rise residential apartments',
            },
        ]
        
        created_count = 0
        for building_data in buildings_data:
            building_data['created_by'] = admin_user
            building, created = Building.objects.get_or_create(
                code=building_data['code'],
                defaults=building_data
            )
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'Created building: {building.name} ({building.code})')
        
        self.stdout.write(f'Buildings: {created_count} created, {Building.objects.count()} total')

    def create_zone_departments(self, admin_user):
        """Create zone departments (for zone app)"""
        departments_data = [
            # Management departments
            {
                'name': 'Executive Management',
                'code': 'EXEC',
                'description': 'Top-level executive and strategic management',
                'parent': None,
            },
            {
                'name': 'Operations Management',
                'code': 'OPS',
                'description': 'Daily operations and production management',
                'parent': None,
            },
            # Production departments
            {
                'name': 'Manufacturing',
                'code': 'MFG',
                'description': 'Production and manufacturing operations',
                'parent': None,
            },
            {
                'name': 'Quality Control',
                'code': 'QC',
                'description': 'Quality assurance and control processes',
                'parent': None,
            },
            {
                'name': 'Warehouse & Logistics',
                'code': 'WH',
                'description': 'Storage, inventory, and logistics management',
                'parent': None,
            },
            # Support departments
            {
                'name': 'Maintenance',
                'code': 'MAINT',
                'description': 'Equipment and facility maintenance',
                'parent': None,
            },
            {
                'name': 'Security',
                'code': 'SEC',
                'description': 'Security and safety operations',
                'parent': None,
            },
        ]
        
        # Create parent departments first
        created_departments = {}
        created_count = 0
        
        for dept_data in departments_data:
            dept_data['created_by'] = admin_user
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            created_departments[dept_data['code']] = dept
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'Created zone department: {dept.name} ({dept.code})')
        
        self.stdout.write(f'Zone Departments: {created_count} created, {Department.objects.count()} total')

    def create_zone_positions(self, admin_user):
        """Create zone positions (for zone app)"""
        departments = {dept.code: dept for dept in Department.objects.all()}
        
        positions_data = [
            # Executive positions
            {
                'name': 'Chief Executive Officer',
                'code': 'CEO',
                'department': departments.get('EXEC'),
                'level': 1,
                'description': 'Chief executive responsible for overall company strategy',
            },
            {
                'name': 'General Manager',
                'code': 'GM',
                'department': departments.get('EXEC'),
                'level': 2,
                'description': 'General management of operations and staff',
            },
            # Operations positions
            {
                'name': 'Operations Manager',
                'code': 'OPSMGR',
                'department': departments.get('OPS'),
                'level': 3,
                'description': 'Management of daily operations and processes',
            },
            {
                'name': 'Shift Supervisor',
                'code': 'SUPER',
                'department': departments.get('OPS'),
                'level': 4,
                'description': 'Supervision of shift workers and production',
            },
            # Production positions
            {
                'name': 'Production Manager',
                'code': 'PRODMGR',
                'department': departments.get('MFG'),
                'level': 3,
                'description': 'Management of production processes and staff',
            },
            {
                'name': 'Machine Operator',
                'code': 'MACHOP',
                'department': departments.get('MFG'),
                'level': 5,
                'description': 'Operation of manufacturing equipment',
            },
            {
                'name': 'Assembly Worker',
                'code': 'ASSEMBLY',
                'department': departments.get('MFG'),
                'level': 6,
                'description': 'Product assembly and basic manufacturing tasks',
            },
            # Quality positions
            {
                'name': 'Quality Manager',
                'code': 'QMGR',
                'department': departments.get('QC'),
                'level': 3,
                'description': 'Management of quality control processes',
            },
            {
                'name': 'Quality Inspector',
                'code': 'QI',
                'department': departments.get('QC'),
                'level': 5,
                'description': 'Inspection and testing of products',
            },
            # Warehouse positions
            {
                'name': 'Warehouse Manager',
                'code': 'WHMGR',
                'department': departments.get('WH'),
                'level': 3,
                'description': 'Management of warehouse operations',
            },
            {
                'name': 'Forklift Operator',
                'code': 'FORK',
                'department': departments.get('WH'),
                'level': 5,
                'description': 'Operation of forklifts and material handling',
            },
            {
                'name': 'Warehouse Worker',
                'code': 'WHWORK',
                'department': departments.get('WH'),
                'level': 6,
                'description': 'General warehouse and inventory tasks',
            },
            # Maintenance positions
            {
                'name': 'Maintenance Manager',
                'code': 'MAINTMGR',
                'department': departments.get('MAINT'),
                'level': 3,
                'description': 'Management of maintenance operations',
            },
            {
                'name': 'Technician',
                'code': 'TECH',
                'department': departments.get('MAINT'),
                'level': 5,
                'description': 'Equipment maintenance and repair',
            },
            # Security positions
            {
                'name': 'Security Manager',
                'code': 'SECMGR',
                'department': departments.get('SEC'),
                'level': 3,
                'description': 'Management of security operations',
            },
            {
                'name': 'Security Guard',
                'code': 'GUARD',
                'department': departments.get('SEC'),
                'level': 6,
                'description': 'Security patrol and monitoring duties',
            },
        ]
        
        created_count = 0
        for pos_data in positions_data:
            if pos_data['department'] is None:
                continue  # Skip if department not found
            
            pos_data['created_by'] = admin_user
            position, created = Position.objects.get_or_create(
                code=pos_data['code'],
                defaults=pos_data
            )
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'Created zone position: {position.name} ({position.code})')
        
        self.stdout.write(f'Zone Positions: {created_count} created, {Position.objects.count()} total')

    def create_hr_departments(self):
        """Create HR departments (for hr app)"""
        departments_data = [
            # Corporate departments
            {
                'name': 'Human Resources',
                'code': 'HR',
                'description': 'Employee relations, recruitment, and HR management',
                'parent': None,
            },
            {
                'name': 'Finance & Accounting',
                'code': 'FIN',
                'description': 'Financial management, accounting, and budgeting',
                'parent': None,
            },
            {
                'name': 'Information Technology',
                'code': 'IT',
                'description': 'IT systems, software development, and technical support',
                'parent': None,
            },
            {
                'name': 'Administration',
                'code': 'ADMIN',
                'description': 'General administration and office management',
                'parent': None,
            },
            {
                'name': 'Legal & Compliance',
                'code': 'LEGAL',
                'description': 'Legal affairs and compliance management',
                'parent': None,
            },
            # Sub-departments
            {
                'name': 'Recruitment',
                'code': 'RECRUIT',
                'description': 'Employee recruitment and onboarding',
                'parent_code': 'HR',
            },
            {
                'name': 'Payroll',
                'code': 'PAYROLL',
                'description': 'Payroll processing and benefits administration',
                'parent_code': 'HR',
            },
        ]
        
        # Create parent departments first
        created_departments = {}
        created_count = 0
        
        for dept_data in departments_data:
            if 'parent_code' not in dept_data:
                dept, created = HRDepartment.objects.get_or_create(
                    code=dept_data['code'],
                    defaults={
                        'name': dept_data['name'],
                        'code': dept_data['code'],
                        'description': dept_data['description'],
                        'parent': None,
                    }
                )
                created_departments[dept_data['code']] = dept
                if created:
                    created_count += 1
                    if self.verbose:
                        self.stdout.write(f'Created HR department: {dept.name} ({dept.code})')
        
        # Create child departments
        for dept_data in departments_data:
            if 'parent_code' in dept_data:
                parent = created_departments.get(dept_data['parent_code'])
                dept, created = HRDepartment.objects.get_or_create(
                    code=dept_data['code'],
                    defaults={
                        'name': dept_data['name'],
                        'code': dept_data['code'],
                        'description': dept_data['description'],
                        'parent': parent,
                    }
                )
                if created:
                    created_count += 1
                    if self.verbose:
                        self.stdout.write(f'Created HR department: {dept.name} ({dept.code})')
        
        self.stdout.write(f'HR Departments: {created_count} created, {HRDepartment.objects.count()} total')

    def create_hr_positions(self):
        """Create HR positions (for hr app)"""
        departments = {dept.code: dept for dept in HRDepartment.objects.all()}
        
        positions_data = [
            # HR positions
            {
                'name': 'HR Director',
                'code': 'HRDIR',
                'department': departments.get('HR'),
                'level': 2,
                'description': 'Director of human resources',
            },
            {
                'name': 'HR Manager',
                'code': 'HRMGR',
                'department': departments.get('HR'),
                'level': 3,
                'description': 'HR management and employee relations',
            },
            {
                'name': 'Recruiter',
                'code': 'RECRUIT',
                'department': departments.get('RECRUIT'),
                'level': 4,
                'description': 'Employee recruitment and selection',
            },
            {
                'name': 'Payroll Specialist',
                'code': 'PAYSPEC',
                'department': departments.get('PAYROLL'),
                'level': 4,
                'description': 'Payroll processing and benefits administration',
            },
            # Finance positions
            {
                'name': 'Finance Director',
                'code': 'FINDIR',
                'department': departments.get('FIN'),
                'level': 2,
                'description': 'Financial management and strategy',
            },
            {
                'name': 'Accountant',
                'code': 'ACCT',
                'department': departments.get('FIN'),
                'level': 4,
                'description': 'Accounting and financial record keeping',
            },
            {
                'name': 'Financial Analyst',
                'code': 'FINAN',
                'department': departments.get('FIN'),
                'level': 4,
                'description': 'Financial analysis and reporting',
            },
            # IT positions
            {
                'name': 'IT Director',
                'code': 'ITDIR',
                'department': departments.get('IT'),
                'level': 2,
                'description': 'IT strategy and systems management',
            },
            {
                'name': 'Software Developer',
                'code': 'DEV',
                'department': departments.get('IT'),
                'level': 4,
                'description': 'Software development and programming',
            },
            {
                'name': 'System Administrator',
                'code': 'SYSADMIN',
                'department': departments.get('IT'),
                'level': 4,
                'description': 'System administration and IT support',
            },
            # Admin positions
            {
                'name': 'Office Manager',
                'code': 'OFFMGR',
                'department': departments.get('ADMIN'),
                'level': 3,
                'description': 'Office administration and management',
            },
            {
                'name': 'Administrative Assistant',
                'code': 'ADMIN',
                'department': departments.get('ADMIN'),
                'level': 5,
                'description': 'General administrative support',
            },
            # Legal positions
            {
                'name': 'Legal Counsel',
                'code': 'LEGAL',
                'department': departments.get('LEGAL'),
                'level': 3,
                'description': 'Legal advice and compliance management',
            },
        ]
        
        created_count = 0
        for pos_data in positions_data:
            if pos_data['department'] is None:
                continue  # Skip if department not found
            
            position, created = HRPosition.objects.get_or_create(
                code=pos_data['code'],
                defaults=pos_data
            )
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'Created HR position: {position.name} ({position.code})')
        
        self.stdout.write(f'HR Positions: {created_count} created, {HRPosition.objects.count()} total')

    def create_billing_services(self):
        """Create billing services"""
        services_data = [
            # ID Cards Services
            {
                'name': 'New Worker ID Card',
                'category': 'id_cards',
                'description': 'Issue new ID card for worker with photo and details',
                'default_price': 15.00,
                'is_active': True,
            },
            {
                'name': 'Employee ID Card',
                'category': 'id_cards',
                'description': 'Issue new ID card for employee',
                'default_price': 12.00,
                'is_active': True,
            },
            {
                'name': 'ID Card Replacement',
                'category': 'id_cards',
                'description': 'Replace lost, damaged, or stolen ID card',
                'default_price': 20.00,
                'is_active': True,
            },
            {
                'name': 'ID Card Update',
                'category': 'id_cards',
                'description': 'Update information on existing ID card',
                'default_price': 10.00,
                'is_active': True,
            },
            # VIP ID Card Services
            {
                'name': 'VIP ID Card Printing',
                'category': 'id_cards',
                'description': 'VIP ID Card Printing',
                'default_price': 5.00,
                'is_active': True,
            },
            {
                'name': 'Worker ID Card Printing',
                'category': 'id_cards',
                'description': 'Worker ID Card Printing',
                'default_price': 2.00,
                'is_active': True,
            },
            {
                'name': 'Lost VIP ID Card Replacement',
                'category': 'id_cards',
                'description': 'Replacement service for lost VIP ID card',
                'default_price': 10.00,
                'is_active': True,
            },
            {
                'name': 'Lost Worker ID Card Replacement',
                'category': 'id_cards',
                'description': 'Replacement service for lost worker id card replacement',
                'default_price': 10.00,
                'is_active': True,
            },
            
            # Document Services
            {
                'name': 'Document Translation',
                'category': 'documents',
                'description': 'Professional document translation services',
                'default_price': 25.00,
                'is_active': True,
            },
            {
                'name': 'Document Certification',
                'category': 'documents',
                'description': 'Document certification and notarization',
                'default_price': 30.00,
                'is_active': True,
            },
            {
                'name': 'Document Processing',
                'category': 'documents',
                'description': 'General document processing and handling',
                'default_price': 15.00,
                'is_active': True,
            },
            
            # Visa & Permit Services
            {
                'name': 'Work Permit Application',
                'category': 'permits',
                'description': 'Process work permit application',
                'default_price': 150.00,
                'is_active': True,
            },
            {
                'name': 'Work Permit Renewal',
                'category': 'permits',
                'description': 'Renew existing work permit',
                'default_price': 120.00,
                'is_active': True,
            },
            {
                'name': 'Tourist Visa Application',
                'category': 'visas',
                'description': 'Process tourist visa application',
                'default_price': 80.00,
                'is_active': True,
            },
            {
                'name': 'Business Visa Application',
                'category': 'visas',
                'description': 'Process business visa application',
                'default_price': 120.00,
                'is_active': True,
            },
            
            # Visa Services by Duration
            {
                'name': '1 Month',
                'category': 'visa_services',
                'description': '1 month visa service',
                'default_price': 55.00,
                'is_active': True,
            },
            {
                'name': '3 Months',
                'category': 'visa_services',
                'description': '3 months visa service',
                'default_price': 85.00,
                'is_active': True,
            },
            {
                'name': '6 Months',
                'category': 'visa_services',
                'description': '6 months visa service',
                'default_price': 165.00,
                'is_active': True,
            },
            {
                'name': '1 Year',
                'category': 'visa_services',
                'description': '1 year visa service',
                'default_price': 300.00,
                'is_active': True,
            },
            
            # Additional Services
            {
                'name': 'Consultation Service',
                'category': 'consultation',
                'description': 'Legal and administrative consultation',
                'default_price': 50.00,
                'is_active': True,
            },
            {
                'name': 'Express Processing',
                'category': 'processing',
                'description': 'Express/urgent processing fee',
                'default_price': 35.00,
                'is_active': True,
            },
            {
                'name': 'Document Delivery',
                'category': 'delivery',
                'description': 'Document delivery and courier service',
                'default_price': 15.00,
                'is_active': True,
            },
        ]
        
        created_count = 0
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'Created service: {service.name}')
        
        self.stdout.write(f'Services: {created_count} created, {Service.objects.count()} total')