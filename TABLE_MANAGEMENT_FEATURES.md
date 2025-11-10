# Table Management Features - F&B/Restaurant

## Overview

Complete table management system for F&B and restaurant operations with three core features:
1. **Change Table** - Move an order from one table to another
2. **Merge Tables** - Combine orders from multiple tables into one
3. **Split Bill** - Divide a table's order into multiple separate bills

## Features

### 1. Change Table

**Use Case**: Customer requests to move to a different table (bigger/smaller, better location, etc.)

**Workflow**:
1. Waiter selects the active order
2. Chooses the new table (must be available)
3. System moves the order to the new table
4. Old table becomes available
5. New table status changes to occupied

**Business Rules**:
- Can only move orders that are PENDING (not completed)
- Target table must be AVAILABLE
- Original table is automatically freed
- Table occupancy timestamps are updated

### 2. Merge Tables

**Use Case**: Multiple groups want to join together, or families seated at separate tables

**Workflow**:
1. Waiter selects 2+ tables with active orders
2. Chooses target table (where merged order will be)
3. System combines all items into one order
4. All source orders are deleted (items transferred)
5. Only target table remains occupied
6. Other tables become available

**Business Rules**:
- Requires at least 2 orders to merge
- Cannot merge completed orders
- All items combined into single order
- Totals (subtotal, discount, tax) are summed
- Source orders are deleted after merge
- Only target table remains occupied

### 3. Split Bill

**Use Case**: Group wants to pay separately ("separate checks")

**Workflow**:
1. Waiter selects the order to split
2. Creates split groups (2 or more)
3. Assigns items to each group
4. System creates separate orders for each group
5. Each split order can be paid independently
6. Original order is marked as completed

**Business Rules**:
- Requires at least 2 split groups
- Each group must have at least 1 item
- Original order items are copied to split orders
- Split orders reference parent order ID
- Each split order can have different customer
- All splits remain at the same table

## Database Schema

### Orders Table Updates

```sql
ALTER TABLE orders
ADD COLUMN table_id BIGINT NULL,
ADD COLUMN order_type VARCHAR(20) NULL,
ADD COLUMN parent_order_id BIGINT NULL,
ADD COLUMN is_split BOOLEAN DEFAULT FALSE,
ADD COLUMN split_number INT NULL;
```

**New Fields**:
- `table_id` - Foreign key to table_layouts
- `order_type` - DINE_IN, TAKEOUT, DELIVERY
- `parent_order_id` - Reference to original order (for split bills)
- `is_split` - Boolean flag indicating split order
- `split_number` - Split sequence (1 of 3, 2 of 3, etc.)

### Table Layouts Table

Already has:
- `current_order_id` - References active order on table
- `status` - AVAILABLE, OCCUPIED, RESERVED, CLEANING
- `occupied_at` - Timestamp when table was occupied

## Backend Implementation

### 1. Request DTOs

**ChangeTableRequest.java**:
```java
{
  "orderId": 123,
  "newTableId": 5,
  "reason": "Customer request"
}
```

**MergeTableRequest.java**:
```java
{
  "sourceOrderIds": [101, 102, 103],
  "targetTableId": 1,
  "reason": "Family gathering"
}
```

**SplitBillRequest.java**:
```java
{
  "originalOrderId": 456,
  "splitGroups": [
    {
      "orderItemIds": [1, 2, 3],
      "customerId": 789
    },
    {
      "orderItemIds": [4, 5],
      "customerId": 790
    }
  ],
  "reason": "Separate payments"
}
```

### 2. Service Layer

**TableManagementService.java** provides:
- `changeTable(ChangeTableRequest)` - Returns updated OrderDTO
- `mergeTables(MergeTableRequest)` - Returns merged OrderDTO
- `splitBill(SplitBillRequest)` - Returns List<OrderDTO>
- `getActiveOrdersByTable(Long tableId)` - Returns active orders

### 3. REST API Endpoints

```
POST /api/table-management/change-table
POST /api/table-management/merge-tables
POST /api/table-management/split-bill
GET  /api/table-management/table/{tableId}/orders
```

## Frontend Implementation

### TableManagement.jsx

**Features**:
- Visual table grid showing status
- Color-coded badges (Green=Available, Red=Occupied, Yellow=Reserved)
- Real-time order information
- Action buttons for all 3 operations

**Dialogs**:
1. **Change Table Dialog**
   - Dropdown to select order
   - Dropdown to select target table (available only)
   - Confirmation button

2. **Merge Tables Dialog**
   - Checkboxes for selecting tables
   - Shows order amounts
   - Requires minimum 2 selections

3. **Split Bill Dialog**
   - Select order to split
   - Create split groups
   - Assign items to groups
   - Shows split count

## API Usage Examples

### 1. Change Table

**Request**:
```bash
POST /api/table-management/change-table
Content-Type: application/json

{
  "orderId": 101,
  "newTableId": 5,
  "reason": "Customer prefers window seat"
}
```

**Response**:
```json
{
  "id": 101,
  "tableId": 5,
  "status": "PENDING",
  "totalAmount": 150.00,
  ...
}
```

### 2. Merge Tables

**Request**:
```bash
POST /api/table-management/merge-tables
Content-Type: application/json

{
  "sourceOrderIds": [101, 102, 103],
  "targetTableId": 1,
  "reason": "Family joining together"
}
```

**Response**:
```json
{
  "id": 101,
  "tableId": 1,
  "subtotal": 425.00,
  "totalAmount": 500.00,
  "items": [...], // All items from 3 orders
  ...
}
```

### 3. Split Bill

**Request**:
```bash
POST /api/table-management/split-bill
Content-Type: application/json

{
  "originalOrderId": 456,
  "splitGroups": [
    {
      "orderItemIds": [1, 2],
      "customerId": 789
    },
    {
      "orderItemIds": [3, 4, 5],
      "customerId": 790
    }
  ]
}
```

**Response**:
```json
[
  {
    "id": 501,
    "parentOrderId": 456,
    "isSplit": true,
    "splitNumber": 1,
    "totalAmount": 75.00,
    "items": [...]
  },
  {
    "id": 502,
    "parentOrderId": 456,
    "isSplit": true,
    "splitNumber": 2,
    "totalAmount": 125.00,
    "items": [...]
  }
]
```

## Business Scenarios

### Scenario 1: Couple Moves to Larger Table

**Initial State**:
- Table T2 (2-seater): Occupied with Order #101
- Table T5 (6-seater): Available

**Customer Action**: More friends arriving, need bigger table

**Solution**: Change Table
1. Waiter clicks "Change Table"
2. Selects Order #101
3. Selects Table T5 as new table
4. Confirms

**Result**:
- Table T2: Available
- Table T5: Occupied with Order #101
- Order continues unchanged

### Scenario 2: Family at 3 Different Tables

**Initial State**:
- Table T1: Order #101 (Dad + kids, $150)
- Table T2: Order #102 (Mom + grandma, $75)
- Table T3: Order #103 (Uncle + aunt, $200)

**Customer Action**: Want to pay together

**Solution**: Merge Tables
1. Waiter clicks "Merge Tables"
2. Selects T1, T2, T3
3. Chooses T1 as target
4. Confirms

**Result**:
- Table T1: Occupied with merged Order ($425 total)
- Table T2: Available
- Table T3: Available
- Single bill with all 3 orders' items

### Scenario 3: Group of 4 Friends Splitting Bill

**Initial State**:
- Table T4: Order #104 with 8 items ($200 total)
  - 2x Burger ($20 each) - Friend A
  - 1x Pasta ($25) - Friend B
  - 2x Salad ($15 each) - Friend B
  - 1x Steak ($50) - Friend C
  - 2x Soda ($5 each) - Shared

**Customer Action**: Each friend pays for their own food

**Solution**: Split Bill
1. Waiter clicks "Split Bill"
2. Selects Order #104
3. Creates 3 groups:
   - Group 1: 2 Burgers + 1 Soda = $45
   - Group 2: 1 Pasta + 2 Salads + 1 Soda = $60
   - Group 3: 1 Steak = $50
4. Confirms

**Result**:
- Original Order #104: Completed
- New Order #201: $45 (Split 1 of 3)
- New Order #202: $60 (Split 2 of 3)
- New Order #203: $50 (Split 3 of 3)
- Each friend pays separately

## Migration

### Run Migration

**Automatic** (on application start):
```bash
# Flyway auto-migrates when application starts
mvn spring-boot:run
```

**Manual**:
```bash
mvn flyway:migrate
```

### Migration File

`V4__Add_Table_Management_Features.sql` includes:
- Add table reference to orders
- Add split bill fields
- Create foreign keys
- Create indexes
- Set default values

## Testing Checklist

### Backend Tests
- [ ] Change table with valid order and table
- [ ] Change table validation (completed order, unavailable table)
- [ ] Merge 2 tables successfully
- [ ] Merge 3+ tables successfully
- [ ] Merge validation (single table, completed orders)
- [ ] Split bill into 2 groups
- [ ] Split bill into 3+ groups
- [ ] Split validation (completed order, empty groups)
- [ ] Table status updates correctly
- [ ] Order totals calculated correctly

### Frontend Tests
- [ ] Table grid displays correctly
- [ ] Status colors accurate
- [ ] Change table dialog works
- [ ] Merge tables dialog works
- [ ] Split bill dialog works
- [ ] API calls successful
- [ ] Error handling displays
- [ ] Toast notifications appear

### Integration Tests
- [ ] Change table updates database
- [ ] Merge tables creates correct order
- [ ] Split bill creates all orders
- [ ] Table statuses persist
- [ ] Kitchen orders updated (if using KDS)

## Error Handling

### Common Errors

**"Order not found"**
- Order ID doesn't exist
- Check order is still active

**"Table not available"**
- Target table is occupied/reserved
- Choose different table

**"Cannot change completed order"**
- Order already paid
- Operation not allowed on completed orders

**"Minimum 2 orders required"**
- Merge needs at least 2 orders
- Select more orders

**"Empty split group"**
- Split group has no items
- Assign items to all groups

## Integration with Existing Features

### Kitchen Display System
- Changed orders maintain kitchen routing
- Merged orders combine kitchen orders
- Split orders create new kitchen orders

### Reservations
- Tables with reservations cannot be used
- Change table respects reservations

### Payment Processing
- Split bills can be paid independently
- Each split has own payment method
- Parent order tracks all splits

## Future Enhancements

1. **Table Transfer History**
   - Audit log of all table changes
   - Reasons tracked

2. **Smart Merge**
   - Auto-suggest tables for merge
   - Based on proximity

3. **Flexible Split**
   - Split by amount (not just items)
   - Percentage-based splits

4. **Table Joining**
   - Physically join tables
   - Update capacity

5. **Mobile Waiter App**
   - Perform operations on tablet
   - Real-time sync

## Files Created/Modified

### Backend
- `com/ng/modal/Order.java` - Added table fields
- `com/ng/payload/request/ChangeTableRequest.java` (new)
- `com/ng/payload/request/MergeTableRequest.java` (new)
- `com/ng/payload/request/SplitBillRequest.java` (new)
- `com/ng/service/TableManagementService.java` (new)
- `com/ng/service/impl/TableManagementServiceImpl.java` (new)
- `com/ng/controller/TableManagementController.java` (new)
- `com/ng/repository/OrderRepository.java` - Added findByTableAndStatus
- `db/migration/V4__Add_Table_Management_Features.sql` (new)

### Frontend
- `src/pages/Branch Manager/Tables/TableManagement.jsx` (new)

## Status

**Backend**: ✅ Complete
**Frontend**: ✅ Complete (Basic UI)
**Database Migration**: ✅ Created
**Testing**: ⏳ Pending
**Documentation**: ✅ Complete

---

**Version**: 1.0.0
**Last Updated**: 2025-10-14
**Author**: Claude Code
