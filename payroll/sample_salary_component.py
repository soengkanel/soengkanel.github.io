#!/usr/bin/env python
"""
Sample Salary Component Generator based on Project Worker Timesheets

This script generates salary components for project workers based on their timesheet data.
It calculates earnings from:
    pass
- Regular hours worked
- Overtime hours
- Project-specific rates
- Different pay types (Normal, PH, OT, Weekend)

Usage:
    # Best method - using Django shell exec
    python manage.py shell -c "exec(open('payroll/sample_salary_component.py').read())"

    # Or using django-extensions runscript
    python manage.py runscript sample_salary_component --dir payroll

    # Or import in Django shell
    python manage.py shell
    >>> from payroll.sample_salary_component import run
    >>> run()

For multi-tenant setup:
    Uses django-tenants schema context
"""

from decimal import Decimal
from datetime import date, datetime, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone

# Import models
from project.models import (
    Project, ProjectTeamMember, Timesheet, TimesheetDetail,
    ActivityTypeMaster
)
from hr.models import Employee
from payroll.models import (
    SalaryComponent, SalaryStructure, SalaryDetail,
    SalaryStructureAssignment, SalarySlip, SalarySlipDetail,
    AdditionalSalary, PayrollPeriod
)
from django.contrib.auth.models import User


class SalaryComponentGenerator:
    """Generate salary components based on project timesheet data"""

    def __init__(self, tenant_schema=None):
        self.tenant_schema = tenant_schema
        self.created_components = []
        self.created_structures = []
        self.created_slips = []

    def run(self):
        """Main execution method"""
        print("=" * 70)
        print("SALARY COMPONENT GENERATOR - Based on Project Timesheets")
        print("=" * 70)

        if self.tenant_schema:
            from django_tenants.utils import schema_context
            with schema_context(self.tenant_schema):
                return self._execute()
        else:
            return self._execute()

    def _execute(self):
        """Execute the generation process"""
        # Step 1: Create base salary components
        print("\n[Step 1] Creating Base Salary Components...")
        self._create_base_components()

        # Step 2: Create project-specific components
        print("\n[Step 2] Creating Project-Specific Components...")
        self._create_project_components()

        # Step 3: Create timesheet-based components
        print("\n[Step 3] Creating Timesheet-Based Components...")
        self._create_timesheet_components()

        # Step 4: Create salary structures for project workers
        print("\n[Step 4] Creating Salary Structures for Project Workers...")
        self._create_worker_salary_structures()

        # Step 5: Generate sample salary slips
        print("\n[Step 5] Generating Sample Salary Slips...")
        self._generate_sample_salary_slips()

        # Step 6: Display summary
        self._display_summary()

        return True

    def _create_base_components(self):
        """Create base salary components for project workers"""
        base_components = [
            {
                'code': 'BASE_RATE',
                'name': 'Base Daily Rate',
                'abbreviation': 'BASE',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_payable': True,
                'depends_on_payment_days': True,
                'is_tax_applicable': True,
                'description': 'Base daily rate for project workers',
                'display_order': 1
            },
            {
                'code': 'OT_PAY',
                'name': 'Overtime Pay',
                'abbreviation': 'OT',
                'component_type': 'EARNING',
                'calculation_type': 'FORMULA',
                'formula': 'base * 1.5',  # 1.5x base rate
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'description': 'Overtime payment at 1.5x rate',
                'display_order': 2
            },
            {
                'code': 'PH_PAY',
                'name': 'Public Holiday Pay',
                'abbreviation': 'PH',
                'component_type': 'EARNING',
                'calculation_type': 'FORMULA',
                'formula': 'base * 2.0',  # 2.0x base rate
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'description': 'Public holiday pay at 2.0x rate',
                'display_order': 3
            },
            {
                'code': 'WEEKEND_PAY',
                'name': 'Weekend Pay',
                'abbreviation': 'WKD',
                'component_type': 'EARNING',
                'calculation_type': 'FORMULA',
                'formula': 'base * 1.5',  # 1.5x base rate
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'description': 'Weekend work pay at 1.5x rate',
                'display_order': 4
            },
            {
                'code': 'TIMESHEET_HOURS',
                'name': 'Timesheet Hours',
                'abbreviation': 'TS_HRS',
                'component_type': 'EARNING',
                'calculation_type': 'FORMULA',
                'formula': 'base * (total_hours / 8)',  # Hourly calculation
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'description': 'Payment based on timesheet hours',
                'display_order': 5
            },
            {
                'code': 'PROJECT_BONUS',
                'name': 'Project Completion Bonus',
                'abbreviation': 'PROJ_BON',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'is_additional_component': True,
                'description': 'Bonus for project completion',
                'display_order': 6
            },
            {
                'code': 'BILLABLE_HOURS',
                'name': 'Billable Hours Incentive',
                'abbreviation': 'BILL_INC',
                'component_type': 'EARNING',
                'calculation_type': 'FORMULA',
                'formula': 'base * 0.1 * (billable_hours / total_hours)',  # 10% of base for billable work
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'description': 'Incentive for billable hours',
                'display_order': 7
            },
            {
                'code': 'TRANSPORT',
                'name': 'Transport Allowance',
                'abbreviation': 'TRANS',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_payable': True,
                'depends_on_payment_days': True,
                'is_tax_applicable': False,
                'description': 'Daily transport allowance',
                'display_order': 8
            },
            {
                'code': 'MEAL',
                'name': 'Meal Allowance',
                'abbreviation': 'MEAL',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_payable': True,
                'depends_on_payment_days': True,
                'is_tax_applicable': False,
                'description': 'Daily meal allowance',
                'display_order': 9
            },
        ]

        for comp_data in base_components:
            component, created = SalaryComponent.objects.get_or_create(
                code=comp_data['code'],
                defaults=comp_data
            )

            if created:
                self.created_components.append(component)
                print(f"  [+] Created: {component.code} - {component.name}")
            else:
                print(f"  [*] Exists: {component.code} - {component.name}")

    def _create_project_components(self):
        """Create project-specific salary components"""
        # Get active projects
        projects = Project.objects.filter(status__in=['in_progress', 'open'])[:5]

        for project in projects:
            comp_data = {
                'code': f'PROJ_{project.id}',
                'name': f'Project: {project.project_name[:30]}',
                'abbreviation': f'P{project.id}',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': True,
                'is_additional_component': True,
                'description': f'Project-specific payment for {project.project_code}',
                'display_order': 100 + project.id
            }

            component, created = SalaryComponent.objects.get_or_create(
                code=comp_data['code'],
                defaults=comp_data
            )

            if created:
                self.created_components.append(component)
                print(f"  [+] Created: {component.code} - {component.name}")

    def _create_timesheet_components(self):
        """Create components based on activity types from timesheets"""
        activity_types = ActivityTypeMaster.objects.filter(is_active=True)

        for idx, activity in enumerate(activity_types):
            comp_data = {
                'code': f'ACT_{idx+1}',
                'name': f'Activity: {activity.activity_name}',
                'abbreviation': f'ACT{idx+1}',
                'component_type': 'EARNING',
                'calculation_type': 'FORMULA',
                'formula': f'base * (activity_hours / 8)',
                'is_payable': True,
                'depends_on_payment_days': False,
                'is_tax_applicable': activity.is_billable,
                'description': f'Payment for {activity.activity_name} hours',
                'display_order': 200 + idx
            }

            component, created = SalaryComponent.objects.get_or_create(
                code=comp_data['code'],
                defaults=comp_data
            )

            if created:
                self.created_components.append(component)
                print(f"  [+] Created: {component.code} - {component.name}")

    def _create_worker_salary_structures(self):
        """Create salary structures for project workers based on their team memberships"""
        # Get project team members
        team_members = ProjectTeamMember.objects.filter(
            is_active=True
        ).select_related('employee', 'project')

        print(f"\n  Found {team_members.count()} active project team members")

        for member in team_members[:10]:  # Limit to 10 for sample
            # Create salary structure
            structure_name = f"{member.employee.full_name} - {member.project.project_code}"

            structure, created = SalaryStructure.objects.get_or_create(
                name=structure_name,
                defaults={
                    'is_active': True,
                    'docstatus': 1,  # Submitted
                    'salary_slip_based_on_timesheet': True,
                    'hour_rate': member.daily_rate_usd or Decimal('50.00')
                }
            )

            if created:
                self.created_structures.append(structure)
                print(f"  [+] Created structure: {structure.name}")

                # Add components to structure
                base_rate = SalaryComponent.objects.filter(code='BASE_RATE').first()
                ot_pay = SalaryComponent.objects.filter(code='OT_PAY').first()
                timesheet_hours = SalaryComponent.objects.filter(code='TIMESHEET_HOURS').first()
                transport = SalaryComponent.objects.filter(code='TRANSPORT').first()
                meal = SalaryComponent.objects.filter(code='MEAL').first()

                if base_rate:
                    SalaryDetail.objects.get_or_create(
                        salary_structure=structure,
                        salary_component=base_rate,
                        defaults={
                            'amount': member.daily_rate_usd or Decimal('50.00')
                        }
                    )

                if ot_pay:
                    SalaryDetail.objects.get_or_create(
                        salary_structure=structure,
                        salary_component=ot_pay,
                        defaults={'amount': Decimal('0')}
                    )

                if timesheet_hours:
                    SalaryDetail.objects.get_or_create(
                        salary_structure=structure,
                        salary_component=timesheet_hours,
                        defaults={'amount': Decimal('0')}
                    )

                if transport:
                    SalaryDetail.objects.get_or_create(
                        salary_structure=structure,
                        salary_component=transport,
                        defaults={'amount': Decimal('5.00')}
                    )

                if meal:
                    SalaryDetail.objects.get_or_create(
                        salary_structure=structure,
                        salary_component=meal,
                        defaults={'amount': Decimal('10.00')}
                    )

                # Create salary structure assignment
                assignment, assign_created = SalaryStructureAssignment.objects.get_or_create(
                    employee=member.employee,
                    from_date=member.start_date or date.today(),
                    defaults={
                        'salary_structure': structure,
                        'base_salary': member.daily_rate_usd or Decimal('50.00'),
                        'is_active': True,
                        'docstatus': 1
                    }
                )

                if assign_created:
                    print(f"    [+] Assigned to {member.employee.full_name}")

    def _generate_sample_salary_slips(self):
        """Generate sample salary slips based on timesheet data"""
        # Get current month
        today = date.today()
        start_date = today.replace(day=1)

        # Get or create payroll period
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        period, period_created = PayrollPeriod.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            defaults={
                'name': f"{start_date.strftime('%B %Y')} - Project Workers",
                'period_type': 'MONTHLY',
                'payment_date': (start_date + timedelta(days=32)).replace(day=5),
                'status': 'DRAFT'
            }
        )

        if period_created:
            print(f"  [+] Created payroll period: {period.name}")

        # Get employees with salary structure assignments
        assignments = SalaryStructureAssignment.objects.filter(
            is_active=True,
            docstatus=1,
            from_date__lte=today
        ).select_related('employee', 'salary_structure')[:5]  # Limit to 5 for sample

        for assignment in assignments:
            employee = assignment.employee

            # Get timesheet data for employee
            timesheets = Timesheet.objects.filter(
                employee=employee,
                start_date__gte=start_date,
                status__in=['submitted', 'approved']
            )

            total_hours = timesheets.aggregate(total=Sum('total_hours'))['total'] or Decimal('0')
            billable_hours = timesheets.aggregate(total=Sum('total_billable_hours'))['total'] or Decimal('0')

            # Calculate working days (assuming 8 hours per day)
            payment_days = int(total_hours / 8) if total_hours > 0 else 0

            # Create salary slip
            slip, slip_created = SalarySlip.objects.get_or_create(
                employee=employee,
                payroll_period=period,
                defaults={
                    'salary_structure': assignment.salary_structure,
                    'start_date': start_date,
                    'end_date': period.end_date,
                    'total_working_days': 22,
                    'payment_days': payment_days,
                    'base_salary': assignment.base_salary,
                    'total_working_hours': total_hours,
                    'hour_rate': assignment.salary_structure.hour_rate,
                    'status': 'CALCULATED',
                    'docstatus': 0
                }
            )

            if slip_created:
                self.created_slips.append(slip)
                print(f"  [+] Created slip for {employee.full_name}")

                # Calculate salary from structure
                slip.calculate_from_salary_structure()

                # Add timesheet-based components
                timesheet_comp = SalaryComponent.objects.filter(code='TIMESHEET_HOURS').first()
                if timesheet_comp and total_hours > 0:
                    amount = (assignment.base_salary / 8) * total_hours  # Hourly rate * hours

                    detail, detail_created = SalarySlipDetail.objects.get_or_create(
                        salary_slip=slip,
                        salary_component=timesheet_comp,
                        defaults={'amount': amount}
                    )

                    if not detail_created:
                        detail.amount = amount
                        detail.save()

                # Add billable hours incentive
                billable_comp = SalaryComponent.objects.filter(code='BILLABLE_HOURS').first()
                if billable_comp and billable_hours > 0:
                    incentive = assignment.base_salary * Decimal('0.1') * (billable_hours / total_hours if total_hours > 0 else 0)

                    SalarySlipDetail.objects.get_or_create(
                        salary_slip=slip,
                        salary_component=billable_comp,
                        defaults={'amount': incentive}
                    )

                # Recalculate totals
                slip.calculate_totals()

                print(f"    [$] Gross: ${slip.gross_pay}, Net: ${slip.net_pay}")

    def _display_summary(self):
        """Display summary of generated data"""
        print("\n" + "=" * 70)
        print("GENERATION SUMMARY")
        print("=" * 70)

        print(f"\n[OK] Salary Components Created: {len(self.created_components)}")
        for comp in self.created_components:
            print(f"   - {comp.code} - {comp.name} ({comp.get_component_type_display()})")

        print(f"\n[OK] Salary Structures Created: {len(self.created_structures)}")
        for structure in self.created_structures:
            print(f"   - {structure.name}")

        print(f"\n[OK] Salary Slips Generated: {len(self.created_slips)}")
        for slip in self.created_slips:
            print(f"   - {slip.employee.full_name}: ${slip.net_pay}")

        print("\n" + "=" * 70)
        print("DATABASE STATISTICS")
        print("=" * 70)
        print(f"   - Total Salary Components: {SalaryComponent.objects.count()}")
        print(f"   - Total Salary Structures: {SalaryStructure.objects.count()}")
        print(f"   - Total Salary Assignments: {SalaryStructureAssignment.objects.count()}")
        print(f"   - Total Salary Slips: {SalarySlip.objects.count()}")
        print(f"   - Total Payroll Periods: {PayrollPeriod.objects.count()}")

        print("\n" + "=" * 70)
        print("API ENDPOINTS TO TEST")
        print("=" * 70)
        print("   - Salary Components: GET http://localhost:8000/payroll/salary-components/")
        print("   - Salary Structures: GET http://localhost:8000/api/payroll/salary-structures/")
        print("   - Salary Slips: GET http://localhost:8000/api/payroll/salary-slips/")
        print("   - Timesheets: GET http://localhost:8000/api/project/timesheets/")

        print("\n[OK] Script completed successfully!")


def run(*args):
    """Entry point for django-extensions runscript"""
    tenant_schema = args[0] if args else None
    generator = SalaryComponentGenerator(tenant_schema=tenant_schema)
    generator.run()


# Allow execution when run directly
if __name__ == '__main__':
    run()
