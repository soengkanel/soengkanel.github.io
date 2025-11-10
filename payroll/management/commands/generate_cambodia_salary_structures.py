"""
Generate comprehensive Cambodian salary structures for different scenarios.

This command creates salary structures covering:
    pass
- Different industries (Garment, Hospitality, Tech, Banking, NGO, etc.)
- Employment types (Full-time, Part-time, Contract, Daily wage)
- Salary levels (Minimum wage, Entry, Mid, Senior, Executive)
- Special scenarios (Expatriate, Remote work, Probation, etc.)

All structures comply with Cambodian labor law:
    pass
- Minimum wage: KHR 200 per day (KHR 4,400-5,200/month depending on sector)
- NSSF: 3.5% employee, 0.8% + 2.6% employer
- Progressive tax: 0%, 5%, 10%, 15%, 20%
- Standard allowances: Housing, Transport, Meal, etc.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import schema_context
from decimal import Decimal
from datetime import date

from payroll.models import (
    SalaryStructure, SalaryDetail, SalaryComponent
)


class Command(BaseCommand):
    help = 'Generate comprehensive Cambodian salary structures for different scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default='kk_company',
            help='Tenant schema name (default: kk_company)'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']

        self.stdout.write(self.style.WARNING(f'\n{"="*80}'))
        self.stdout.write(self.style.WARNING('CAMBODIAN SALARY STRUCTURE GENERATOR'))
        self.stdout.write(self.style.WARNING(f'{"="*80}\n'))

        try:
            with schema_context(schema_name):
                self.stdout.write(f'>> Working in schema: {schema_name}\n')

                with transaction.atomic():
                    # Ensure salary components exist
                    self.ensure_salary_components()

                    # Generate different salary structure categories
                    structures_created = []

                    # 1. Industry-Specific Structures
                    self.stdout.write(self.style.SUCCESS('\n>> Creating Industry-Specific Structures...'))
                    structures_created.extend(self.create_industry_structures())

                    # 2. Employment Type Structures
                    self.stdout.write(self.style.SUCCESS('\n>> Creating Employment Type Structures...'))
                    structures_created.extend(self.create_employment_type_structures())

                    # 3. Salary Level Structures
                    self.stdout.write(self.style.SUCCESS('\n>> Creating Salary Level Structures...'))
                    structures_created.extend(self.create_salary_level_structures())

                    # 4. Special Scenario Structures
                    self.stdout.write(self.style.SUCCESS('\n>> Creating Special Scenario Structures...'))
                    structures_created.extend(self.create_special_scenario_structures())

                    # 5. Executive & Management Structures
                    self.stdout.write(self.style.SUCCESS('\n>> Creating Executive & Management Structures...'))
                    structures_created.extend(self.create_executive_structures())

                    # Print summary
                    self.print_summary(structures_created)

                self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Created {len(structures_created)} salary structures!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] Error: {str(e)}'))
            raise

    def ensure_salary_components(self):
        """Ensure all necessary salary components exist"""
        self.stdout.write('Checking salary components...')

        components = [
            # Earnings
            ('BASIC', 'Basic Salary', 'EARNING', 'FIXED'),
            ('HRA', 'Housing Allowance', 'EARNING', 'FIXED'),
            ('TRANSPORT', 'Transport Allowance', 'EARNING', 'FIXED'),
            ('MEAL', 'Meal Allowance', 'EARNING', 'FIXED'),
            ('PHONE', 'Phone Allowance', 'EARNING', 'FIXED'),
            ('SENIORITY', 'Seniority Allowance', 'EARNING', 'FIXED'),
            ('OVERTIME', 'Overtime Pay', 'EARNING', 'VARIABLE'),
            ('BONUS', 'Performance Bonus', 'EARNING', 'VARIABLE'),
            ('COMMISSION', 'Sales Commission', 'EARNING', 'VARIABLE'),
            ('SHIFT', 'Shift Allowance', 'EARNING', 'FIXED'),
            ('HARDSHIP', 'Hardship Allowance', 'EARNING', 'FIXED'),
            ('EXPAT', 'Expatriate Allowance', 'EARNING', 'FIXED'),
            ('EDUCATION', 'Education Allowance', 'EARNING', 'FIXED'),
            ('HEALTH', 'Health Insurance', 'EARNING', 'FIXED'),

            # Deductions
            ('NSSF_EMP', 'NSSF Employee', 'DEDUCTION', 'PERCENTAGE'),
            ('TAX', 'Salary Tax', 'DEDUCTION', 'PERCENTAGE'),
            ('ADVANCE', 'Salary Advance', 'DEDUCTION', 'VARIABLE'),
            ('LOAN', 'Loan Deduction', 'DEDUCTION', 'VARIABLE'),
        ]

        for code, name, comp_type, calc_type in components:
            component, created = SalaryComponent.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'component_type': comp_type,
                    'calculation_type': calc_type,
                    'is_payable': True if comp_type == 'EARNING' else False,
                    'is_tax_applicable': True if code not in ['NSSF_EMP', 'TAX'] else False,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  [+] Created component: {name}')

    def create_industry_structures(self):
        """Create industry-specific salary structures"""
        structures = []

        # 1. Garment Industry (Minimum Wage Sector)
        structure = self.create_structure(
            name='Garment Factory Worker',
            company='Garment Industry',
            components={
                'BASIC': 200 * 26,      # KHR 200/day × 26 days = 5,200
                'MEAL': 50000,          # Standard meal allowance
                'TRANSPORT': 50000,     # Transport allowance
                'OVERTIME': 0,          # Variable, added during payroll
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 2. Hospitality Industry
        structure = self.create_structure(
            name='Hospitality Staff',
            company='Hotel & Restaurant',
            components={
                'BASIC': 800000,        # KHR 800K base
                'HRA': 120000,          # 15% housing
                'MEAL': 100000,         # Meal allowance
                'TRANSPORT': 80000,     # Transport
                'SHIFT': 50000,         # Shift allowance
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 3. IT/Tech Industry
        structure = self.create_structure(
            name='IT Professional',
            company='Technology Sector',
            components={
                'BASIC': 2000000,       # KHR 2M base
                'HRA': 300000,          # Housing
                'TRANSPORT': 150000,    # Transport
                'PHONE': 50000,         # Phone allowance
                'HEALTH': 100000,       # Health insurance
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 4. Banking & Finance
        structure = self.create_structure(
            name='Banking Professional',
            company='Financial Sector',
            components={
                'BASIC': 2500000,       # KHR 2.5M base
                'HRA': 375000,          # 15% housing
                'TRANSPORT': 200000,    # Transport
                'PHONE': 80000,         # Phone
                'HEALTH': 150000,       # Health insurance
                'BONUS': 0,             # Performance bonus (variable)
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 5. NGO Sector
        structure = self.create_structure(
            name='NGO Program Officer',
            company='NGO Sector',
            components={
                'BASIC': 1500000,       # KHR 1.5M base
                'HRA': 225000,          # Housing
                'TRANSPORT': 150000,    # Transport
                'PHONE': 60000,         # Phone
                'HARDSHIP': 100000,     # Hardship allowance (field work)
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 6. Construction Industry
        structure = self.create_structure(
            name='Construction Worker',
            company='Construction Sector',
            components={
                'BASIC': 220 * 26,      # KHR 220/day
                'MEAL': 60000,          # Meal
                'TRANSPORT': 80000,     # Transport
                'HARDSHIP': 50000,      # Site work allowance
                'OVERTIME': 0,          # Variable
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 7. Retail & Sales
        structure = self.create_structure(
            name='Retail Sales Staff',
            company='Retail Sector',
            components={
                'BASIC': 900000,        # KHR 900K base
                'HRA': 135000,          # Housing
                'MEAL': 80000,          # Meal
                'TRANSPORT': 70000,     # Transport
                'COMMISSION': 0,        # Sales commission (variable)
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        return structures

    def create_employment_type_structures(self):
        """Create structures for different employment types"""
        structures = []

        # 1. Full-Time Regular
        structure = self.create_structure(
            name='Full-Time Regular Employee',
            company='Standard Employment',
            components={
                'BASIC': 1200000,
                'HRA': 180000,
                'TRANSPORT': 100000,
                'MEAL': 80000,
                'PHONE': 40000,
                'HEALTH': 80000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 2. Part-Time Employee
        structure = self.create_structure(
            name='Part-Time Employee',
            company='Part-Time Employment',
            components={
                'BASIC': 600000,        # 50% of full-time
                'TRANSPORT': 50000,     # Reduced allowances
                'MEAL': 40000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 3. Fixed-Term Contract
        structure = self.create_structure(
            name='Fixed-Term Contract',
            company='Contract Employment',
            components={
                'BASIC': 1500000,
                'HRA': 225000,
                'TRANSPORT': 120000,
                'MEAL': 80000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 4. Daily Wage Worker
        structure = self.create_structure(
            name='Daily Wage Worker',
            company='Daily Employment',
            components={
                'BASIC': 250 * 26,      # KHR 250/day × 26 days
                'MEAL': 40000,
                'OVERTIME': 0,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            },
            salary_slip_based_on_timesheet=True
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 5. Freelance/Consultant
        structure = self.create_structure(
            name='Freelance Consultant',
            company='Freelance/Contract',
            components={
                'BASIC': 3000000,       # Project-based rate
                'TAX': 'progressive',   # No NSSF for true freelancers
            },
            salary_slip_based_on_timesheet=True
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        return structures

    def create_salary_level_structures(self):
        """Create structures for different salary levels"""
        structures = []

        # 1. Entry Level (Minimum Wage Compliant)
        structure = self.create_structure(
            name='Entry Level - Minimum Wage',
            company='Entry Level',
            components={
                'BASIC': 200 * 26,      # Minimum wage
                'MEAL': 50000,
                'TRANSPORT': 50000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 2. Junior Level
        structure = self.create_structure(
            name='Junior Level',
            company='Junior Position',
            components={
                'BASIC': 800000,
                'HRA': 120000,
                'TRANSPORT': 80000,
                'MEAL': 60000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 3. Mid Level
        structure = self.create_structure(
            name='Mid Level Professional',
            company='Mid Level',
            components={
                'BASIC': 1500000,
                'HRA': 225000,
                'TRANSPORT': 150000,
                'MEAL': 80000,
                'PHONE': 50000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 4. Senior Level
        structure = self.create_structure(
            name='Senior Professional',
            company='Senior Level',
            components={
                'BASIC': 2500000,
                'HRA': 375000,
                'TRANSPORT': 200000,
                'MEAL': 100000,
                'PHONE': 80000,
                'HEALTH': 150000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 5. Lead/Principal Level
        structure = self.create_structure(
            name='Lead/Principal Level',
            company='Principal Level',
            components={
                'BASIC': 4000000,
                'HRA': 600000,
                'TRANSPORT': 300000,
                'MEAL': 150000,
                'PHONE': 100000,
                'HEALTH': 200000,
                'BONUS': 0,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        return structures

    def create_special_scenario_structures(self):
        """Create structures for special scenarios"""
        structures = []

        # 1. Probation Period
        structure = self.create_structure(
            name='Probation Period (3 months)',
            company='Probationary',
            components={
                'BASIC': 1000000,       # Often 80-85% of regular
                'HRA': 150000,
                'TRANSPORT': 80000,
                'MEAL': 60000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 2. Expatriate Package
        structure = self.create_structure(
            name='Expatriate Package',
            company='Expatriate Employment',
            components={
                'BASIC': 5000000,
                'HRA': 2000000,         # Higher housing for expats
                'TRANSPORT': 500000,    # Car allowance
                'PHONE': 150000,
                'EXPAT': 1000000,       # Special expat allowance
                'HEALTH': 500000,       # International health insurance
                'EDUCATION': 800000,    # Children's education
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 3. Remote Work Package
        structure = self.create_structure(
            name='Remote Work Package',
            company='Remote Employment',
            components={
                'BASIC': 1800000,
                'HRA': 270000,
                'PHONE': 100000,        # Higher for home internet/phone
                'HEALTH': 100000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 4. Shift Work (24/7 Operations)
        structure = self.create_structure(
            name='Shift Worker (24/7 Operations)',
            company='Shift Operations',
            components={
                'BASIC': 1000000,
                'HRA': 150000,
                'TRANSPORT': 120000,    # Higher for night transport
                'MEAL': 100000,
                'SHIFT': 200000,        # Shift differential
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 5. Sales with Commission
        structure = self.create_structure(
            name='Sales Representative (Commission-based)',
            company='Sales',
            components={
                'BASIC': 800000,        # Lower base
                'HRA': 120000,
                'TRANSPORT': 150000,    # Higher for field work
                'PHONE': 80000,
                'COMMISSION': 0,        # Variable, can be substantial
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 6. Intern/Trainee
        structure = self.create_structure(
            name='Intern/Trainee',
            company='Internship',
            components={
                'BASIC': 400000,        # Stipend amount
                'MEAL': 40000,
                'TRANSPORT': 40000,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        return structures

    def create_executive_structures(self):
        """Create executive and management structures"""
        structures = []

        # 1. Manager
        structure = self.create_structure(
            name='Manager',
            company='Management',
            components={
                'BASIC': 3500000,
                'HRA': 525000,
                'TRANSPORT': 300000,
                'MEAL': 150000,
                'PHONE': 100000,
                'HEALTH': 200000,
                'BONUS': 0,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 2. Senior Manager
        structure = self.create_structure(
            name='Senior Manager',
            company='Senior Management',
            components={
                'BASIC': 5000000,
                'HRA': 750000,
                'TRANSPORT': 500000,
                'MEAL': 200000,
                'PHONE': 150000,
                'HEALTH': 300000,
                'BONUS': 0,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 3. Director
        structure = self.create_structure(
            name='Director',
            company='Executive',
            components={
                'BASIC': 8000000,
                'HRA': 1200000,
                'TRANSPORT': 800000,    # Car allowance
                'MEAL': 300000,
                'PHONE': 200000,
                'HEALTH': 500000,
                'BONUS': 0,
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        # 4. C-Level Executive
        structure = self.create_structure(
            name='C-Level Executive (CEO/CFO/CTO)',
            company='C-Suite',
            components={
                'BASIC': 12000000,
                'HRA': 2000000,
                'TRANSPORT': 1500000,
                'MEAL': 500000,
                'PHONE': 300000,
                'HEALTH': 800000,
                'BONUS': 0,             # Variable, often substantial
                'NSSF_EMP': '3.5%',
                'TAX': 'progressive',
            }
        )
        structures.append(structure)
        self.stdout.write(f'  [+] Created: {structure.name}')

        return structures

    def create_structure(self, name, company, components, salary_slip_based_on_timesheet=False):
        """Helper method to create a salary structure"""

        # Create salary structure
        structure = SalaryStructure.objects.create(
            name=name,
            company=company,
            is_active=True,
            salary_slip_based_on_timesheet=salary_slip_based_on_timesheet,
            docstatus=1  # Submitted
        )

        # Add salary components
        for comp_code, amount in components.items():
            try:
                component = SalaryComponent.objects.get(code=comp_code)

                # Determine if it's a fixed amount or formula
                if isinstance(amount, str) and '%' in amount:
                    # Percentage formula
                    formula = f"base * {Decimal(amount.replace('%', '')) / 100}"
                    SalaryDetail.objects.create(
                        salary_structure=structure,
                        salary_component=component,
                        amount=Decimal('0'),
                        formula=formula
                    )
                elif amount == 'progressive':
                    # Progressive tax - will be calculated
                    SalaryDetail.objects.create(
                        salary_structure=structure,
                        salary_component=component,
                        amount=Decimal('0'),
                        formula='progressive_tax(taxable_income)'
                    )
                else:
                    # Fixed amount
                    SalaryDetail.objects.create(
                        salary_structure=structure,
                        salary_component=component,
                        amount=Decimal(str(amount)),
                        formula=''
                    )
            except SalaryComponent.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  [!] Component {comp_code} not found'))

        return structure

    def print_summary(self, structures):
        """Print summary of created structures"""
        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING('SALARY STRUCTURES SUMMARY'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))

        # Group by company/category
        by_category = {}
        for structure in structures:
            category = structure.company
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(structure)

        for category, structs in sorted(by_category.items()):
            self.stdout.write(self.style.SUCCESS(f'\n{category}:'))
            for struct in structs:
                # Calculate approximate monthly salary
                earnings = struct.salary_details.filter(
                    salary_component__component_type='EARNING',
                    salary_component__code__in=['BASIC', 'HRA', 'TRANSPORT', 'MEAL', 'PHONE']
                )
                total = sum(detail.amount for detail in earnings)

                self.stdout.write(f'  * {struct.name}')
                self.stdout.write(f'    Base Package: ~KHR {total:,.0f}')
                self.stdout.write(f'    Components: {earnings.count()} fixed + variable')

        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(f'Total Structures Created: {len(structures)}')
        self.stdout.write(self.style.WARNING('='*80 + '\n'))

        self.stdout.write(self.style.SUCCESS('\n>> Usage Examples:\n'))
        self.stdout.write('1. Assign to employees via Admin Panel:')
        self.stdout.write('   >> Admin > Salary Structure Assignments\n')
        self.stdout.write('2. Generate salary slips using these structures:')
        self.stdout.write('   >> Admin > Payroll > Salary Slips\n')
        self.stdout.write('3. View salary structure details:')
        self.stdout.write('   >> http://kk.lyp:8000/payroll/salary-structures/\n')
