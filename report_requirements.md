# NextHR System - Report Requirements Document

## Current Reports Inventory

### **Attendance Module**
1. **Attendance Reports** (`templates/attendance/reports.html`)
   - Daily attendance records with clock in/out times
   - Filters: Date range, employee, department, project
   - Export: CSV, Excel, PDF
   - Metrics: Total records, present, late, absent

2. **Overtime Reports** (`templates/attendance/overtime_report.html`)
   - Overtime requests with hours, rates, and amounts
   - Filters: Date range, employee, status, project
   - Export: CSV, Excel, PDF
   - Metrics: Total requests, pending, approved, total hours, total amount

### **Payroll Module**
3. **Payroll Reports** (`templates/payroll/reports/index.html`)
   - Monthly payroll records
   - Shows: Base salary, allowances, gross pay, deductions, net pay
   - Filters: Period (month/year), employee search, status
   - Export: Excel, PDF
   - Includes payslip generation

### **HR Module**
4. **Foreign/Khmer Report** (`hr/templates/hr/foreign_khmer_report.html`)
   - Monthly worker distribution by nationality
   - Breakdown by building
   - Filters: Year, month, zone, building, floor
   - Shows: Foreign vs Khmer worker counts per building

5. **Staff Report** (`hr/templates/hr/staff_report.html`)
   - Staff categorization with gender breakdown
   - By position and building
   - Filters: Year, month, zone, building, floor
   - Shows: Male/female/total counts by category

6. **Worker Reports Dashboard** (`hr/templates/hr/worker_reports_dashboard.html`)
   - Central hub for accessing worker reports
   - Links to Foreign/Khmer and Staff reports

### **Payments Module**
7. **Payment Reports Dashboard** (`templates/payments/reports.html`)
   - Monthly payment trends (chart visualization)
   - Payment method breakdown
   - Metrics: Current month total, payment methods count, total transactions
   - Links to detailed reports

8. **Daily Collection Report** (View: `payments/views.py:345`)
   - Daily payment collection tracking

9. **Monthly Payment Report** (View: `payments/views.py:368`)
   - Monthly payment summaries

### **Billing Module**
10. **Revenue Report** (View: `billing/views.py:823`)
    - Revenue tracking

11. **Overdue Report** (`templates/billing/overdue_report.html`)
    - Overdue payments/invoices tracking

12. **Receipt Summary Report** (View: `billing/views.py:1855`)
    - Receipt summaries

13. **Visa Services Report** (View: `billing/views.py:2070`)
    - Visa service tracking

### **E-Form Module**
14. **Worker Reports** (`eform/templates/eform/worker_reports.html`)
    - Custom worker data collection reports
    - Worker report results and printing capabilities

### **Training Module**
15. **Reports Overview** (View: `training/views.py:640`)
    - Training program reports

---

## Recommended Additional Reports

### **Category 1: Employee Analytics & KPIs**

#### **1.1 Employee Turnover Report**
**Purpose:** Track and analyze employee retention and turnover patterns

**Key Metrics:**
- Monthly/quarterly/annual turnover rates
- Voluntary vs involuntary turnover
- Turnover by department, position, nationality, building, zone
- Average tenure by department/position
- Retention rate trends
- Cost of turnover estimation

**Filters:**
- Date range (month/quarter/year)
- Department
- Building/Zone/Floor
- Position/Job title
- Employment type
- Reason for leaving

**Visualizations:**
- Turnover trend line chart
- Turnover by department (bar chart)
- Reasons for leaving (pie chart)
- Average tenure by department (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Critical for retention strategies

---

#### **1.2 Headcount Report**
**Purpose:** Track current workforce composition and trends

**Key Metrics:**
- Current headcount by department, building, zone, floor
- Active vs inactive employees
- Contract type distribution (permanent, temporary, contract)
- Full-time vs part-time breakdown
- Headcount changes over time (hires - separations)
- Contractor vs employee ratio
- Headcount by nationality

**Filters:**
- As of date
- Department
- Building/Zone/Floor
- Employment status
- Contract type
- Nationality

**Visualizations:**
- Headcount trend over time (line chart)
- Headcount by department (bar chart)
- Contract type distribution (pie chart)
- Building occupancy (stacked bar chart)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Essential for workforce planning

---

#### **1.3 New Hires Report**
**Purpose:** Track recruitment effectiveness and onboarding

**Key Metrics:**
- New employees by period
- Time-to-fill by position
- Source of hire analysis
- New hire retention rate (30/60/90 days)
- Onboarding completion status
- New hires by department/building
- Cost per hire

**Filters:**
- Hire date range
- Department
- Building/Zone
- Position
- Hire source
- Onboarding status

**Visualizations:**
- New hires trend (line chart)
- Hires by department (bar chart)
- Source of hire (pie chart)
- Time-to-fill analysis (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

### **Category 2: Attendance & Time Management**

#### **2.1 Absenteeism Report**
**Purpose:** Monitor and analyze employee absence patterns

**Key Metrics:**
- Absence rate by employee/department/building
- Total absence days/hours
- Unplanned vs planned absences
- Absence frequency and duration
- Bradford Factor scores (for chronic absenteeism)
- Most common absence days (Monday, Friday patterns)
- Cost of absenteeism

**Filters:**
- Date range
- Department
- Building/Zone/Floor
- Employee
- Absence type
- Planned vs unplanned

**Visualizations:**
- Absence rate trend (line chart)
- Absence by department (bar chart)
- Absence by day of week (bar chart)
- Top absentees (table with Bradford Factor)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Critical for productivity management

---

#### **2.2 Late Coming Analysis**
**Purpose:** Identify and analyze tardiness patterns

**Key Metrics:**
- Late arrival frequency by employee
- Total late minutes by employee/department
- Average lateness per incident
- Lateness patterns (time of day, day of week)
- Chronic lateness identification (threshold-based)
- Impact on productivity hours
- Late arrivals by building/zone

**Filters:**
- Date range
- Department
- Building/Zone/Floor
- Employee
- Lateness threshold (e.g., >15 minutes)

**Visualizations:**
- Lateness trend (line chart)
- Top late employees (bar chart)
- Lateness by day of week (bar chart)
- Lateness by time slot (heatmap)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **2.3 Leave Balance Report**
**Purpose:** Track employee leave entitlements and usage

**Key Metrics:**
- Current leave balance by employee
- Leave accrued vs used
- Leave taken by type (annual, sick, unpaid, etc.)
- Upcoming scheduled leave
- Leave liability value
- Employees with low/high balances
- Expiring leave alerts

**Filters:**
- Department
- Building/Zone
- Employee
- Leave type
- Balance threshold
- Expiry date

**Visualizations:**
- Leave usage trend (line chart)
- Leave balance distribution (histogram)
- Leave by type (pie chart)
- Upcoming leave calendar (Gantt chart)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Needed for operational planning

---

#### **2.4 Time & Attendance Summary**
**Purpose:** Comprehensive overview of time and attendance

**Key Metrics:**
- Total work hours by employee/department
- Overtime vs regular hours ratio
- Attendance percentage by building/zone
- Average daily attendance
- Shift compliance rate
- Clock in/out accuracy
- Time fraud incidents

**Filters:**
- Date range
- Department
- Building/Zone/Floor
- Shift
- Employee

**Visualizations:**
- Attendance rate trend (line chart)
- Hours breakdown (stacked bar chart)
- Attendance heatmap (by day/week)
- Department comparison (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

### **Category 3: Payroll & Compensation**

#### **3.1 Payroll Cost Analysis**
**Purpose:** Analyze and control payroll expenses

**Key Metrics:**
- Total payroll cost by period
- Payroll cost by department/building/zone
- Cost per employee (average)
- Payroll cost trends over time
- Budget vs actual payroll spending
- Cost breakdown: base salary, allowances, overtime, bonuses, deductions
- Payroll cost as % of revenue (if available)

**Filters:**
- Period (month/quarter/year)
- Department
- Building/Zone
- Cost category
- Budget comparison toggle

**Visualizations:**
- Payroll cost trend (line chart)
- Cost by department (bar chart)
- Cost breakdown (pie chart)
- Budget vs actual (comparison chart)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Financial management essential

---

#### **3.2 Salary Distribution Report**
**Purpose:** Analyze compensation structure and equity

**Key Metrics:**
- Salary ranges by position/department
- Salary quartiles (25th, 50th, 75th percentiles)
- Salary distribution histogram
- Gender pay gap analysis
- Compensation competitiveness (vs market if data available)
- Pay equity ratios
- Highest/lowest paid positions

**Filters:**
- Department
- Position/Job level
- Gender
- Employment type
- Building/Zone

**Visualizations:**
- Salary distribution (histogram)
- Salary by position (box plot)
- Gender pay comparison (bar chart)
- Salary range by department (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **3.3 Deductions Report**
**Purpose:** Track and analyze payroll deductions

**Key Metrics:**
- Total deductions by category
- Tax deductions summary
- Insurance/benefits deductions
- Loan repayments tracking
- Deductions by employee/department
- Average deduction per employee
- Deduction trends over time

**Filters:**
- Period
- Deduction type
- Department
- Employee
- Building/Zone

**Visualizations:**
- Deductions trend (line chart)
- Deductions by type (pie chart)
- Deductions by department (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **3.4 Bonus & Incentive Report**
**Purpose:** Track performance-based compensation

**Key Metrics:**
- Total bonuses paid by period
- Bonus distribution by department/position
- Average bonus per employee
- Bonus types (performance, project, retention, etc.)
- Incentive program participation
- Bonus as % of base salary
- Top bonus earners

**Filters:**
- Period
- Bonus type
- Department
- Building/Zone
- Position

**Visualizations:**
- Bonus trend (line chart)
- Bonus by department (bar chart)
- Bonus distribution (histogram)

**Export:** Excel, PDF, CSV

**Priority:** LOW

---

### **Category 4: Compliance & Regulatory**

#### **4.1 Work Permit & Visa Expiry Report**
**Purpose:** Ensure compliance for foreign workers

**Key Metrics:**
- Permits/visas expiring in 30/60/90 days
- Expired permits/visas
- Renewal status tracking
- Compliance status by worker
- Foreign workers by permit type
- Processing time tracking
- Cost of permits/visas

**Filters:**
- Expiry date range
- Document type
- Nationality
- Department
- Building/Zone
- Status (valid, expiring, expired)

**Alerts:**
- Email alerts for upcoming expirations
- Dashboard alerts for expired documents

**Visualizations:**
- Expiration timeline (Gantt chart)
- Status distribution (pie chart)
- Permits by nationality (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Compliance critical

---

#### **4.2 Contract Expiry Report**
**Purpose:** Track employment contract renewals

**Key Metrics:**
- Contracts expiring in 30/60/90 days
- Expired contracts
- Contract type distribution
- Renewal decisions (renew/terminate/pending)
- Probation period completion
- Average contract duration
- Contract renewal rate

**Filters:**
- Expiry date range
- Contract type
- Department
- Building/Zone
- Status

**Alerts:**
- Email alerts for upcoming expirations
- Manager notifications

**Visualizations:**
- Expiration timeline (Gantt chart)
- Contract type distribution (pie chart)
- Renewal decisions (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Planning and compliance

---

#### **4.3 Labor Law Compliance Report**
**Purpose:** Monitor compliance with labor regulations

**Key Metrics:**
- Working hours compliance (max hours/week)
- Overtime limits monitoring
- Minimum wage compliance
- Rest day compliance (weekly/monthly)
- Break time compliance
- Violations count and severity
- Non-compliant employees/departments

**Filters:**
- Period
- Compliance category
- Department
- Building/Zone
- Violation severity

**Alerts:**
- Real-time alerts for violations
- Weekly compliance summary

**Visualizations:**
- Compliance score trend (line chart)
- Violations by type (bar chart)
- Compliance by department (scorecard)

**Export:** Excel, PDF, CSV

**Priority:** HIGH - Legal compliance

---

#### **4.4 Audit Trail Report**
**Purpose:** Track system access and data changes

**Key Metrics:**
- User login activity
- Data modification logs
- Record creation/deletion
- Failed login attempts
- User activity by module
- Changes by user
- Security incidents

**Filters:**
- Date range
- User
- Module/Section
- Action type
- Record type

**Visualizations:**
- Activity trend (line chart)
- Activity by user (bar chart)
- Activity by module (pie chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM - Security and compliance

---

### **Category 5: Performance & Productivity**

#### **5.1 Department Performance Dashboard**
**Purpose:** Track departmental KPIs and performance

**Key Metrics:**
- Department-specific KPIs
- Productivity metrics
- Goal achievement rates
- Team efficiency scores
- Project completion rates
- Quality metrics
- Department comparisons

**Filters:**
- Period
- Department
- Metric type
- Building/Zone

**Visualizations:**
- KPI scorecard
- Performance trend (line chart)
- Department comparison (radar chart)
- Goal achievement (progress bars)

**Export:** Excel, PDF

**Priority:** MEDIUM

---

#### **5.2 Project Staffing Report**
**Purpose:** Track resource allocation to projects

**Key Metrics:**
- Employees assigned to projects
- Project hours by employee
- Project cost allocation
- Resource utilization rates
- Project vs non-project time
- Over/under-allocated resources
- Project team composition

**Filters:**
- Project
- Date range
- Department
- Employee
- Utilization threshold

**Visualizations:**
- Utilization rate (gauge chart)
- Project hours breakdown (stacked bar)
- Resource allocation (heatmap)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **5.3 Training Effectiveness Report**
**Purpose:** Measure training program ROI and impact

**Key Metrics:**
- Training completion rates
- Training hours by employee/department
- Skills gap analysis
- Training cost per employee
- Post-training performance improvement
- Certification tracking
- Training satisfaction scores

**Filters:**
- Period
- Training type
- Department
- Employee
- Certification status

**Visualizations:**
- Completion rate trend (line chart)
- Training by department (bar chart)
- Skills gap matrix (heatmap)
- ROI analysis (comparison chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

### **Category 6: Operational Reports**

#### **6.1 Building/Zone Occupancy Report**
**Purpose:** Track space utilization and planning

**Key Metrics:**
- Employee distribution by building/zone/floor
- Capacity vs actual occupancy
- Occupancy rate by location
- Space per employee
- Occupancy trends over time
- Vacant/over-utilized spaces

**Filters:**
- Building
- Zone
- Floor
- Date

**Visualizations:**
- Occupancy map (floor plan visualization)
- Occupancy rate (bar chart)
- Trend over time (line chart)

**Export:** Excel, PDF

**Priority:** LOW

---

#### **6.2 Shift Coverage Report**
**Purpose:** Ensure adequate shift staffing

**Key Metrics:**
- Shift assignments by employee
- Coverage gaps (understaffed shifts)
- Shift preference compliance
- Rotation effectiveness
- Overtime due to coverage gaps
- Shift swap tracking

**Filters:**
- Date range
- Shift
- Department
- Building/Zone

**Visualizations:**
- Shift coverage calendar (heatmap)
- Coverage gaps (table)
- Shift distribution (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **6.3 Employee Document Status**
**Purpose:** Track document collection and compliance

**Key Metrics:**
- Missing documents by employee
- Document compliance percentage
- Documents pending verification
- Expiring documents (ID, certificates, etc.)
- Document types collected
- Compliance by department

**Filters:**
- Document type
- Status (complete, missing, pending)
- Department
- Employee
- Expiry date

**Alerts:**
- Alerts for missing critical documents
- Expiry notifications

**Visualizations:**
- Compliance rate (progress bar)
- Document status (pie chart)
- Compliance by department (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

### **Category 7: Financial Reports**

#### **7.1 Cost-per-Hire Report**
**Purpose:** Analyze recruitment efficiency and costs

**Key Metrics:**
- Total recruitment cost by position
- Time-to-fill by position
- Cost breakdown (advertising, agency fees, etc.)
- Cost per hire by department
- Hire source effectiveness
- Recruitment ROI

**Filters:**
- Period
- Position
- Department
- Hire source

**Visualizations:**
- Cost trend (line chart)
- Cost by position (bar chart)
- Cost breakdown (pie chart)
- Time-to-fill vs cost (scatter plot)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **7.2 Benefits Cost Report**
**Purpose:** Track and manage employee benefits expenses

**Key Metrics:**
- Total benefits cost by period
- Benefits cost per employee
- Benefits enrollment by type
- Benefits utilization rates
- Cost by benefit category
- Benefits cost trend
- Benefits cost as % of payroll

**Filters:**
- Period
- Benefit type
- Department
- Building/Zone

**Visualizations:**
- Benefits cost trend (line chart)
- Cost by benefit type (pie chart)
- Enrollment vs utilization (comparison)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **7.3 Expense Report**
**Purpose:** Track employee expense claims

**Key Metrics:**
- Total expenses by period
- Expenses by category
- Expenses by employee/department
- Average expense claim amount
- Approval/rejection rates
- Processing time
- Budget vs actual expenses

**Filters:**
- Period
- Expense category
- Department
- Employee
- Status (pending, approved, rejected)

**Visualizations:**
- Expense trend (line chart)
- Expenses by category (pie chart)
- Top expense claimants (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** LOW

---

### **Category 8: Workforce Planning**

#### **8.1 Workforce Demographics**
**Purpose:** Understand workforce composition

**Key Metrics:**
- Age distribution
- Gender distribution by department/level
- Nationality mix
- Education level distribution
- Marital status statistics
- Diversity metrics
- Generational breakdown

**Filters:**
- Department
- Building/Zone
- Position level

**Visualizations:**
- Age distribution (histogram)
- Gender by level (stacked bar)
- Nationality distribution (pie chart)
- Education levels (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** LOW

---

#### **8.2 Succession Planning Report**
**Purpose:** Identify and track succession readiness

**Key Metrics:**
- Key position risk assessment
- Internal candidate readiness
- Succession coverage (positions with successors)
- Promotion pipeline analysis
- Critical role coverage
- Development progress of successors

**Filters:**
- Department
- Position level
- Readiness level
- Risk level

**Visualizations:**
- Succession coverage (scorecard)
- Risk assessment matrix (heatmap)
- Pipeline by level (funnel chart)

**Export:** Excel, PDF

**Priority:** LOW

---

#### **8.3 Skills Inventory Report**
**Purpose:** Map organizational skills and gaps

**Key Metrics:**
- Skills by employee/department
- Skills gap analysis
- Critical skills shortage
- Training needs by skill
- Skill proficiency levels
- Skills availability vs requirement

**Filters:**
- Department
- Skill category
- Proficiency level

**Visualizations:**
- Skills matrix (table/heatmap)
- Skills gap (bar chart)
- Skills by department (radar chart)

**Export:** Excel, PDF, CSV

**Priority:** LOW

---

### **Category 9: Employee Relations**

#### **9.1 Disciplinary Action Report**
**Purpose:** Track disciplinary cases and trends

**Key Metrics:**
- Disciplinary cases by type
- Cases by department/building
- Repeat offenders identification
- Resolution time
- Severity distribution
- Outcome tracking (warning, suspension, termination)

**Filters:**
- Period
- Case type
- Department
- Building/Zone
- Severity
- Status

**Visualizations:**
- Cases trend (line chart)
- Cases by type (bar chart)
- Cases by department (bar chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **9.2 Grievance Report**
**Purpose:** Track employee complaints and resolutions

**Key Metrics:**
- Open vs closed grievances
- Average resolution time
- Grievance categories
- Department-wise patterns
- Satisfaction with resolution
- Escalation rate

**Filters:**
- Period
- Status
- Category
- Department
- Building/Zone

**Visualizations:**
- Grievance trend (line chart)
- Resolution time (bar chart)
- Grievances by category (pie chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

#### **9.3 Exit Interview Analysis**
**Purpose:** Analyze reasons for employee departures

**Key Metrics:**
- Exit interview completion rate
- Reasons for leaving (categorized)
- Satisfaction scores
- Would recommend company (%)
- Issues raised
- Improvement recommendations
- Regrettable vs non-regrettable turnover

**Filters:**
- Period
- Department
- Position
- Reason category

**Visualizations:**
- Reasons for leaving (pie chart)
- Satisfaction scores (bar chart)
- Trend over time (line chart)

**Export:** Excel, PDF, CSV

**Priority:** MEDIUM

---

### **Category 10: Custom Dashboard Reports**

#### **10.1 Executive Dashboard**
**Purpose:** High-level organizational metrics for leadership

**Key Widgets:**
- Current headcount
- Turnover rate (monthly/annual)
- Average tenure
- Attendance rate
- Total payroll cost
- Open positions
- Compliance alerts
- Key performance indicators
- Budget utilization

**Filters:**
- Period
- Department (optional)

**Features:**
- Real-time data
- Drill-down capability
- Alerts and notifications
- Export to PDF

**Priority:** HIGH

---

#### **10.2 Manager Self-Service Dashboard**
**Purpose:** Department managers' team overview

**Key Widgets:**
- Team attendance today
- Team leave calendar (upcoming)
- Pending approvals (leave, overtime, expenses)
- Team performance metrics
- Birthday/anniversary reminders
- Open requisitions
- Team documents pending

**Filters:**
- Date range
- Team member

**Features:**
- Quick approve/reject actions
- Team communication
- Export capabilities

**Priority:** MEDIUM

---

#### **10.3 Employee Self-Service Dashboard**
**Purpose:** Individual employee personal records

**Key Widgets:**
- Personal attendance history
- Leave balance
- Pay slip access
- Training records
- Benefits enrollment
- Documents uploaded
- Performance reviews
- Time off requests status

**Features:**
- Self-service requests
- Document upload
- Personal information update
- Export personal data

**Priority:** MEDIUM

---

## Implementation Priority Matrix

### **High Priority (Implement First)**
1. **Employee Turnover Report** - Critical for retention strategies
2. **Headcount Report** - Essential for workforce planning
3. **Leave Balance Report** - Operational necessity
4. **Work Permit & Visa Expiry Report** - Legal compliance
5. **Payroll Cost Analysis** - Financial management
6. **Absenteeism Report** - Productivity management
7. **Labor Law Compliance Report** - Legal risk mitigation
8. **Contract Expiry Report** - Planning and compliance
9. **Executive Dashboard** - Management visibility

### **Medium Priority**
10. Time & Attendance Summary
11. Late Coming Analysis
12. Training Effectiveness Report
13. Project Staffing Report
14. Department Performance Dashboard
15. Shift Coverage Report
16. Employee Document Status
17. Disciplinary Action Report
18. Grievance Report
19. Exit Interview Analysis
20. Manager Self-Service Dashboard
21. Employee Self-Service Dashboard
22. Salary Distribution Report
23. Deductions Report
24. Audit Trail Report
25. Cost-per-Hire Report
26. Benefits Cost Report
27. New Hires Report

### **Lower Priority (Nice to Have)**
28. Building/Zone Occupancy Report
29. Workforce Demographics
30. Skills Inventory Report
31. Succession Planning Report
32. Bonus & Incentive Report
33. Expense Report

---

## Common Report Features

### **Standard Filters (Apply to Most Reports)**
- Date range (from/to)
- Department
- Building
- Zone
- Floor
- Employee (search/select)
- Status (where applicable)

### **Standard Export Options**
- Excel (.xlsx)
- PDF
- CSV

### **Standard Visualizations**
- Line charts (trends over time)
- Bar charts (comparisons)
- Pie charts (distributions)
- Tables (detailed data)
- Heatmaps (patterns)

### **Standard Features**
- Pagination (for large datasets)
- Sorting (by column)
- Search functionality
- Print-friendly layout
- Mobile responsive design
- Email scheduling (for regular reports)
- Saved filter preferences
- Report scheduling and automation

---

## Technical Implementation Notes

### **Architecture Considerations**
1. **Report Engine**: Consider using Django ORM with aggregation functions
2. **Caching**: Implement Redis caching for frequently accessed reports
3. **Background Jobs**: Use Celery for long-running report generation
4. **Export Libraries**:
   - Excel: `openpyxl` or `xlsxwriter`
   - PDF: `weasyprint` or `reportlab`
   - Charts: `Chart.js` or `plotly`
5. **Performance**: Index database fields used in report queries
6. **Permissions**: Role-based access control for sensitive reports

### **Design Consistency**
- Follow existing report template patterns
- Maintain consistent filter layouts
- Use standardized color schemes
- Implement responsive tables
- Ensure print-friendly CSS

### **Data Privacy**
- Implement data access controls
- Audit trail for sensitive reports
- Data masking for personal information (where needed)
- GDPR compliance considerations

---

## Next Steps

1. **Review and Prioritize**: Stakeholders review and confirm priority list
2. **Technical Specification**: Detailed specs for high-priority reports
3. **Database Schema Review**: Ensure all required data points are captured
4. **UI/UX Mockups**: Design report layouts
5. **Development Sprints**: Implement in priority order
6. **Testing**: UAT with actual users
7. **Training**: Train users on new reports
8. **Documentation**: User guides and admin documentation

---

## Document Version Control

- **Version**: 1.0
- **Date**: 2025-11-06
- **Author**: Analysis of NextHR System
- **Status**: Draft - Awaiting Review

---

## Appendix: Current Report Locations

### File Paths Reference
- Attendance Reports: `templates/attendance/reports.html`
- Overtime Reports: `templates/attendance/overtime_report.html`
- Payroll Reports: `templates/payroll/reports/index.html`
- Foreign/Khmer Report: `hr/templates/hr/foreign_khmer_report.html`
- Staff Report: `hr/templates/hr/staff_report.html`
- Worker Reports Dashboard: `hr/templates/hr/worker_reports_dashboard.html`
- Payment Reports: `templates/payments/reports.html`
- Overdue Report: `templates/billing/overdue_report.html`

### View Functions Reference
- `attendance/views.py:997` - attendance_report
- `attendance/views.py:1266` - overtime_report
- `payroll/views.py:993` - payroll_reports
- `hr/views.py:685` - foreign_khmer_report
- `hr/views.py:848` - staff_report
- `hr/views.py:644` - worker_reports_dashboard
- `payments/views.py:303` - payment_reports
- `billing/views.py:830` - overdue_report
- `training/views.py:640` - reports_overview
