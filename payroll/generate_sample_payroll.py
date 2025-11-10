"""
Sample Payroll Data Generator
This script creates sample salary components, salary structures, and salary slips for testing.

Usage:
    python manage.py shell < payroll/generate_sample_payroll.py
    OR
    python manage.py shell
    >>> exec(open('payroll/generate_sample_payroll.py').read())
"""

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User
from hr.models import Employee
from payroll.models import (
    SalaryComponent, SalaryStructure, SalaryDetail,
    SalaryStructureAssignment, SalarySlip, SalarySlipDetail,
    PayrollPeriod
)


def create_sample_salary_components():
    """Create sample salary components (earnings and deductions)"""
    print("Creating salary components...")

    components = [
        # Earnings
        {
            'code': 'BASIC',
            'name': 'Basic Pay',
            'abbreviation': 'BASIC',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': True,
            'display_order': 1
        },
        {
            'code': 'MEAL_ALLOW',
            'name': 'Meal Allowance',
            'abbreviation': 'MEAL',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'display_order': 2
        },
        {
            'code': 'LEAVE_ALLOW',
            'name': 'Leave Allowance',
            'abbreviation': 'LEAVE',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'display_order': 3
        },
        {
            'code': 'OVERTIME',
            'name': 'Overtime Pay',
            'abbreviation': 'OT',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': True,
            'display_order': 4
        },
        # Deductions
        {
            'code': 'PENSION',
            'name': 'Pension Fund',
            'abbreviation': 'PENSION',
            'component_type': 'DEDUCTION',
            'calculation_type': 'PERCENTAGE',
            'percentage_value': Decimal('0.63'),  # 0.63% of gross
            'is_tax_applicable': False,
            'display_order': 10
        },
        {
            'code': 'TAX',
            'name': 'Tax on Salary (TOS)',
            'abbreviation': 'TAX',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FORMULA',
            'formula': 'base * 0.10',  # Simplified 10% tax
            'is_tax_applicable': False,
            'variable_based_on_taxable_salary': True,
            'display_order': 11
        },
        {
            'code': 'TAX_BENEFIT',
            'name': 'Tax on Benefit',
            'abbreviation': 'TAX-B',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'display_order': 12
        },
        {
            'code': 'LATE_DEDUCT',
            'name': 'Late Deduction',
            'abbreviation': 'LATE',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'display_order': 13
        },
        {
            'code': 'UNPAID_LEAVE',
            'name': 'Unpaid Leave',
            'abbreviation': 'UL',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'depends_on_payment_days': True,
            'is_tax_applicable': False,
            'display_order': 14
        },
    ]

    created_components = []
    for comp_data in components:
        component, created = SalaryComponent.objects.get_or_create(
            code=comp_data['code'],
            defaults=comp_data
        )
        if created:
            print(f"  ✓ Created: {component.name}")
        else:
            print(f"  - Exists: {component.name}")
        created_components.append(component)

    return created_components


def create_sample_salary_structure():
    """Create a sample salary structure"""
    print("\nCreating salary structure...")

    structure, created = SalaryStructure.objects.get_or_create(
        name='Standard Salary Structure',
        defaults={
            'company': 'Next Generation Technology',
            'is_active': True,
            'docstatus': 1  # Submitted
        }
    )

    if created:
        print(f"  ✓ Created: {structure.name}")

        # Add salary components to structure
        components_config = [
            ('BASIC', Decimal('950.00')),  # $950 base
            ('MEAL_ALLOW', Decimal('40.00')),
            ('LEAVE_ALLOW', Decimal('0.00')),
            ('OVERTIME', Decimal('0.00')),
            ('PENSION', Decimal('5.99')),
            ('TAX', Decimal('138.23')),
            ('TAX_BENEFIT', Decimal('8.00')),
        ]

        for code, amount in components_config:
            try:
                component = SalaryComponent.objects.get(code=code)
                detail, detail_created = SalaryDetail.objects.get_or_create(
                    salary_structure=structure,
                    salary_component=component,
                    defaults={'amount': amount}
                )
                if detail_created:
                    print(f"    ✓ Added component: {component.name}")
            except SalaryComponent.DoesNotExist:
                print(f"    ✗ Component not found: {code}")
    else:
        print(f"  - Exists: {structure.name}")

    return structure


def create_sample_payroll_period():
    """Create a sample payroll period"""
    print("\nCreating payroll period...")

    # Current month
    today = date.today()
    start_date = date(today.year, today.month, 16)
    end_date = date(today.year, today.month, 30) if today.month != 2 else date(today.year, today.month, 28)
    payment_date = end_date + timedelta(days=5)

    period, created = PayrollPeriod.objects.get_or_create(
        start_date=start_date,
        end_date=end_date,
        defaults={
            'name': f'{start_date.strftime("%B %Y")} - Period 2',
            'period_type': 'SEMI_MONTHLY',
            'payment_date': payment_date,
            'status': 'APPROVED',
            'created_by': User.objects.first()
        }
    )

    if created:
        print(f"  ✓ Created: {period.name}")
    else:
        print(f"  - Exists: {period.name}")

    return period


def create_sample_salary_slip(employee=None):
    """Create a sample salary slip for an employee"""
    print("\nCreating salary slip...")

    # Get or create employee
    if not employee:
        try:
            # Try to find an existing employee
            employee = Employee.objects.filter(is_active=True).first()
            if not employee:
                print("  ✗ No active employees found. Please create an employee first.")
                return None
        except Exception as e:
            print(f"  ✗ Error finding employee: {e}")
            return None

    # Get salary structure
    structure = SalaryStructure.objects.filter(is_active=True).first()
    if not structure:
        print("  ✗ No salary structure found. Creating one...")
        structure = create_sample_salary_structure()

    # Create salary structure assignment
    assignment, created = SalaryStructureAssignment.objects.get_or_create(
        employee=employee,
        salary_structure=structure,
        from_date=date(2025, 1, 1),
        defaults={
            'base_salary': Decimal('1900.00'),
            'is_active': True,
            'docstatus': 1
        }
    )

    if created:
        print(f"  ✓ Created assignment for: {employee.get_full_name()}")

    # Get payroll period
    period = PayrollPeriod.objects.filter(status='APPROVED').first()
    if not period:
        print("  Creating payroll period...")
        period = create_sample_payroll_period()

    # Create salary slip
    salary_slip, created = SalarySlip.objects.get_or_create(
        employee=employee,
        payroll_period=period,
        defaults={
            'salary_structure': structure,
            'start_date': period.start_date,
            'end_date': period.end_date,
            'posting_date': date.today(),
            'total_working_days': 22,
            'payment_days': 22,
            'leave_without_pay': 0,
            'base_salary': Decimal('1900.00'),
            'status': 'APPROVED',
            'docstatus': 1,
            'created_by': User.objects.first()
        }
    )

    if created:
        print(f"  ✓ Created salary slip for: {employee.get_full_name()}")

        # Calculate from salary structure
        salary_slip.calculate_from_salary_structure()
        print(f"  ✓ Calculated salary components")
        print(f"    - Gross Pay: ${salary_slip.gross_pay}")
        print(f"    - Total Deductions: ${salary_slip.total_deduction}")
        print(f"    - Net Pay: ${salary_slip.net_pay}")
    else:
        print(f"  - Salary slip already exists for: {employee.get_full_name()}")

    return salary_slip


def main():
    """Main function to create all sample data"""
    print("=" * 60)
    print("PAYROLL SAMPLE DATA GENERATOR")
    print("=" * 60)

    # Step 1: Create salary components
    create_sample_salary_components()

    # Step 2: Create salary structure
    create_sample_salary_structure()

    # Step 3: Create payroll period
    create_sample_payroll_period()

    # Step 4: Create salary slip for first active employee
    salary_slip = create_sample_salary_slip()

    print("\n" + "=" * 60)
    if salary_slip:
        print("✓ SAMPLE DATA CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nYou can view the payslip at:")
        print(f"  /payroll/salary-slip/{salary_slip.id}/")
        print("\nOr in Django admin, go to:")
        print("  Payroll → Salary Slips")
    else:
        print("✗ FAILED TO CREATE SAMPLE DATA")
        print("=" * 60)
        print("\nPlease ensure you have at least one active employee in the system.")
    print()


if __name__ == '__main__':
    main()
