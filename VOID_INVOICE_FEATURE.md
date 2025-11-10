# Void Invoice Feature

## Overview

Complete void invoice functionality for handling order cancellations, mistakes, and refunds in F&B/Restaurant operations. Includes comprehensive audit trail, authorization, and reporting capabilities.

## Features

### Core Functionality
1. **Void Completed Orders** - Cancel orders that have been processed
2. **Required Authorization** - Mandatory reason and detailed notes
3. **Audit Trail** - Complete logging of who, when, why
4. **Manager Approval** - Optional manager verification
5. **Prevention Controls** - Cannot void already-voided orders
6. **Statistics & Reports** - Track void patterns and amounts

### Business Rules

- ✅ Can only void COMPLETED orders
- ✅ Cannot void already-voided orders
- ✅ Requires mandatory void reason
- ✅ Requires detailed explanation (min 10 characters)
- ✅ Optionally requires manager approval
- ✅ Audit trail permanently records void action
- ✅ Changes order status to CANCELLED
- ✅ Void action is irreversible

## Void Reasons

The system supports 10 predefined void reasons:

| Reason | Use Case |
|--------|----------|
| **CUSTOMER_COMPLAINT** | Customer dissatisfaction with food/service |
| **ENTRY_ERROR** | Staff entered wrong items |
| **WRONG_ORDER** | Kitchen prepared wrong items |
| **KITCHEN_ERROR** | Food preparation mistake |
| **CUSTOMER_CANCELLATION** | Customer cancelled before service |
| **PAYMENT_ISSUE** | Payment dispute or problem |
| **DUPLICATE_ORDER** | Same order entered twice |
| **MANAGER_DISCRETION** | Goodwill gesture |
| **SYSTEM_ERROR** | Technical/system malfunction |
| **OTHER** | Any other reason (must explain in notes) |

## Database Schema

### Orders Table Updates

```sql
ALTER TABLE orders
ADD COLUMN is_voided BOOLEAN DEFAULT FALSE,
ADD COLUMN void_reason VARCHAR(50) NULL,
ADD COLUMN void_notes VARCHAR(1000) NULL,
ADD COLUMN voided_by BIGINT NULL,
ADD COLUMN voided_at DATETIME NULL,
ADD COLUMN void_approved_by BIGINT NULL;
```

**New Fields**:
- `is_voided` - Boolean flag indicating voided status
- `void_reason` - Enum reason for void
- `void_notes` - Detailed explanation (up to 1000 chars)
- `voided_by` - Foreign key to users table (who performed void)
- `voided_at` - Timestamp of void action
- `void_approved_by` - Foreign key to users table (manager approval)

### Indexes
```sql
CREATE INDEX idx_orders_is_voided ON orders(is_voided);
CREATE INDEX idx_orders_void_reason ON orders(void_reason);
CREATE INDEX idx_orders_voided_at ON orders(voided_at);
CREATE INDEX idx_orders_voided_by ON orders(voided_by);
```

## Backend Implementation

### 1. Void Reason Enum
**File**: `com.ng.domain.VoidReason.java`

```java
public enum VoidReason {
    CUSTOMER_COMPLAINT,
    ENTRY_ERROR,
    WRONG_ORDER,
    KITCHEN_ERROR,
    CUSTOMER_CANCELLATION,
    PAYMENT_ISSUE,
    DUPLICATE_ORDER,
    MANAGER_DISCRETION,
    SYSTEM_ERROR,
    OTHER
}
```

### 2. Request DTO
**File**: `com.ng.payload.request.VoidInvoiceRequest.java`

```java
{
  "orderId": 123,
  "voidReason": "CUSTOMER_COMPLAINT",
  "voidNotes": "Customer complained about cold food and requested refund",
  "managerId": 5,              // Optional
  "managerPassword": "xxxxx"   // Optional
}
```

### 3. Service Layer
**File**: `com.ng.service.VoidInvoiceService.java`

Methods:
- `voidInvoice(request, userId)` - Void an invoice
- `getVoidedOrders(branchId, startDate, endDate)` - Get void history
- `getVoidStatistics(branchId, startDate, endDate)` - Get void stats

**Business Logic** (`VoidInvoiceServiceImpl.java`):
```java
// Validations
✓ Order exists
✓ Order not already voided
✓ Order status is COMPLETED
✓ User exists
✓ Manager exists (if provided)

// Void Process
1. Set isVoided = true
2. Set voidReason, voidNotes
3. Set voidedBy, voidedAt
4. Set voidApprovedBy (if manager approval)
5. Change status to CANCELLED
6. Save order
7. Log void action
```

### 4. REST API
**File**: `com.ng.controller.VoidInvoiceController.java`

Endpoints:
```
POST /api/void-invoice
GET  /api/void-invoice/branch/{branchId}
GET  /api/void-invoice/statistics/branch/{branchId}
```

## Frontend Implementation

### 1. Void Invoice Dialog
**File**: `VoidInvoiceDialog.jsx`

**Features**:
- Order summary display
- Reason dropdown (10 options)
- Detailed notes textarea (required, min 10 chars)
- Manager password field (optional)
- Warning alert
- Loading state
- Validation

**Usage**:
```jsx
<VoidInvoiceDialog
  open={showVoidDialog}
  onOpenChange={setShowVoidDialog}
  order={selectedOrder}
/>
```

### 2. Void Invoice Report
**File**: `VoidInvoiceReport.jsx`

**Features**:
- Date range filter
- Statistics cards (total voids, amount, top reason, impact %)
- Voided orders table
- CSV export
- Color-coded reason badges

## API Usage Examples

### 1. Void an Invoice

**Request**:
```bash
POST /api/void-invoice
Content-Type: application/json
Authorization: Bearer {token}

{
  "orderId": 456,
  "voidReason": "CUSTOMER_COMPLAINT",
  "voidNotes": "Customer complained that steak was overcooked. Requested full refund. Manager approved goodwill gesture.",
  "managerId": 10,
  "managerPassword": "manager123"
}
```

**Response**:
```json
{
  "id": 456,
  "totalAmount": 150.00,
  "status": "CANCELLED",
  "isVoided": true,
  "voidReason": "CUSTOMER_COMPLAINT",
  "voidNotes": "Customer complained that steak was overcooked...",
  "voidedById": 5,
  "voidedByName": "John Cashier",
  "voidedAt": "2025-10-14T15:30:00",
  "voidApprovedById": 10,
  "voidApprovedByName": "Sarah Manager"
}
```

### 2. Get Voided Orders

**Request**:
```bash
GET /api/void-invoice/branch/1?startDate=2025-10-01T00:00:00&endDate=2025-10-31T23:59:59
```

**Response**:
```json
[
  {
    "id": 456,
    "totalAmount": 150.00,
    "isVoided": true,
    "voidReason": "CUSTOMER_COMPLAINT",
    "voidNotes": "Customer complained...",
    "voidedByName": "John Cashier",
    "voidedAt": "2025-10-14T15:30:00"
  },
  {
    "id": 457,
    "totalAmount": 75.00,
    "isVoided": true,
    "voidReason": "ENTRY_ERROR",
    "voidNotes": "Accidentally entered wrong items",
    "voidedByName": "Jane Server",
    "voidedAt": "2025-10-15T10:15:00"
  }
]
```

### 3. Get Void Statistics

**Request**:
```bash
GET /api/void-invoice/statistics/branch/1?startDate=2025-10-01T00:00:00&endDate=2025-10-31T23:59:59
```

**Response**:
```json
{
  "totalVoidedOrders": 15,
  "totalVoidedAmount": 2250.00,
  "voidsByReason": {
    "CUSTOMER_COMPLAINT": 8,
    "ENTRY_ERROR": 4,
    "KITCHEN_ERROR": 2,
    "OTHER": 1
  },
  "voidsByUser": {
    "John Cashier": 6,
    "Jane Server": 5,
    "Mike Waiter": 4
  }
}
```

## Business Scenarios

### Scenario 1: Customer Complaint

**Situation**: Customer complains steak is overcooked, wants refund

**Process**:
1. Manager reviews complaint
2. Cashier opens order #456
3. Clicks "Void Invoice" button
4. Selects reason: "CUSTOMER_COMPLAINT"
5. Notes: "Customer complained steak overcooked. Full refund approved."
6. Enters manager password
7. Confirms void

**Result**:
- Order #456 marked as voided
- Status changed to CANCELLED
- Audit log created
- Statistics updated
- Customer receives refund

### Scenario 2: Entry Error

**Situation**: Cashier entered wrong items, customer hasn't received yet

**Process**:
1. Cashier realizes mistake immediately
2. Opens order #457
3. Clicks "Void Invoice"
4. Selects reason: "ENTRY_ERROR"
5. Notes: "Entered Table 5 items instead of Table 6"
6. Confirms void
7. Creates new correct order

**Result**:
- Wrong order voided
- New correct order created
- No impact to kitchen (caught early)
- Audit trail for accountability

### Scenario 3: Duplicate Order

**Situation**: System glitch created duplicate order

**Process**:
1. Manager notices duplicate order
2. Opens duplicate order #458
3. Clicks "Void Invoice"
4. Selects reason: "DUPLICATE_ORDER"
5. Notes: "System created duplicate due to network timeout"
6. Confirms void

**Result**:
- Duplicate order removed
- Original order remains
- Statistics track system issues
- Can identify technical problems

## Migration

### Run Migration

**Automatic** (on application start):
```bash
mvn spring-boot:run
```

**Manual**:
```bash
mvn flyway:migrate
```

### Migration File
`V5__Add_Void_Invoice_Feature.sql` includes:
- Add void columns to orders table
- Create foreign keys to users table
- Create indexes for performance
- Set default values for existing orders

## Integration with Other Features

### Payment Processing
- TODO: Trigger refund when invoice voided
- TODO: Update payment gateway
- TODO: Create credit note

### Inventory Management
- TODO: Return items to inventory (if applicable)
- TODO: Update stock levels
- TODO: Prevent wastage tracking confusion

### Kitchen Display System
- TODO: Cancel kitchen orders
- TODO: Notify kitchen staff
- TODO: Remove from active displays

### Reports
- ✅ Void statistics included in reporting
- ✅ Filter orders by void status
- ✅ Track void patterns
- ✅ Export void history

## Security & Authorization

### User Permissions
- **Cashier**: Can void with reason (low amounts)
- **Manager**: Required approval for high amounts
- **Admin**: Full void access + statistics

### Authorization Levels
1. **Level 1** (< $50): Cashier only, no manager approval
2. **Level 2** ($50-$200): Requires manager approval
3. **Level 3** (> $200): Requires admin approval

*Note: Implement authorization levels based on business needs*

### Audit Trail
Every void action logs:
- User who initiated
- Timestamp
- Reason code
- Detailed notes
- Manager approval (if any)
- Original order details

## Reporting & Analytics

### Key Metrics
1. **Void Rate**: (Voided Orders / Total Orders) × 100%
2. **Void Impact**: Total $ amount voided
3. **Top Reasons**: Which reasons most common
4. **Staff Performance**: Voids by employee
5. **Time Trends**: Voids by day/week/month

### Report Features
- Date range filtering
- Export to CSV
- Visual statistics cards
- Detailed void history table
- Color-coded reason badges

## Error Handling

### Common Errors

**"Order not found"**
- Order ID doesn't exist
- Check order number

**"Order already voided"**
- Cannot void twice
- Check order status first

**"Can only void completed orders"**
- Order must be COMPLETED
- Cannot void PENDING/CANCELLED orders

**"Validation Error: Notes required"**
- Void notes are mandatory
- Minimum 10 characters required

**"Manager approval required"**
- High-value void needs approval
- Get manager password

## Testing Checklist

### Backend Tests
- [ ] Void invoice with valid data
- [ ] Cannot void non-existent order
- [ ] Cannot void already-voided order
- [ ] Cannot void non-completed order
- [ ] Validation requires void reason
- [ ] Validation requires notes (min length)
- [ ] Manager approval validation
- [ ] Audit trail created
- [ ] OrderDTO includes void fields
- [ ] Statistics calculated correctly

### Frontend Tests
- [ ] Dialog opens/closes correctly
- [ ] Reason dropdown populates
- [ ] Notes validation works
- [ ] Manager password optional
- [ ] Loading state displays
- [ ] Success toast shows
- [ ] Error toast shows
- [ ] Report loads data
- [ ] Date filter works
- [ ] CSV export works
- [ ] Statistics display correctly

### Integration Tests
- [ ] Void persists to database
- [ ] Order status changes to CANCELLED
- [ ] Void fields populated correctly
- [ ] Foreign keys maintained
- [ ] Indexes working
- [ ] Report queries performant

## Future Enhancements

1. **Refund Processing**
   - Auto-trigger refund
   - Payment gateway integration
   - Credit note generation

2. **Approval Workflow**
   - Multi-level authorization
   - Email notifications
   - Pending approval queue

3. **Advanced Analytics**
   - Void trend analysis
   - Predictive alerts
   - Pattern detection

4. **Inventory Integration**
   - Auto-return items to stock
   - Wastage tracking
   - Cost analysis

5. **Mobile Void**
   - Void from mobile app
   - Photo evidence upload
   - Digital signatures

## Files Created/Modified

### Backend
- `com/ng/domain/VoidReason.java` (new)
- `com/ng/modal/Order.java` - Added void fields
- `com/ng/payload/request/VoidInvoiceRequest.java` (new)
- `com/ng/payload/dto/OrderDTO.java` - Added void fields
- `com/ng/service/VoidInvoiceService.java` (new)
- `com/ng/service/impl/VoidInvoiceServiceImpl.java` (new)
- `com/ng/controller/VoidInvoiceController.java` (new)
- `com/ng/mapper/OrderMapper.java` - Added void field mapping
- `db/migration/V5__Add_Void_Invoice_Feature.sql` (new)

### Frontend
- `src/components/VoidInvoiceDialog.jsx` (new)
- `src/pages/Branch Manager/Reports/VoidInvoiceReport.jsx` (new)

## Status

**Backend**: ✅ Complete
**Frontend**: ✅ Complete
**Database Migration**: ✅ Created
**Audit Logging**: ✅ Implemented
**Testing**: ⏳ Pending
**Documentation**: ✅ Complete

---

**Version**: 1.0.0
**Last Updated**: 2025-10-14
**Author**: Claude Code
