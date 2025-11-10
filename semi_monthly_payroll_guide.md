# Semi-Monthly Payroll Best Practices Guide

## ✅ AUTOMATIC IMPLEMENTATION STATUS

**Semi-monthly calculations are NOW AUTOMATICALLY IMPLEMENTED!**

When you create a period with `period_type='SEMI_MONTHLY'`, the system automatically:
- ✅ Splits monthly base salary 50/50
- ✅ Adjusts all salary component calculations
- ✅ Handles formulas correctly (no need for manual `× 0.5`)
- ✅ Works with standard salary structures

**You can use the SAME salary structure for both monthly and semi-monthly periods!**

---

## Table of Contents
1. [Understanding Semi-Monthly Payroll](#understanding-semi-monthly-payroll)
2. [Best Practices](#best-practices)
3. [Period Creation Strategy](#period-creation-strategy)
4. [Automatic Calculation (NEW!)](#automatic-calculation-new)
5. [Implementation Guide](#implementation-guide)
6. [Complete Examples](#complete-examples)
7. [Common Pitfalls](#common-pitfalls)

---

## Understanding Semi-Monthly Payroll

### What is Semi-Monthly?

**Semi-Monthly**: Employees are paid **twice per month** on specific dates
- **24 pay periods per year** (12 months × 2)
- **Common schedules**:
  - 1st and 15th of each month
  - 15th and last day of each month
  - 10th and 25th of each month

### Semi-Monthly vs Bi-Weekly

| Feature | Semi-Monthly | Bi-Weekly |
|---------|-------------|-----------|
| Pay Frequency | 2x per month (24/year) | Every 2 weeks (26/year) |
| Pay Dates | Fixed dates (15th, 30th) | Fixed day (every other Friday) |
| Working Days | Varies (10-12 per period) | Fixed (10 working days) |
| Calculation | Split monthly salary | Annualized salary ÷ 26 |
| Months with 3 Pays | Never | Twice per year |

---

## Best Practices

### ✅ Recommended Approach: **50/50 Split Method**

**Split monthly salary equally into two periods**

**Advantages**:
- ✓ Simple and predictable for employees
- ✓ Easy to calculate (monthly salary ÷ 2)
- ✓ Consistent net pay each period
- ✓ Less administrative overhead
- ✓ Easier to explain to employees

**How it works**:
```
Monthly Base Salary: 3,000,000 KHR
Period 1 (1-15): 1,500,000 KHR (50%)
Period 2 (16-31): 1,500,000 KHR (50%)
```

### Alternative Approach: **Proration by Days**

**Split based on actual calendar days**

**Use when**:
- Company policy requires day-accurate calculation
- Employees frequently join/leave mid-month
- Contract workers paid by the day

**How it works**:
```
January has 31 days
Monthly Base Salary: 3,100,000 KHR

Period 1 (1-15): 15 days
= 3,100,000 × (15/31) = 1,500,000 KHR

Period 2 (16-31): 16 days
= 3,100,000 × (16/31) = 1,600,000 KHR
```

**Note**: This creates slightly different amounts each period

---

## Period Creation Strategy

### Method 1: Two Separate Periods (Recommended)

Create **two distinct payroll periods** each month with 50/50 split.

#### January 2025 Example:

**Period 1: January 1-15, 2025**
```
Name: January 2025 - Period 1 (1-15)
Period Type: SEMI_MONTHLY
Start Date: 2025-01-01
End Date: 2025-01-15
Payment Date: 2025-01-20
Working Days: 11 (auto-calculated)
```

**Period 2: January 16-31, 2025**
```
Name: January 2025 - Period 2 (16-31)
Period Type: SEMI_MONTHLY
Start Date: 2025-01-16
End Date: 2025-01-31
Payment Date: 2025-02-05
Working Days: 11 (auto-calculated)
```

**Total Working Days**: 22 for the month

---

## Automatic Calculation (NEW!)

### How It Works

The system now **automatically detects** the period type and adjusts calculations accordingly.

#### Implementation Details (`payroll/models.py:768-828`):

```python
def calculate_from_salary_structure(self):
    # Get monthly base salary from assignment
    monthly_base_salary = assignment.base_salary  # e.g., 3,000,000 KHR

    # Automatic adjustment based on period type
    if self.payroll_period.period_type == 'SEMI_MONTHLY':
        self.base_salary = monthly_base_salary * 0.5  # = 1,500,000 KHR
        period_multiplier = 0.5
    elif self.payroll_period.period_type == 'MONTHLY':
        self.base_salary = monthly_base_salary  # = 3,000,000 KHR
        period_multiplier = 1.0

    # Formulas now use adjusted base salary
    context = {
        'base': self.base_salary,        # 1,500,000 (semi-monthly) or 3,000,000 (monthly)
        'monthly_base': monthly_base_salary,  # Always 3,000,000
        'period_multiplier': period_multiplier,  # 0.5 or 1.0
        ...
    }
```

### What This Means for You

**1. Use Standard Formulas**

You can now use **regular formulas** without manual adjustments:

```
Housing Allowance formula: base * 0.20

For MONTHLY period:
  base = 3,000,000
  Housing = 3,000,000 × 0.20 = 600,000 KHR ✓

For SEMI_MONTHLY period:
  base = 1,500,000 (automatically adjusted!)
  Housing = 1,500,000 × 0.20 = 300,000 KHR ✓
```

**2. One Salary Structure for All Period Types**

You can assign the **same salary structure** to an employee regardless of period type:

```
Salary Structure: "Standard Employee"
Formula: base * 0.20

Works for:
- Monthly periods (gets 600,000)
- Semi-monthly periods (gets 300,000 automatically)
- Weekly periods (prorated automatically)
```

**3. Context Variables Available in Formulas**

| Variable | Description | Example (Semi-Monthly) |
|----------|-------------|----------------------|
| `base` or `basic` | Auto-adjusted base salary | 1,500,000 |
| `monthly_base` | Original monthly base | 3,000,000 |
| `period_multiplier` | Multiplier for period type | 0.5 |
| `working_days` | Working days in period | 11 |
| `payment_days` | Days employee is paid | 11 |
| `gross` or `gross_pay` | Total earnings | (calculated) |

**Advanced Example**:
```
Formula: monthly_base * 0.20 * period_multiplier
```
This gives you explicit control over the calculation.

### Simplified Setup Process

**Before (Manual)**:
1. Create "Monthly Salary Structure" with `base * 0.20`
2. Create "Semi-Monthly Salary Structure" with `base * 0.20 * 0.5`
3. Assign different structures to employees based on pay frequency
4. ❌ Error-prone, complex

**Now (Automatic)**:
1. Create ONE "Standard Salary Structure" with `base * 0.20`
2. Assign it to ALL employees
3. Create monthly OR semi-monthly periods as needed
4. ✅ System automatically adjusts calculations!

---

## Calculation Methods

### Method A: 50/50 Split (Simple & Recommended)

All salary components split equally between two periods.

#### Salary Components Configuration:

**For Period 1 (1-15):**

| Component | Monthly Amount | Period 1 Amount | Formula |
|-----------|----------------|-----------------|---------|
| Basic Salary | 3,000,000 | 1,500,000 | `base * 0.5` |
| Housing Allowance | 600,000 (20%) | 300,000 | `base * 0.20 * 0.5` |
| Transport Allowance | 300,000 (10%) | 150,000 | `base * 0.10 * 0.5` |
| Meal Allowance | 200,000 | 100,000 | `100000` (fixed) |
| Phone Allowance | 50,000 | 25,000 | `25000` (fixed) |

**For Period 2 (16-31):**
Same as Period 1 (identical formulas)

#### Deductions:

**Option A: Split Monthly Deductions 50/50**
```
Monthly NSSF: 77,000 KHR
Period 1 NSSF: 38,500 KHR
Period 2 NSSF: 38,500 KHR

Monthly Tax: 150,000 KHR
Period 1 Tax: 75,000 KHR
Period 2 Tax: 75,000 KHR
```

**Pros**: Consistent net pay, simple
**Cons**: Not technically accurate (NSSF/tax rates based on period gross, not monthly)

**Option B: Calculate Deductions Per Period**
```
Period 1 Gross: 2,075,000 KHR
Period 1 NSSF: 2,075,000 × 3.5% = 72,625 KHR
Period 1 Tax: Calculate based on period taxable income

Period 2 Gross: 2,075,000 KHR
Period 2 NSSF: 2,075,000 × 3.5% = 72,625 KHR
Period 2 Tax: Calculate based on period taxable income
```

**Pros**: Technically accurate
**Cons**: More complex, net pay varies if employee has unpaid leave

---

### Method B: Proration by Working Days

Calculate based on actual working days in each period.

#### Example:
```
Monthly Base Salary: 3,000,000 KHR
Total Working Days (January): 22

Period 1 Working Days: 11
Period 1 Base: 3,000,000 × (11/22) = 1,500,000 KHR

Period 2 Working Days: 11
Period 2 Base: 3,000,000 × (11/22) = 1,500,000 KHR
```

**When to use**:
- When working days vary significantly (holidays)
- For hourly-rated employees
- Company policy requires working day accuracy

#### Component Configuration:

```python
# In salary component or formula
base * payment_days / (total_monthly_working_days)
```

**Note**: Requires knowing total monthly working days in advance

---

## Implementation Guide

### Step 1: Configure Salary Structure (Same for All Period Types!)

Create ONE salary structure: **"Standard Employee Structure"**

✅ **No need for separate semi-monthly structures!** The system automatically adjusts based on period type.

#### Earnings Configuration:

| Component | Formula | Note |
|-----------|---------|------|
| Basic Salary | `base` | Auto-adjusts: Full for monthly, 50% for semi-monthly |
| Housing Allowance | `base * 0.20` | Auto-adjusts: 20% of monthly, or 10% per semi-monthly period |
| Transport Allowance | `base * 0.10` | Auto-adjusts: 10% of monthly, or 5% per semi-monthly period |
| Meal Allowance | `100000` | Fixed KHR 100,000 per period |
| Phone Allowance | `25000` | Fixed KHR 25,000 per period |

**Key Point**: Use `base` in formulas, and the system automatically applies:
- `base = monthly_base` for MONTHLY periods
- `base = monthly_base × 0.5` for SEMI_MONTHLY periods

#### Deductions Configuration:

Use standard NSSF/TAX components - they calculate based on period gross automatically:

| Component | Formula | Note |
|-----------|---------|------|
| NSSF Employee | `(calculated)` | 3.5% of gross, auto-adjusted |
| Tax | `(calculated)` | Progressive tax based on taxable income |

---

### Step 2: Create Two Periods Per Month

**Naming Convention**: `{Month} {Year} - Period {1|2} ({dates})`

```
January 2025 - Period 1 (1-15)
January 2025 - Period 2 (16-31)

February 2025 - Period 1 (1-15)
February 2025 - Period 2 (16-28)
```

**Important Fields**:
- Period Type: **SEMI_MONTHLY**
- Start/End dates: First or second half of month
- Payment Date: Typically 5 days after period end

---

### Step 3: Assign Salary Structure

Assign the standard structure to employees (works for ALL period types!):

```
Employee: John Doe
Salary Structure: Standard Employee Structure
Base Salary: 3,000,000 KHR (ALWAYS enter monthly base!)
From Date: 2025-01-01
Docstatus: 1 (Submitted)
```

**Critical**: Always enter the **monthly base salary** in the assignment:
- For monthly periods: Employee gets 3,000,000 KHR
- For semi-monthly periods: Employee gets 1,500,000 KHR (automatic split!)
- For weekly periods: Employee gets proportional amount (automatic!)

The system automatically adjusts based on the period type when generating payroll.

---

### Step 4: Generate Payroll for Each Period

**Period 1 Generation** (1-15):
1. Navigate to Period 1 detail page
2. Click "Generate Payroll"
3. System creates salary slips with 50% of monthly amounts
4. Review and approve

**Period 2 Generation** (16-31):
1. Navigate to Period 2 detail page
2. Click "Generate Payroll"
3. System creates salary slips with 50% of monthly amounts
4. Review and approve

**Important**: Generate and complete Period 1 before Period 2

---

## Complete Examples

### Example 1: Standard Employee (50/50 Method)

**Employee**: John Doe
**Monthly Base Salary**: 3,000,000 KHR
**Dependents**: 2 (wife + 1 child)

#### Period 1 (January 1-15, 2025):

**Earnings:**
```
Basic Salary:         1,500,000 KHR (base × 0.5)
Housing Allowance:      300,000 KHR (20% × 0.5)
Transport Allowance:    150,000 KHR (10% × 0.5)
Meal Allowance:         100,000 KHR (fixed)
Phone Allowance:         25,000 KHR (fixed)
─────────────────────────────────
Gross Pay:            2,075,000 KHR
```

**Deductions:**
```
NSSF Employee (3.5%):    72,625 KHR
Tax:                     45,000 KHR (calculated)
─────────────────────────────────
Total Deductions:       117,625 KHR
```

**Net Pay**: 1,957,375 KHR

#### Period 2 (January 16-31, 2025):

**Same calculation as Period 1**
- Gross Pay: 2,075,000 KHR
- Deductions: 117,625 KHR
- **Net Pay**: 1,957,375 KHR

#### Monthly Total:
- Gross: 4,150,000 KHR
- Deductions: 235,250 KHR
- Net: 3,914,750 KHR

---

### Example 2: Employee with Leave Without Pay

**Employee**: Jane Smith
**Monthly Base Salary**: 2,500,000 KHR
**Leave Without Pay**: 3 days in Period 2

#### Period 1 (January 1-15, 2025):

**Normal calculation** (no leave)
- Gross Pay: 1,729,167 KHR
- Net Pay: 1,627,542 KHR

#### Period 2 (January 16-31, 2025):

**Calculation with LWP:**
```
Working Days in Period: 11
Payment Days: 11 - 3 = 8 days

Basic Salary: 1,250,000 × (8/11) = 909,091 KHR
Housing:        250,000 × (8/11) = 181,818 KHR
Transport:      125,000 × (8/11) =  90,909 KHR
Meal:           100,000 (fixed, no proration)
Phone:           25,000 (fixed, no proration)
─────────────────────────────────
Gross Pay:                      1,306,818 KHR
```

**Deductions** (calculated on reduced gross):
```
NSSF:    45,739 KHR
Tax:     15,000 KHR
─────────────────
Total:   60,739 KHR
```

**Net Pay**: 1,246,079 KHR (reduced due to leave)

#### Monthly Total:
- Gross: 3,035,985 KHR (reduced from 3,458,334)
- Net: 2,873,621 KHR

---

### Example 3: New Employee Joining Mid-Month

**Employee**: Bob Johnson
**Monthly Base Salary**: 4,000,000 KHR
**Hire Date**: January 10, 2025

#### Period 1 (January 1-15, 2025):

**Prorated for 6 working days** (Jan 10-15)
```
Working Days in Period: 11 (total)
Employee Working Days: 6 (from Jan 10)

Basic Salary: 2,000,000 × (6/11) = 1,090,909 KHR
Housing:        400,000 × (6/11) =   218,182 KHR
Transport:      200,000 × (6/11) =   109,091 KHR
Meal:           100,000 (full)
Phone:           25,000 (full)
─────────────────────────────────
Gross Pay:                       1,543,182 KHR
```

**Deductions**:
```
NSSF:     54,011 KHR
Tax:      25,000 KHR
─────────
Total:    79,011 KHR
```

**Net Pay**: 1,464,171 KHR

#### Period 2 (January 16-31, 2025):

**Full period payment** (all 11 working days)
- Gross Pay: 2,725,000 KHR
- Net Pay: 2,531,375 KHR

#### First Month Total:
- Gross: 4,268,182 KHR
- Net: 3,995,546 KHR

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: Using Monthly Formulas

**Problem**: Using `base` instead of `base * 0.5` in semi-monthly structure
```
Formula: base * 0.20  (Wrong! Gives monthly allowance)
Result: Employee gets 20% twice = 40% total
```

**Solution**: Always multiply by 0.5
```
Formula: base * 0.20 * 0.5  (Correct!)
Result: Employee gets 10% + 10% = 20% total
```

---

### ❌ Pitfall 2: Incorrect Tax Calculation

**Problem**: Calculating tax on period gross instead of monthly gross
```
Period Gross: 2,075,000 KHR
Tax on 2,075,000: ~40,000 KHR per period
Monthly Tax: 80,000 KHR (incorrect - too low)
```

**Solution**: Calculate monthly gross, then split tax 50/50
```
Monthly Gross: 4,150,000 KHR
Monthly Tax: 150,000 KHR
Period Tax: 75,000 KHR (each period)
```

---

### ❌ Pitfall 3: Not Handling Month-End Dates

**Problem**: Setting Period 2 end date to 30th in months with 31 days
```
February Period 2: Feb 16-28 (missing Feb 29 in leap year)
January Period 2: Jan 16-30 (missing Jan 31)
```

**Solution**: Always use last day of month
```
January: Use end_date = 2025-01-31
February: Use end_date = 2025-02-28 (or 29 in leap year)
```

---

### ❌ Pitfall 4: Overlapping Periods

**Problem**: Periods overlap or have gaps
```
Period 1: Jan 1-15
Period 2: Jan 15-31  (Jan 15 counted twice!)
```

**Solution**: Use consecutive non-overlapping dates
```
Period 1: Jan 1-15
Period 2: Jan 16-31  (no overlap)
```

---

### ❌ Pitfall 5: Forgetting to Generate Both Periods

**Problem**: Generating only Period 1, forgetting Period 2

**Solution**: Create checklist for each month:
- [ ] Generate Period 1 (1-15)
- [ ] Review Period 1 slips
- [ ] Approve Period 1
- [ ] Pay Period 1
- [ ] Generate Period 2 (16-31)
- [ ] Review Period 2 slips
- [ ] Approve Period 2
- [ ] Pay Period 2

---

## Tax Considerations for Semi-Monthly

### Cambodia Tax Law

**Progressive Tax is calculated on MONTHLY taxable income**, not semi-monthly.

### Best Practice: Monthly Tax Calculation, Split Payment

**Method 1: Calculate Monthly, Split 50/50**

```python
# Pseudo-code
monthly_gross = period1_gross + period2_gross
monthly_nssf = monthly_gross × 3.5%
monthly_taxable = monthly_gross - monthly_nssf - dependent_deduction
monthly_tax = calculate_progressive_tax(monthly_taxable)

period1_tax = monthly_tax × 0.5
period2_tax = monthly_tax × 0.5
```

**Method 2: Estimate and Reconcile**

Calculate tax per period, but reconcile at year-end:
```python
period_taxable = period_gross - period_nssf - (dependent_deduction / 2)
period_tax = calculate_progressive_tax(period_taxable × 2) / 2
```

### Recommendation

For Cambodia compliance, use **Method 1**: Calculate based on monthly income, split payment.

This ensures:
- ✓ Correct progressive tax slab application
- ✓ Proper dependent deduction (KHR 150,000 × dependents per month)
- ✓ Compliance with tax law
- ✓ Consistent net pay for employees

---

## Implementation Checklist

### Initial Setup (One-Time)

- [ ] Create semi-monthly salary components (with `× 0.5` formulas)
- [ ] Create semi-monthly salary structure
- [ ] Assign structure to employees
- [ ] Test with one employee first
- [ ] Verify calculations are correct
- [ ] Document your semi-monthly policy

### Monthly Process

**For each month**:

1. **Create Periods** (1st of month)
   - [ ] Create Period 1 (1-15)
   - [ ] Create Period 2 (16-31)
   - [ ] Verify dates don't overlap
   - [ ] Set payment dates

2. **Period 1 Processing** (around 13th-15th)
   - [ ] Generate payroll for Period 1
   - [ ] Review all salary slips
   - [ ] Handle any special cases (new hires, leave)
   - [ ] Approve Period 1
   - [ ] Process payment
   - [ ] Update status to PAID

3. **Period 2 Processing** (around 28th-31st)
   - [ ] Generate payroll for Period 2
   - [ ] Review all salary slips
   - [ ] Handle any special cases
   - [ ] Approve Period 2
   - [ ] Process payment
   - [ ] Update status to PAID

4. **Month-End Reconciliation**
   - [ ] Verify total monthly amounts
   - [ ] Check NSSF totals
   - [ ] Verify tax calculations
   - [ ] Generate reports

---

## Recommended Salary Structure Template

### Structure Name: "Semi-Monthly Standard"

**Earnings:**

| Component | Formula | Description |
|-----------|---------|-------------|
| Basic Salary | `base * 0.5` | 50% of monthly base |
| Housing Allowance | `base * 0.20 * 0.5` | 10% per period (20% monthly) |
| Transport Allowance | `base * 0.10 * 0.5` | 5% per period (10% monthly) |
| Meal Allowance | `100000` | Fixed KHR 100,000 per period |
| Phone Allowance | `25000` | Fixed KHR 25,000 per period |
| Seniority Allowance | `base * 0.05 * 0.5` | 2.5% per period (5% monthly) |

**Deductions:**

| Component | Formula | Description |
|-----------|---------|-------------|
| NSSF Employee | `(gross * 0.035)` | 3.5% of period gross |
| Tax | `(calculated)` | Based on monthly taxable income ÷ 2 |

**Formula Context**:
- `base` = Employee's monthly base salary
- `gross` = Total earnings for the period
- All allowances are split 50/50 by using `× 0.5`

---

## Summary

### Key Takeaways

1. **✅ AUTOMATIC IMPLEMENTATION**
   - System now automatically detects SEMI_MONTHLY period type
   - Splits base salary 50/50 without manual formulas
   - Use standard formulas (`base * 0.20`) for all period types
   - One salary structure works for monthly AND semi-monthly!

2. **50/50 Split Method (Automatically Applied)**
   - Simple, predictable, easy to explain
   - System uses `base = monthly_base * 0.5` for semi-monthly
   - Consistent net pay each period
   - No manual `* 0.5` needed in formulas!

3. **Create Two Separate Periods Each Month**
   - Period 1: 1st to 15th (type = SEMI_MONTHLY)
   - Period 2: 16th to last day (type = SEMI_MONTHLY)
   - No overlaps or gaps
   - Working days auto-calculated

4. **Tax Calculation**
   - Calculate on period gross (automatically adjusted)
   - Progressive tax applied correctly
   - NSSF calculated on period amounts

5. **Handle Special Cases**
   - Leave without pay: Prorate using payment_days
   - New hires: Prorate for partial period
   - Terminations: Generate final slip for worked days
   - All handled automatically by the system!

6. **Monthly Process**
   - Generate Period 1 → Review → Approve → Pay
   - Generate Period 2 → Review → Approve → Pay
   - Reconcile monthly totals
   - System tracks totals automatically

### Decision Matrix

| Situation | Recommended Method |
|-----------|-------------------|
| Standard employees, stable workforce | 50/50 Split |
| Frequent mid-month hires/terminations | Proration by days |
| Hourly/daily workers | Proration by working days |
| Contract workers | Proration by actual days worked |
| Compliance-critical | 50/50 split with monthly tax calc |

---

*Last Updated: November 2025*
*Version: 1.0*
