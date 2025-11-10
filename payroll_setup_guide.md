# Payroll Setup Guide

## Overview

Before you can generate payroll for employees, you must complete the following setup steps **in order**. The system will validate these prerequisites and guide you through any missing requirements.

---

## Required Setup Steps

```
Step 1: Salary Components
         ↓
Step 2: Salary Structures
         ↓
Step 3: Salary Structure Assignments
         ↓
Step 4: Create Payroll Period
         ↓
Step 5: Generate Payroll
```

---

## Step 1: Create Salary Components

**What are Salary Components?**
Salary components are the building blocks of a salary calculation. They define individual elements like basic salary, allowances, and deductions.

### Components You Need to Create:

#### A. Earnings (Income)
- **Basic Salary** - The base salary amount
- **Housing Allowance** - Housing/accommodation allowance
- **Transport Allowance** - Transportation allowance
- **Meal Allowance** - Meal/food allowance
- **Phone Allowance** - Communication allowance
- **Seniority Allowance** - Based on years of service
- **Position Allowance** - Based on job position

#### B. Deductions (Subtractions)
- **NSSF Employee** - Employee's NSSF contribution (3.5%)
- **Tax** - Salary tax based on progressive tax slabs
- **Loan Deduction** - Employee loan repayment
- **Advance Deduction** - Salary advance repayment

#### C. Employer Contributions (Not deducted from employee)
- **NSSF Employer** - Employer's NSSF contribution

### How to Create:

1. Navigate to: **Payroll > Salary Components**
2. Click **"Create Salary Component"**
3. Fill in details:
   - **Code**: Unique identifier (e.g., BASIC, HOUSING_ALLOWANCE)
   - **Name**: Display name (e.g., "Basic Salary")
   - **Component Type**: EARNING or DEDUCTION
   - **Calculation Type**: FIXED, PERCENTAGE, or FORMULA
   - **Is Tax Applicable**: Check if this component is taxable
   - **Is Active**: Must be checked

### Example: Creating Basic Salary Component

```
Code: BASIC_SALARY
Name: Basic Salary
Component Type: EARNING
Calculation Type: FIXED
Is Tax Applicable: ✓ Yes
Depends on Payment Days: ✓ Yes
Is Active: ✓ Yes
Display Order: 1
```

### Example: Creating NSSF Deduction

```
Code: NSSF_EMPLOYEE
Name: NSSF Employee Contribution
Component Type: DEDUCTION
Calculation Type: FORMULA
Formula: (Leave blank - handled by calculate_nssf() method)
Is Tax Applicable: ✗ No
Is Active: ✓ Yes
Display Order: 100
```

**Location**: `http://kk.lyp:8000/payroll/salary-components/`

---

## Step 2: Create Salary Structures

**What are Salary Structures?**
A salary structure is a template that combines multiple salary components together. It defines which components apply to employees using this structure and how they're calculated.

### How to Create:

1. Navigate to: **Payroll > Salary Structures**
2. Click **"Create Salary Structure"**
3. Fill in basic information:
   - **Name**: e.g., "Standard Employee Structure"
   - **Company**: Your company name
   - **Is Active**: Must be checked
   - **Docstatus**: Set to 1 (Submitted) when ready

4. Add Salary Components (Salary Details):
   - Click **"Add Component"** for each component
   - Select the salary component
   - Set the amount or formula
   - Save each detail

### Example Salary Structure

**Name**: Standard Employee Structure

**Earnings:**
| Component | Amount/Formula | Note |
|-----------|---------------|------|
| Basic Salary | base | Uses employee's base salary |
| Housing Allowance | base * 0.20 | 20% of base salary |
| Transport Allowance | base * 0.10 | 10% of base salary |
| Meal Allowance | 200000 | Fixed KHR 200,000 |
| Phone Allowance | 50000 | Fixed KHR 50,000 |

**Deductions:**
| Component | Amount/Formula | Note |
|-----------|---------------|------|
| NSSF Employee | (calculated) | 3.5% capped at KHR 1,300,000 |
| Tax | (calculated) | Progressive tax based on taxable income |

### Formula Context Variables

When writing formulas, you can use:
- `base` or `basic` - Employee's base salary
- `gross` or `gross_pay` - Total earnings
- `working_days` - Total working days in period
- `payment_days` - Days employee will be paid for
- `lwp_days` - Leave without pay days

**Example Formulas:**
- `base * 0.15` - 15% of base salary
- `gross * 0.05` - 5% of gross salary
- `base * payment_days / working_days` - Prorated base salary

**Location**: `http://kk.lyp:8000/payroll/salary-structures/`

---

## Step 3: Assign Salary Structures to Employees

**What are Salary Structure Assignments?**
Assignments link employees to salary structures and define their base salary amount and effective dates.

### How to Create:

1. Navigate to: **Payroll > Salary Structure Assignments**
2. Click **"Create Assignment"**
3. Fill in details:
   - **Employee**: Select the employee
   - **Salary Structure**: Select the structure created in Step 2
   - **From Date**: When this salary becomes effective
   - **To Date**: (Optional) When this salary ends
   - **Base Salary**: The employee's base amount (e.g., KHR 1,000,000)
   - **Is Active**: Must be checked ✓
   - **Docstatus**: Set to 1 (Submitted) to activate

### Important Notes:

- **Docstatus must be 1 (Submitted)** for the assignment to be used in payroll generation
- Each employee can have multiple assignments over time (salary changes)
- The system uses the assignment where `from_date <= payroll_period.end_date`
- Only active assignments with docstatus=1 are considered

### Example Assignment

```
Employee: John Doe (EMP001)
Salary Structure: Standard Employee Structure
From Date: 2025-01-01
To Date: (blank - ongoing)
Base Salary: 1,500,000 KHR
Is Active: ✓ Yes
Docstatus: 1 (Submitted)
```

**Result**: John Doe will receive:
- Basic Salary: 1,500,000 KHR
- Housing Allowance: 300,000 KHR (20%)
- Transport Allowance: 150,000 KHR (10%)
- Meal Allowance: 200,000 KHR
- Phone Allowance: 50,000 KHR
- **Gross**: 2,200,000 KHR
- Minus NSSF: ~77,000 KHR
- Minus Tax: (calculated based on taxable income)

**Location**: `http://kk.lyp:8000/payroll/salary-structure-assignments/`

---

## Step 4: Create Payroll Period

**What is a Payroll Period?**
A payroll period defines the time range for which you're calculating salaries (e.g., January 2025).

### How to Create:

1. Navigate to: **Payroll > Periods**
2. Click **"Create Period"**
3. Fill in details:
   - **Name**: e.g., "January 2025"
   - **Period Type**: MONTHLY, WEEKLY, BI_WEEKLY, or SEMI_MONTHLY
   - **Start Date**: 2025-01-01
   - **End Date**: 2025-01-31
   - **Payment Date**: 2025-02-05 (when employees get paid)
   - **Status**: DRAFT (auto-set)

### Period Features:

- **Working Days**: Auto-calculated (excludes weekends)
  - January 1-31, 2025 = 22 working days
- **Status Workflow**: DRAFT → PROCESSING → APPROVED → PAID
- **Validation**: Prevents overlapping period dates

**Location**: `http://kk.lyp:8000/payroll/periods/`

---

## Step 5: Generate Payroll

**What happens when you generate payroll?**
The system creates individual salary slips for each employee based on their assigned salary structure.

### Prerequisites Validation:

Before generating, the system checks:

1. ✓ **Salary Components exist** (at least 1 active)
2. ✓ **Salary Structures exist** (at least 1 active)
3. ✓ **Active Employees exist** (at least 1)
4. ✓ **Employees have Assignments** (at least 1 employee with active assignment)

### If Prerequisites Not Met:

You'll see an error message with specific guidance:

```
❌ No salary components found!
   → Go to Payroll > Salary Components to create components

❌ No salary structures found!
   → Go to Payroll > Salary Structures to create structures

❌ No employees have salary structure assignments!
   → Go to Payroll > Salary Structure Assignments
```

### If Prerequisites Are Met:

1. Navigate to the period detail page: `/payroll/periods/{id}/`
2. Click **"Generate Payroll"** button
3. Confirm the action
4. Wait for processing (button shows spinner)

### What Happens During Generation:

```
FOR EACH Active Employee:
  1. Check if employee has salary structure assignment
     - Must be active
     - Must have docstatus = 1 (Submitted)
     - from_date <= period.end_date

  2. If YES:
     a) Create/Update SalarySlip for employee
     b) Set working_days from period (e.g., 22 days)
     c) Calculate salary from structure:
        - Process EARNINGS (basic, allowances)
        - Calculate GROSS PAY
        - Process DEDUCTIONS (NSSF, tax)
        - Calculate NET PAY
     d) Save salary slip

  3. If NO:
     - Skip employee (shown in warning message)

AFTER ALL EMPLOYEES:
  1. Update period status to PROCESSING
  2. Set processed_by = current user
  3. Set processed_at = now
  4. Update summary metrics:
     - total_employees
     - total_gross_pay
     - total_deductions
     - total_net_pay
```

### Success Message:

```
✓ Payroll generated: 15 new, 0 updated. Working days: 22
```

### Partial Success Message (Some Skipped):

```
⚠ Payroll generated: 12 new, 0 updated. Working days: 22
  3 employees skipped (no salary structure assignment):
  John Doe, Jane Smith, Bob Johnson
```

**Location**: Click "Generate Payroll" on period detail page

---

## Calculation Details

### How Salary is Calculated

The `calculate_from_salary_structure()` method performs these steps:

1. **Get Assignment**: Find active SalaryStructureAssignment for employee
2. **Set Base Salary**: From assignment.base_salary
3. **Calculate Working Days**: Auto-calculated from period dates (excludes weekends)
4. **Process Earnings**: Calculate each earning component using formulas
5. **Calculate Gross Pay**: Sum of all earnings
6. **Process Deductions**:
   - NSSF: 3.5% of gross (capped at KHR 1,300,000 for health care)
   - Tax: Progressive tax based on taxable income minus NSSF and dependents
7. **Process Additional Salaries**: One-time bonuses/deductions in date range
8. **Calculate Net Pay**: Gross Pay - Total Deductions

### Tax Calculation (Cambodia)

**Progressive Tax Slabs** (as configured in system):
- 0 - 1,300,000: 0%
- 1,300,001 - 2,000,000: 5%
- 2,000,001 - 8,500,000: 10%
- 8,500,001 - 12,500,000: 15%
- Above 12,500,000: 20%

**Deductions from Taxable Income**:
- Employee NSSF contribution
- 150,000 KHR per dependent (spouse + children)

### NSSF Calculation (Cambodia)

**Employee Contribution**: 3.5% of gross salary
- Occupational Risk: Capped at different amounts per contribution type
- Health Care: Capped at KHR 1,300,000

**Employer Contribution**: Separate calculation (not deducted from employee)

**Location**: Configured in `Payroll > NSSF Configuration`

---

## Troubleshooting

### Issue: "Generate Payroll" button is disabled

**Cause**: Prerequisites not met

**Solution**: Check the yellow warning box above the button for specific issues

---

### Issue: Payroll generated but amounts are zero

**Causes**:
1. Salary structure assignment docstatus is not 1 (Submitted)
2. Salary structure has no components
3. Base salary is set to 0

**Solution**:
- Edit the assignment and set docstatus to 1
- Add components to the salary structure
- Set correct base salary amount

---

### Issue: Some employees skipped during generation

**Cause**: Those employees don't have active salary structure assignments

**Solution**:
1. Go to Payroll > Salary Structure Assignments
2. Create assignment for each skipped employee
3. Set docstatus to 1 (Submitted)
4. Regenerate payroll (will update existing slips)

---

### Issue: Tax calculation seems wrong

**Causes**:
1. Tax slabs not configured correctly
2. Number of dependents not set on employee
3. NSSF not calculated before tax

**Solution**:
1. Check Payroll > Tax Slabs for correct rates
2. Update employee record with number_of_dependents
3. Ensure NSSF component exists and calculates before Tax

---

## Quick Reference URLs

| Page | URL |
|------|-----|
| Salary Components | `/payroll/salary-components/` |
| Salary Structures | `/payroll/salary-structures/` |
| Salary Assignments | `/payroll/salary-structure-assignments/` |
| Payroll Periods | `/payroll/periods/` |
| Tax Slabs | `/payroll/tax-slabs/` |
| NSSF Configuration | `/payroll/nssf-config/` |

---

## Complete Example Workflow

### Scenario: Setting up payroll for 3 employees

#### 1. Create Salary Components (10 minutes)

Create these components via `/payroll/salary-components/`:
- BASIC_SALARY (Earning, Fixed)
- HOUSING_ALLOWANCE (Earning, Percentage)
- TRANSPORT_ALLOWANCE (Earning, Percentage)
- NSSF_EMPLOYEE (Deduction, Formula)
- TAX (Deduction, Formula)

#### 2. Create Salary Structure (5 minutes)

Via `/payroll/salary-structures/`, create "Standard Structure":
- Name: Standard Employee Structure
- Company: My Company
- Add components with formulas
- Set docstatus to 1

#### 3. Assign to Employees (15 minutes)

Via `/payroll/salary-structure-assignments/`:

**Employee 1**: John Doe
- Structure: Standard Employee Structure
- Base Salary: 1,500,000 KHR
- From Date: 2025-01-01
- Docstatus: 1

**Employee 2**: Jane Smith
- Structure: Standard Employee Structure
- Base Salary: 2,000,000 KHR
- From Date: 2025-01-01
- Docstatus: 1

**Employee 3**: Bob Johnson
- Structure: Standard Employee Structure
- Base Salary: 1,800,000 KHR
- From Date: 2025-01-01
- Docstatus: 1

#### 4. Create Period (2 minutes)

Via `/payroll/periods/`, create "January 2025":
- Start: 2025-01-01
- End: 2025-01-31
- Payment: 2025-02-05

#### 5. Generate Payroll (1 minute)

Click "Generate Payroll" → Wait → Done!

**Result**: 3 salary slips created with calculated amounts

---

## Best Practices

### 1. Set Up Components Once
Create all your salary components at the beginning. You'll reuse them across multiple structures.

### 2. Use Salary Structures for Different Employee Types
- "Executive Structure" - Higher allowances
- "Manager Structure" - Medium allowances
- "Staff Structure" - Standard allowances

### 3. Set Docstatus to 1
Always remember to set docstatus to 1 (Submitted) on salary structure assignments. Draft assignments (docstatus=0) are ignored.

### 4. Test with One Employee First
Before generating payroll for all employees, test with one employee to verify calculations are correct.

### 5. Review Before Approving
After generation, review all salary slips before changing period status to APPROVED.

---

## Summary

The correct order is:

1. **Salary Components** → Building blocks
2. **Salary Structures** → Combine components into templates
3. **Salary Assignments** → Link employees to structures with base salary
4. **Payroll Period** → Define time range
5. **Generate Payroll** → Create salary slips

Each step depends on the previous one. The system will validate and guide you if any step is missing!

---

*Last Updated: November 2025*
*Version: 1.0*
