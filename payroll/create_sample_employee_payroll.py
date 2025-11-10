"""
Complete Sample Employee and Payroll Data Generator
Creates a complete employee with payroll data matching the payslip image.

Usage:
    python manage.py shell
    >>> exec(open('payroll/create_sample_employee_payroll.py').read())
"""

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.db import transaction
from hr.models import Employee, Department, Position
from payroll.models import (
    SalaryComponent, SalaryStructure, SalaryDetail,
    SalaryStructureAssignment, SalarySlip, SalarySlipDetail,
    PayrollPeriod, EmployeeSalary
)


def create_or_get_department():
    """Create or get Technical department"""
    department, created = Department.objects.get_or_create(
        code='TECH',
        defaults={
            'name': 'Technical',
            'description': 'Technical Department'
        }
    )
    if created:
        print(f"✓ Created department: {department.name}")
    else:
        print(f"- Using existing department: {department.name}")
    return department


def create_or_get_position(department):
    """Create or get Manager, Technical position"""
    position, created = Position.objects.get_or_create(
        code='MGR-TECH',
        defaults={
            'name': 'Manager, Technical',
            'department': department,
            'description': 'Technical Manager Position',
            'level': 3
        }
    )
    if created:
        print(f"✓ Created position: {position.name}")
    else:
        print(f"- Using existing position: {position.name}")
    return position


def create_sample_user():
    """Create a sample user for the employee"""
    username = 'soeng.kanel'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': 'Soeng',
            'last_name': 'Kanel',
            'email': 'soeng.kanel@nextgdt.com',
            'is_active': True
        }
    )

    if created:
        user.set_password('password123')
        user.save()
        print(f"✓ Created user: {username} (password: password123)")
    else:
        print(f"- Using existing user: {username}")

    return user


def create_sample_employee(user, department, position):
    """Create a sample employee matching the payslip"""
    try:
        employee = Employee.objects.get(employee_id='NGT015')
        print(f"- Using existing employee: {employee.get_full_name()}")
        return employee
    except Employee.DoesNotExist:
        pass

    employee = Employee.objects.create(
        user=user,
        employee_id='NGT015',
        first_name='Soeng',
        last_name='Kanel',

        # Personal Information
        national_id='110536304',
        date_of_birth=date(1990, 5, 15),
        gender='M',
        nationality='KH',
        marital_status='Married',

        # Contact Information
        phone_number='087845111',
        email='soeng.kanel@nextgdt.com',
        current_address='#F 31, St. 136.04, Talei, Dangkor, Dangkor, Phnom Penh , Phnom Penh',
        permanent_address='#F 31, St. 136.04, Talei, Dangkor, Dangkor, Phnom Penh , Phnom Penh',

        # Employment Information
        department=department,
        position=position,
        employment_status='active',
        hire_date=date(2023, 1, 15),

        # Additional fields
        is_active=True,
        number_of_dependents=2,  # Spouse + 2 children = 2 dependents
    )

    print(f"✓ Created employee: {employee.get_full_name()} (ID: {employee.employee_id})")
    return employee


def create_employee_salary(employee):
    """Create salary information for the employee"""
    salary, created = EmployeeSalary.objects.get_or_create(
        employee=employee,
        defaults={
            'basic_salary': Decimal('1900.00'),
            'housing_allowance': Decimal('0.00'),
            'transport_allowance': Decimal('0.00'),
            'meal_allowance': Decimal('40.00'),
            'phone_allowance': Decimal('0.00'),
            'seniority_allowance': Decimal('0.00'),
            'bank_name': 'ACLEDA Bank',
            'bank_account_number': '1234567890',
            'bank_account_name': 'SOENG KANEL',
            'payment_method': 'BANK',
            'effective_date': date(2023, 1, 15),
            'is_active': True
        }
    )

    if created:
        print(f"✓ Created salary info: Base ${salary.basic_salary}")
    else:
        print(f"- Using existing salary info")

    return salary


def create_salary_components():
    """Create all necessary salary components"""
    print("\nCreating salary components...")

    components_data = [
        # Earnings
        {
            'code': 'BASIC',
            'name': 'Basic Pay',
            'abbreviation': 'BASIC',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': True,
            'is_payable': True,
            'display_order': 1
        },
        {
            'code': 'MEAL_ALLOW',
            'name': 'Meal Allowance',
            'abbreviation': 'MEAL',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'is_payable': True,
            'display_order': 2
        },
        {
            'code': 'LEAVE_ALLOW',
            'name': 'Leave Allowance',
            'abbreviation': 'LEAVE',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'is_payable': True,
            'display_order': 3
        },
        {
            'code': 'OVERTIME',
            'name': 'Overtime Pay',
            'abbreviation': 'OT',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': True,
            'is_payable': True,
            'display_order': 4
        },
        {
            'code': 'ADJUSTMENT',
            'name': 'Adjustment ()',
            'abbreviation': 'ADJ',
            'component_type': 'EARNING',
            'calculation_type': 'FIXED',
            'is_tax_applicable': True,
            'is_payable': True,
            'display_order': 5
        },
        # Deductions
        {
            'code': 'UNPAID_LEAVE',
            'name': 'Unpaid Leave',
            'abbreviation': 'UL',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'depends_on_payment_days': True,
            'is_tax_applicable': False,
            'is_payable': True,
            'display_order': 10
        },
        {
            'code': 'LATE_DEDUCT',
            'name': 'Late Deduction',
            'abbreviation': 'LATE',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'is_payable': True,
            'display_order': 11
        },
        {
            'code': 'PENSION',
            'name': 'Pension Fund',
            'abbreviation': 'PENSION',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'is_payable': True,
            'display_order': 12
        },
        {
            'code': 'TAX_SALARY',
            'name': 'Tax on Salary (TOS)',
            'abbreviation': 'TAX',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'variable_based_on_taxable_salary': True,
            'is_payable': True,
            'display_order': 13
        },
        {
            'code': 'TAX_BENEFIT',
            'name': 'Tax on Benefit',
            'abbreviation': 'TAX-B',
            'component_type': 'DEDUCTION',
            'calculation_type': 'FIXED',
            'is_tax_applicable': False,
            'is_payable': True,
            'display_order': 14
        },
    ]

    components = []
    for comp_data in components_data:
        component, created = SalaryComponent.objects.get_or_create(
            code=comp_data['code'],
            defaults=comp_data
        )
        if created:
            print(f"  ✓ Created: {component.name}")
        else:
            print(f"  - Exists: {component.name}")
        components.append(component)

    return components


def create_salary_structure():
    """Create salary structure with components"""
    print("\nCreating salary structure...")

    structure, created = SalaryStructure.objects.get_or_create(
        name='NGT Standard Structure',
        defaults={
            'company': 'Next Generation Technology',
            'is_active': True,
            'docstatus': 1
        }
    )

    if created:
        print(f"✓ Created structure: {structure.name}")
    else:
        print(f"- Using existing structure: {structure.name}")

    # Add components to structure
    components_config = [
        ('BASIC', Decimal('950.00')),
        ('MEAL_ALLOW', Decimal('40.00')),
        ('LEAVE_ALLOW', Decimal('0.00')),
        ('OVERTIME', Decimal('0.00')),
        ('ADJUSTMENT', Decimal('0.00')),
        ('UNPAID_LEAVE', Decimal('0.00')),
        ('LATE_DEDUCT', Decimal('0.00')),
        ('PENSION', Decimal('5.99')),
        ('TAX_SALARY', Decimal('138.23')),
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
                print(f"  ✓ Added: {component.name} = ${amount}")
        except SalaryComponent.DoesNotExist:
            print(f"  ✗ Component not found: {code}")

    return structure


def create_payroll_period():
    """Create payroll period"""
    print("\nCreating payroll period...")

    # September 16-30, 2025
    start_date = date(2025, 9, 16)
    end_date = date(2025, 9, 30)
    payment_date = date(2025, 9, 30)

    period, created = PayrollPeriod.objects.get_or_create(
        start_date=start_date,
        end_date=end_date,
        defaults={
            'name': 'September 2025 - Period 2',
            'period_type': 'SEMI_MONTHLY',
            'payment_date': payment_date,
            'status': 'APPROVED',
            'created_by': User.objects.first()
        }
    )

    if created:
        print(f"✓ Created period: {period.name}")
    else:
        print(f"- Using existing period: {period.name}")

    return period


def create_salary_structure_assignment(employee, structure):
    """Assign salary structure to employee"""
    print("\nCreating salary structure assignment...")

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
        print(f"✓ Assigned structure to {employee.get_full_name()}")
    else:
        print(f"- Assignment already exists")

    return assignment


def create_salary_slip(employee, period, structure):
    """Create salary slip with exact values from image"""
    print("\nCreating salary slip...")

    # Check if salary slip already exists
    try:
        salary_slip = SalarySlip.objects.get(
            employee=employee,
            payroll_period=period
        )
        print(f"- Salary slip already exists (ID: {salary_slip.id})")
        return salary_slip
    except SalarySlip.DoesNotExist:
        pass

    # Create salary slip
    salary_slip = SalarySlip.objects.create(
        employee=employee,
        payroll_period=period,
        salary_structure=structure,
        start_date=period.start_date,
        end_date=period.end_date,
        posting_date=date.today(),
        total_working_days=22,
        payment_days=22,
        leave_without_pay=0,
        base_salary=Decimal('1900.00'),
        status='APPROVED',
        docstatus=1,
        created_by=User.objects.first()
    )

    print(f"✓ Created salary slip (ID: {salary_slip.id})")

    # Create salary slip details manually to match the image exactly
    details_data = [
        # Earnings
        ('BASIC', Decimal('950.00')),
        ('MEAL_ALLOW', Decimal('40.00')),
        # Deductions
        ('PENSION', Decimal('5.99')),
        ('TAX_SALARY', Decimal('138.23')),
        ('TAX_BENEFIT', Decimal('8.00')),
    ]

    print("\nAdding salary components:")
    for code, amount in details_data:
        try:
            component = SalaryComponent.objects.get(code=code)
            detail = SalarySlipDetail.objects.create(
                salary_slip=salary_slip,
                salary_component=component,
                amount=amount,
                default_amount=amount
            )
            print(f"  ✓ {component.name}: ${amount}")
        except SalaryComponent.DoesNotExist:
            print(f"  ✗ Component not found: {code}")

    # Calculate totals
    salary_slip.gross_pay = Decimal('990.00')  # 950 + 40
    salary_slip.total_deduction = Decimal('152.22')  # 5.99 + 138.23 + 8.00
    salary_slip.net_pay = Decimal('837.78')  # 990 - 152.22
    salary_slip.rounded_total = Decimal('837.78')
    salary_slip.save()

    print(f"\n✓ Salary slip calculations:")
    print(f"  - Gross Pay: ${salary_slip.gross_pay}")
    print(f"  - Total Deductions: ${salary_slip.total_deduction}")
    print(f"  - Net Pay: ${salary_slip.net_pay}")

    return salary_slip


@transaction.atomic
def main():
    """Main function to create complete sample data"""
    print("=" * 70)
    print("SAMPLE EMPLOYEE AND PAYROLL GENERATOR")
    print("=" * 70)
    print()

    try:
        # Step 1: Create department and position
        print("Step 1: Creating organizational structure...")
        department = create_or_get_department()
        position = create_or_get_position(department)

        # Step 2: Create user
        print("\nStep 2: Creating user account...")
        user = create_sample_user()

        # Step 3: Create employee
        print("\nStep 3: Creating employee...")
        employee = create_sample_employee(user, department, position)

        # Step 4: Create employee salary
        print("\nStep 4: Creating salary information...")
        create_employee_salary(employee)

        # Step 5: Create salary components
        create_salary_components()

        # Step 6: Create salary structure
        structure = create_salary_structure()

        # Step 7: Create payroll period
        period = create_payroll_period()

        # Step 8: Create salary structure assignment
        create_salary_structure_assignment(employee, structure)

        # Step 9: Create salary slip
        salary_slip = create_salary_slip(employee, period, structure)

        # Success!
        print("\n" + "=" * 70)
        print("✅ SUCCESS! SAMPLE DATA CREATED")
        print("=" * 70)
        print()
        print("Employee Details:")
        print(f"  Name: {employee.get_full_name()}")
        print(f"  Employee ID: {employee.employee_id}")
        print(f"  National ID: {employee.national_id}")
        print(f"  Department: {employee.department.name}")
        print(f"  Position: {employee.position.name}")
        print()
        print("Salary Slip Details:")
        print(f"  Salary Slip ID: {salary_slip.id}")
        print(f"  Period: {period.name}")
        print(f"  Gross Pay: ${salary_slip.gross_pay}")
        print(f"  Net Pay: ${salary_slip.net_pay}")
        print()
        print("🎉 You can now view the payslip at:")
        print(f"  👉 /payroll/salary-slip/{salary_slip.id}/")
        print()
        print("Login credentials:")
        print(f"  Username: {user.username}")
        print(f"  Password: password123")
        print()

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR CREATING SAMPLE DATA")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        print()


if __name__ == '__main__':
    main()
