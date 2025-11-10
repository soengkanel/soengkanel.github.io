# PayrollPeriod Flow Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Model Structure](#model-structure)
3. [Complete Integration Flow](#complete-integration-flow)
4. [Database Relationships](#database-relationships)
5. [Status Workflow](#status-workflow)
6. [Admin Interface Integration](#admin-interface-integration)
7. [API Integration](#api-integration)
8. [Key Benefits](#key-benefits)
9. [Example Complete Flow](#example-complete-flow)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        PAYROLL PERIOD                           │
│  (payroll/models.py:116-206)                                   │
│  - Defines time boundaries for payroll processing               │
│  - Tracks status: DRAFT → PROCESSING → APPROVED → PAID        │
│  - Caches summary metrics for performance                       │
└───────────┬─────────────────────────────────────────────────────┘
            │
            ├─── Foreign Key Relationships ───┐
            │                                  │
            ▼                                  ▼
    ┌───────────────┐              ┌──────────────────┐
    │  SalarySlip   │              │ EmployeeBenefit  │
    │  (1:N)        │              │     (1:N)        │
    └───────────────┘              └──────────────────┘
```

---

## Model Structure

### Core Fields (`payroll/models.py:116-206`)

```python
class PayrollPeriod:
    # Period Definition
    name = "January 2025"                    # Display name
    period_type = "MONTHLY"                  # MONTHLY, WEEKLY, BI_WEEKLY, SEMI_MONTHLY
    start_date = 2025-01-01                 # Period start
    end_date = 2025-01-31                   # Period end
    payment_date = 2025-02-05               # When employees get paid

    # Status Workflow
    status = "DRAFT"                         # DRAFT → PROCESSING → APPROVED → PAID → CANCELLED

    # Summary Metrics (Auto-calculated)
    total_employees = 50                     # Total salary slips
    processed_employees = 45                 # Completed salary slips
    total_gross_pay = 125000000.00          # Sum of all gross
    total_deductions = 15000000.00          # Sum of all deductions
    total_net_pay = 110000000.00            # Sum of all net pay

    # Audit Trail
    created_by = User                        # Who created
    approved_by = User                       # Who approved
    processed_by = User                      # Who processed
    processed_at = timestamp                 # When processed
    notes = TextField                        # Internal notes

    # Calculated Properties
    @property working_days → 22              # Auto-calculated (excludes weekends)
    @property is_current → True/False        # Is today within period?
```

### Constraints

- **Unique Together**: `['start_date', 'end_date']` - No overlapping periods allowed
- **Ordering**: `-start_date` - Most recent periods first
- **Cascade Delete**: Deleting a period deletes all related SalarySlips and EmployeeBenefits

---

## Complete Integration Flow

### 1. Period Creation

**Location**: `payroll/views.py:87-124`

```
User Action: Create New Period
         ↓
┌────────────────────────────┐
│ 1. Validate Dates          │ ← No overlapping periods allowed
│ 2. Set status = "DRAFT"    │
│ 3. Set created_by = user   │
│ 4. Save to database        │
└────────────────────────────┘
         ↓
     Period Ready
```

**Key Validation Code**:
```python
# payroll/views.py:99-102
overlapping = PayrollPeriod.objects.filter(
    Q(start_date__lte=end_date, end_date__gte=start_date)
).exists()

if overlapping:
    messages.error(request, 'Period dates overlap with an existing period.')
    return redirect('payroll:periods')
```

**URL**: `/payroll/periods/create/`

---

### 2. Payroll Generation

**Location**: `payroll/api_views.py:45-95`

This is where PayrollPeriod **actively drives** the payroll calculation:

```
User: Click "Generate Payroll" for Period
         ↓
┌─────────────────────────────────────────────┐
│ FOR EACH Active Employee:                   │
│                                             │
│ 1. Get period.working_days (22 days) ────┐ │
│    → Auto-calculated excluding weekends   │ │
│                                           │ │
│ 2. Create SalarySlip:                    │ │
│    - payroll_period = THIS PERIOD        │ │
│    - start_date = period.start_date   ◄──┘ │
│    - end_date = period.end_date             │
│    - total_working_days = working_days      │
│                                             │
│ 3. Calculate salary using period dates:     │
│    a) Get Tax/NSSF configs valid on        │
│       period.end_date ─────────────────┐   │
│    b) Filter AdditionalSalary in        │   │
│       [start_date, end_date] range      │   │
│    c) Calculate all components          │   │
│                                         │   │
│ 4. Save salary slip                     │   │
└─────────────────────────────────────────┼───┘
         ↓                                │
┌────────────────────────────────────────┼───┐
│ Update Period:                         │   │
│ - status = "PROCESSING"                │   │
│ - processed_by = current_user          │   │
│ - processed_at = now()                 │   │
│                                        │   │
│ Call period.update_summary():          │   │
│ - Count all salary_slips            ◄──┘   │
│ - Sum gross_pay, deductions, net_pay       │
│ - Update total_employees, etc.             │
└────────────────────────────────────────────┘
         ↓
  Period.status = "PROCESSING"
  Period has summary metrics
```

#### Critical Integration Points

##### A. Working Days Calculation
**Location**: `payroll/models.py:178-186`

```python
@property
def working_days(self):
    """Auto-calculate excluding weekends"""
    current_date = self.start_date
    working_days = 0
    while current_date <= self.end_date:
        if current_date.weekday() < 5:  # Mon-Fri only
            working_days += 1
        current_date += timedelta(days=1)
    return working_days
```

**Purpose**:
- Used for prorated salary calculations
- Automatically excludes weekends
- No manual entry required

##### B. Tax Configuration Lookup
**Location**: `payroll/models.py:656-659`

```python
# Uses period.end_date to find applicable tax rules
tax_slabs = TaxSlab.objects.filter(
    is_active=True,
    effective_from__lte=self.end_date  # ← Period integration
).order_by('min_amount')
```

**Purpose**:
- Ensures historical accuracy
- Old periods use old tax rates
- New periods use current tax rates

##### C. NSSF Configuration Lookup
**Location**: `payroll/models.py:679-682`

```python
# Uses period.end_date to find applicable NSSF rates
nssf_configs = NSSFConfiguration.objects.filter(
    is_active=True,
    effective_from__lte=self.end_date  # ← Period integration
)
```

**Purpose**:
- Social security rates change over time
- Period date determines which rate applies

##### D. Additional Salary Filtering
**Location**: `payroll/models.py:906-909`

```python
# Bonuses, deductions within period date range
additional_salaries = AdditionalSalary.objects.filter(
    employee=self.employee,
    payroll_date__range=[self.start_date, self.end_date],  # ← Period integration
    status='ACTIVE'
)
```

**Purpose**:
- Include bonuses paid during the period
- Include one-time deductions during the period
- Exclude items outside the period

**URL**: `POST /api/payroll-periods/{id}/generate/`

---

### 3. Summary Metrics Update

**Location**: `payroll/models.py:188-206`

```python
def update_summary(self):
    """Aggregate all salary slips for this period"""
    from django.db.models import Sum, Count

    # Query all related salary slips
    summary = self.salary_slips.aggregate(
        total=Count('id'),
        processed=Count('id', filter=models.Q(status__in=['SUBMITTED', 'PAID'])),
        gross=Sum('gross_pay'),
        deductions=Sum('total_deduction'),
        net=Sum('net_pay')
    )

    # Update period's cached totals
    self.total_employees = summary['total'] or 0
    self.processed_employees = summary['processed'] or 0
    self.total_gross_pay = summary['gross'] or Decimal('0.00')
    self.total_deductions = summary['deductions'] or Decimal('0.00')
    self.total_net_pay = summary['net'] or Decimal('0.00')

    self.save(update_fields=['total_employees', 'processed_employees',
                            'total_gross_pay', 'total_deductions',
                            'total_net_pay', 'updated_at'])
```

**Triggers**:
1. After payroll generation: `payroll/api_views.py:87`
2. When viewing period detail with `?refresh=1`: `payroll/views.py:176`
3. Admin bulk action "Update summary metrics": `payroll/admin.py:145-152`

**Purpose**:
- Cache expensive aggregate queries
- Improve performance of period listing/detail views
- Provide quick overview without scanning all salary slips

---

### 4. Period Detail View

**Location**: `payroll/views.py:170-195`

```
User: View Period Details
         ↓
┌────────────────────────────────────┐
│ 1. Load PayrollPeriod             │
│ 2. Check if summary needs refresh │
│    - If total_employees == 0      │
│    - If ?refresh=1 in URL         │
│      → Call period.update_summary()│
│                                    │
│ 3. Display:                        │
│    - Period info (dates, status)  │
│    - Working days (calculated)    │
│    - Summary metrics (cached)     │
│    - List of salary slips         │
└────────────────────────────────────┘
```

**Statistics Displayed**:
```python
stats = {
    'total_employees': period.total_employees,        # From cached field
    'processed_employees': period.processed_employees,
    'total_gross': period.total_gross_pay,           # No query needed!
    'total_deductions': period.total_deductions,
    'total_net': period.total_net_pay,
    'working_days': period.working_days,             # Calculated property
    'is_current': period.is_current,                 # Is today in period?
}
```

**URL**: `/payroll/periods/{period_id}/`

---

## Database Relationships

### 1. SalarySlip (Many-to-One)

**Location**: `payroll/models.py:554`

```python
class SalarySlip:
    payroll_period = ForeignKey(PayrollPeriod,
                                on_delete=CASCADE,
                                related_name='salary_slips')
    employee = ForeignKey(Employee)

    class Meta:
        unique_together = ['payroll_period', 'employee']  # One slip per employee per period
```

**Purpose**:
- Links each salary calculation to a specific period
- Enforces one salary slip per employee per period
- Cascade delete: Deleting period removes all salary slips

**Query Examples**:
```python
# Get all slips for a period
slips = period.salary_slips.all()

# Count employees in period
count = period.salary_slips.count()

# Sum totals
totals = period.salary_slips.aggregate(
    gross=Sum('gross_pay'),
    net=Sum('net_pay')
)

# Filter by status
paid_slips = period.salary_slips.filter(status='PAID')
```

---

### 2. EmployeeBenefit (Many-to-One)

**Location**: `payroll/models.py:421`

```python
class EmployeeBenefit:
    payroll_period = ForeignKey(PayrollPeriod, on_delete=CASCADE)
    employee = ForeignKey(Employee)
    earning_component = ForeignKey(SalaryComponent)

    max_benefit_amount = DecimalField()
    claimed_amount = DecimalField()
    remaining_benefit = DecimalField()

    class Meta:
        unique_together = ['employee', 'earning_component', 'payroll_period']
```

**Purpose**:
- Track employee benefit claims per period
- Examples: health insurance, meal vouchers, transport reimbursements
- One claim per employee per component per period

**Use Cases**:
- Flexible benefits with caps (e.g., max $500/month for meals)
- Period-specific benefit tracking
- Remaining benefit calculation

---

## Status Workflow

```
┌────────┐
│ DRAFT  │ ← Period created, can be edited
└───┬────┘
    │ Action: Generate Payroll
    ▼
┌────────────┐
│ PROCESSING │ ← Salary slips being generated/calculated
└─────┬──────┘
      │ Action: Review & Approve
      ▼
┌──────────┐
│ APPROVED │ ← Calculations finalized, ready for payment
└────┬─────┘
     │ Action: Execute Payment
     ▼
┌──────┐
│ PAID │ ← Employees paid, period locked
└──────┘

   (Can also be CANCELLED at any stage)
```

### Status Meanings

| Status | Description | Actions Allowed | Protection |
|--------|-------------|-----------------|------------|
| **DRAFT** | Newly created, not processed | Edit, Delete, Generate | None |
| **PROCESSING** | Payroll being generated/calculated | View, Edit slips | Can delete |
| **APPROVED** | Ready for payment | View only | **Cannot delete** |
| **PAID** | Payment completed | View only | **Cannot delete** |
| **CANCELLED** | Period cancelled | View only | Can delete |

### Protection Rules

**Location**: `payroll/views.py:197-199`

```python
# Prevent deletion of APPROVED or PAID periods for safety
if period.status in ['APPROVED', 'PAID']:
    messages.error(request, f'Cannot delete {period.name}. '
                           f'{period.get_status_display()} periods cannot be deleted.')
    return redirect('payroll:periods')
```

---

## Admin Interface Integration

**Location**: `payroll/admin.py:87-152`

### List View

Displays all periods with key metrics:

| Name | Type | Start Date | End Date | Payment Date | Status | Employees | Total Net Pay | Created By |
|------|------|------------|----------|--------------|--------|-----------|---------------|------------|
| January 2025 | Monthly | 2025-01-01 | 2025-01-31 | 2025-02-05 | PROCESSING | 50 | KHR 110,000,000 | john.doe |
| December 2024 | Monthly | 2024-12-01 | 2024-12-31 | 2025-01-05 | PAID | 48 | KHR 105,500,000 | jane.smith |

### Filters
- Period Type (Monthly, Weekly, Bi-Weekly, Semi-Monthly)
- Status (Draft, Processing, Approved, Paid, Cancelled)
- Start Date (date hierarchy)

### Detail View Sections

#### 1. Basic Information
- Name, period type
- Start date, end date, payment date
- Status

#### 2. Period Metrics (Collapsible)
- Working days (calculated)
- Is current period indicator

#### 3. Summary Totals
- Total employees
- Processed employees
- Total gross pay
- Total deductions
- Total net pay
- **Note**: Auto-calculated from salary slips (read-only)

#### 4. Tracking (Collapsible)
- Created by
- Approved by
- Processed by
- Processed at

#### 5. Additional Information (Collapsible)
- Notes

#### 6. System Information (Collapsible)
- Created at
- Updated at

### Bulk Actions

**"Update summary metrics from salary slips"**

```python
def update_period_summaries(self, request, queryset):
    """Bulk action to update summary metrics for selected periods"""
    updated = 0
    for period in queryset:
        period.update_summary()
        updated += 1
    self.message_user(request, f'Successfully updated summaries for {updated} period(s).')
```

**Use Case**: Refresh cached totals after manual salary slip edits

---

## API Integration

**Location**: `payroll/api_views.py:22-95`

### Endpoints

```
GET    /api/payroll-periods/                  List all periods
POST   /api/payroll-periods/                  Create new period
GET    /api/payroll-periods/{id}/             Get period details
PUT    /api/payroll-periods/{id}/             Update period
DELETE /api/payroll-periods/{id}/             Delete period
POST   /api/payroll-periods/{id}/generate/    Generate payroll for period
```

### Generate Payroll Response

**Endpoint**: `POST /api/payroll-periods/{id}/generate/`

```json
{
  "message": "Generated payroll for 50 employees",
  "payroll_ids": [123, 124, 125, 126, ...],
  "working_days": 22,
  "total_gross_pay": 125000000.00,
  "total_net_pay": 110000000.00
}
```

### Serializer

**Location**: `payroll/serializers.py:9-17`

```python
class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'
        read_only_fields = ('created_by', 'approved_by', 'processed_by',
                           'total_employees', 'processed_employees',
                           'total_gross_pay', 'total_deductions', 'total_net_pay')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
```

---

## Key Benefits

### 1. Date-Based Configuration Lookup ✅

**Benefit**: Historical accuracy for recalculations

```python
# Tax rates effective on period.end_date
tax_slabs = TaxSlab.objects.filter(
    is_active=True,
    effective_from__lte=self.end_date
)
```

**Example**:
- Recalculating January 2024 payroll uses 2024 tax rates
- Running payroll for January 2025 uses 2025 tax rates (if changed)

---

### 2. Automatic Working Days ✅

**Benefit**: Consistent, error-free calculations

```python
# Auto-calculated, excludes weekends
working_days = period.working_days  # → 22
```

**Example**:
- January 2025: 31 days → 22 working days (auto-calculated)
- Used for prorated salaries when employees join mid-month

---

### 3. Performance Optimization ✅

**Benefit**: Fast page loads, cached totals

```python
# No expensive aggregation needed on every page load
total_net = period.total_net_pay  # Cached field
```

**Performance Comparison**:
- **Without cache**: Query 50 salary slips, aggregate → ~200ms
- **With cache**: Read single field → ~5ms

---

### 4. Data Integrity ✅

**Benefit**: Prevents errors and data corruption

**Enforcements**:
- Unique constraint on `[start_date, end_date]` → No overlapping periods
- Foreign key cascade → Deleting period cleans up related data
- Status workflow → Cannot delete APPROVED/PAID periods
- Unique constraint on `[employee, payroll_period]` in SalarySlip → One slip per employee

---

### 5. Audit Trail ✅

**Benefit**: Full accountability and tracking

```python
period.created_by      # Who created
period.approved_by     # Who approved
period.processed_by    # Who generated payroll
period.processed_at    # When it was done
period.notes           # Why/additional context
```

**Use Cases**:
- Compliance audits
- Troubleshooting issues
- Management oversight

---

## Example Complete Flow

### Scenario: January 2025 Payroll

#### Step 1: Period Creation
```
Date: 2025-01-25
User: HR Manager (Sarah)

Action: Create period via web interface
- Name: "January 2025 - Monthly Payroll"
- Period Type: MONTHLY
- Start Date: 2025-01-01
- End Date: 2025-01-31
- Payment Date: 2025-02-05

Result:
✓ Period created with status = DRAFT
✓ created_by = Sarah
✓ working_days = 22 (auto-calculated)
```

---

#### Step 2: Payroll Generation
```
Date: 2025-01-26
User: HR Manager (Sarah)

Action: Click "Generate Payroll" button

Process:
1. System queries: 50 active employees found
2. For each employee:
   - Create SalarySlip linked to period
   - Set total_working_days = 22 (from period.working_days)
   - Look up TaxSlab effective on 2025-01-31
   - Look up NSSFConfiguration effective on 2025-01-31
   - Filter AdditionalSalary where payroll_date in [2025-01-01, 2025-01-31]
   - Calculate: Earnings, NSSF, Tax, Deductions
   - Save salary slip

3. Update Period:
   - status = PROCESSING
   - processed_by = Sarah
   - processed_at = 2025-01-26 10:30:00

4. Call period.update_summary():
   - total_employees = 50
   - processed_employees = 0 (none submitted yet)
   - total_gross_pay = KHR 125,000,000
   - total_deductions = KHR 15,000,000
   - total_net_pay = KHR 110,000,000

Result:
✓ 50 salary slips created
✓ Period status = PROCESSING
✓ Summary metrics cached
```

---

#### Step 3: Review
```
Date: 2025-01-27
User: HR Manager (Sarah)

Action: View period detail page

Display:
- Period: January 2025
- Status: PROCESSING
- Working Days: 22
- Total Employees: 50
- Total Gross Pay: KHR 125,000,000
- Total Net Pay: KHR 110,000,000

Action: Review individual salary slips
- Check calculations for accuracy
- Verify deductions
- Confirm bonuses included

Action: Make corrections if needed
- Edit individual salary slips
- Recalculate specific slips

Action: Click "Refresh Summary" (or visit with ?refresh=1)
- period.update_summary() recalculates totals
```

---

#### Step 4: Approval
```
Date: 2025-01-28
User: Finance Manager (John)

Action: Review and approve period

Process:
1. Verify all 50 salary slips are correct
2. Confirm budget allocation
3. Update period:
   - status = APPROVED
   - approved_by = John

Result:
✓ Period status = APPROVED
✓ Period is now locked (cannot delete)
✓ Ready for payment processing
```

---

#### Step 5: Payment
```
Date: 2025-02-05 (Payment Date)
User: Finance Team

Action: Execute bank transfers

Process:
1. Export salary slip data
2. Generate bank transfer file
3. Submit to bank
4. Receive confirmation
5. Update period:
   - status = PAID

Result:
✓ All employees paid
✓ Period status = PAID
✓ Period fully locked
✓ Historical record preserved
```

---

#### Step 6: Historical Reporting
```
Date: 2025-06-15 (6 months later)
User: Accountant

Action: View January 2025 payroll report

Process:
1. Query: PayrollPeriod.objects.get(name__contains='January 2025')
2. Display cached summary:
   - Total Net Pay: KHR 110,000,000 ← Fast! No aggregation
   - Total Employees: 50
   - Working Days: 22
3. Export detailed report if needed

Result:
✓ Fast access to historical data
✓ No performance impact
✓ Accurate historical record
```

---

## URL Routes Reference

**Location**: `payroll/urls.py:10-16`

```python
# Period Management
path('periods/', views.payroll_periods, name='periods')
path('periods/create/', views.create_payroll_period, name='create_period')
path('periods/<int:period_id>/', views.payroll_period_detail, name='period_detail')
path('periods/<int:period_id>/edit/', views.edit_payroll_period, name='edit_period')
path('periods/<int:period_id>/generate/', views.generate_payroll, name='generate_payroll')
path('periods/<int:period_id>/delete/', views.payroll_period_delete, name='period_delete')
```

---

## File Reference

### Models
- **PayrollPeriod**: `payroll/models.py:116-206`
- **SalarySlip**: `payroll/models.py:550-1000+`
- **EmployeeBenefit**: `payroll/models.py:412-431`
- **TaxSlab**: `payroll/models.py:509-526`
- **NSSFConfiguration**: `payroll/models.py:528-547`

### Views
- **Period List**: `payroll/views.py:46-84`
- **Period Create**: `payroll/views.py:87-124`
- **Period Detail**: `payroll/views.py:170-195`
- **Period Delete**: `payroll/views.py:192-230`
- **Generate Payroll**: `payroll/views.py:234-282`

### API
- **PayrollPeriodViewSet**: `payroll/api_views.py:22-95`
- **Generate Action**: `payroll/api_views.py:45-95`

### Admin
- **PayrollPeriodAdmin**: `payroll/admin.py:87-152`

### Serializers
- **PayrollPeriodSerializer**: `payroll/serializers.py:9-17`

### Templates
- **Period List**: `templates/payroll/periods/list.html`
- **Period Create**: `templates/payroll/periods/create.html`
- **Period Detail**: `templates/payroll/periods/detail.html`
- **Period Edit**: `templates/payroll/periods/edit.html`

---

## Summary

**PayrollPeriod is the backbone of the payroll system:**

1. ✅ **Defines temporal boundaries** for payroll processing
2. ✅ **Drives salary calculations** through date-based config lookups
3. ✅ **Provides working days** for prorated calculations
4. ✅ **Caches summary metrics** for performance
5. ✅ **Enforces data integrity** through constraints and status workflow
6. ✅ **Maintains audit trail** of who did what and when

It's not just a time period—it's an **active coordinator** that orchestrates the entire payroll calculation process!

---

## Migration History

### Enhancement: 0007_enhance_payroll_period

**Date**: 2025-11-01

**Changes**:
- Added `notes` field for internal documentation
- Added `processed_at` timestamp field
- Added `processed_by` foreign key to User
- Added `processed_employees` count field
- Added `total_deductions` summary field
- Added `total_employees` summary field
- Added `total_gross_pay` summary field
- Added `total_net_pay` summary field
- Added `working_days` calculated property
- Added `is_current` calculated property
- Added `update_summary()` method for metrics refresh

**Benefits**:
- Better tracking and audit trail
- Performance optimization through cached summaries
- Automatic working days calculation
- Enhanced reporting capabilities

---

*Last Updated: November 2025*
*Version: 1.0*
