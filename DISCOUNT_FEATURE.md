# Discount Feature Implementation

## Overview

Complete discount feature supporting both **line-item discounts** (per product) and **invoice-level discounts** (entire order). All discount data is persisted to the database for tracking and reporting.

## Features

### 1. Line-Item Discount
- Apply discount to individual products in the cart
- Supports percentage (e.g., 10% off) and fixed amount (e.g., $5 off)
- Visual indicator showing discount on each item
- Automatically recalculates item totals

### 2. Invoice-Level Discount
- Apply discount to the entire order subtotal
- Supports percentage and fixed amount
- Applied after line-item discounts
- Included in order total calculation

### 3. Backend Persistence
- All discounts saved to database
- Track discount history for analytics
- Support for discount reason/notes
- Proper calculation order: Base Price → Line Discount → Subtotal → Invoice Discount → Tax → Total

## Database Schema

### Orders Table
```sql
ALTER TABLE orders ADD COLUMN subtotal DOUBLE NULL;
ALTER TABLE orders ADD COLUMN discount_type VARCHAR(20) NULL;
ALTER TABLE orders ADD COLUMN discount_value DOUBLE NULL;
ALTER TABLE orders ADD COLUMN discount_amount DOUBLE NULL;
ALTER TABLE orders ADD COLUMN discount_reason VARCHAR(500) NULL;
ALTER TABLE orders ADD COLUMN tax_amount DOUBLE NULL;
```

### Order Items Table
```sql
ALTER TABLE order_items ADD COLUMN discount_type VARCHAR(20) NULL;
ALTER TABLE order_items ADD COLUMN discount_value DOUBLE NULL;
ALTER TABLE order_items ADD COLUMN discount_amount DOUBLE NULL;
ALTER TABLE order_items ADD COLUMN discount_reason VARCHAR(500) NULL;
```

## Backend Implementation

### 1. Discount Enum
**File**: `com.ng.domain.DiscountType.java`

```java
public enum DiscountType {
    PERCENTAGE,    // Percentage discount (e.g., 10%)
    FIXED_AMOUNT,  // Fixed dollar amount (e.g., $5)
    NONE           // No discount
}
```

### 2. Order Entity Updates
**File**: `com.ng.modal.Order.java`

Added fields:
- `subtotal` - Order subtotal before invoice discount
- `discountType` - Type of invoice discount
- `discountValue` - Discount value (percentage or amount)
- `discountAmount` - Calculated discount in dollars
- `discountReason` - Optional reason
- `taxAmount` - Tax amount

### 3. OrderItem Entity Updates
**File**: `com.ng.modal.OrderItem.java`

Added fields:
- `discountType` - Type of line-item discount
- `discountValue` - Discount value
- `discountAmount` - Calculated discount
- `discountReason` - Optional reason

New method:
```java
public void calculateDiscountAmount() {
    // Calculates discount based on type and value
    // Updates discountAmount field
}
```

### 4. Order Service Logic
**File**: `com.ng.service.impl.OrderServiceImpl.java`

Calculation flow:
1. Calculate line-item discount for each item
2. Sum item totals to get subtotal (already includes line discounts)
3. Apply invoice-level discount to subtotal
4. Add tax
5. Calculate final total

```java
// Calculate subtotal (including line-item discounts)
double subtotal = orderItems.stream()
    .mapToDouble(OrderItem::getTotalPrice)
    .sum();

// Apply invoice-level discount
if (dto.getDiscountType() == DiscountType.PERCENTAGE) {
    invoiceDiscountAmount = subtotal * (dto.getDiscountValue() / 100.0);
} else if (dto.getDiscountType() == DiscountType.FIXED_AMOUNT) {
    invoiceDiscountAmount = Math.min(dto.getDiscountValue(), subtotal);
}

// Calculate final total
double total = subtotal - invoiceDiscountAmount + taxAmount;
```

## Frontend Implementation

### 1. Cart State Updates
**File**: `pos-frontend-vite/src/Redux Toolkit/features/cart/cartSlice.js`

New state:
- Each cart item has `discount: { type, value }` field
- Invoice-level discount in `state.cart.discount`

New actions:
- `setItemDiscount` - Set line-item discount
- `setDiscount` - Set invoice-level discount (already existed)

New selectors:
- `selectItemDiscount(item)` - Calculate discount for specific item
- `selectSubtotal` - Updated to include line-item discounts

### 2. Cart Item Component
**File**: `pos-frontend-vite/src/pages/cashier/cart/CartItem.jsx`

Features:
- Percent icon button opens discount popover
- Radio buttons for discount type (none/percentage/fixed)
- Input field for discount value
- Visual badge showing active discount
- Strikethrough original price when discounted
- Shows final price after discount

### 3. Payment Processing
**File**: `pos-frontend-vite/src/pages/cashier/payment/PaymentDialog.jsx`

Updated `processPayment()` to include:
- `subtotal` - Order subtotal
- `discountType` - Mapped to backend enum
- `discountValue` - Discount value
- `discountAmount` - Calculated discount
- `taxAmount` - Tax amount
- Item-level discount data for each product

## Usage

### Cashier Workflow

1. **Add items to cart**
2. **Apply line-item discount (optional)**:
   - Click percent icon on cart item
   - Select discount type
   - Enter discount value
   - Click "Apply Discount"
3. **Apply invoice discount (optional)**:
   - Enter discount value in discount section
   - Select percentage or fixed amount
4. **Process payment**
   - All discount data automatically saved

### Discount Calculation Example

**Cart:**
- Product A: $100 x 2 = $200 (10% line discount = $20 off)
- Product B: $50 x 1 = $50 (no discount)

**Calculation:**
```
Product A after line discount: $200 - $20 = $180
Product B: $50
Subtotal: $180 + $50 = $230

Invoice discount (5%): $230 * 0.05 = $11.50
After invoice discount: $230 - $11.50 = $218.50

Tax (18%): $218.50 * 0.18 = $39.33
Total: $218.50 + $39.33 = $257.83
```

## API Endpoints

### Create Order with Discount
```http
POST /api/orders
Content-Type: application/json

{
  "subtotal": 230.00,
  "totalAmount": 257.83,
  "discountType": "PERCENTAGE",
  "discountValue": 5.0,
  "discountAmount": 11.50,
  "discountReason": "Loyalty customer",
  "taxAmount": 39.33,
  "branchId": 1,
  "cashierId": 1,
  "customer": {...},
  "items": [
    {
      "productId": 10,
      "quantity": 2,
      "price": 100.00,
      "productType": "RETAIL",
      "discountType": "PERCENTAGE",
      "discountValue": 10.0,
      "discountAmount": 20.00
    },
    {
      "productId": 11,
      "quantity": 1,
      "price": 50.00,
      "productType": "RETAIL",
      "discountType": "NONE",
      "discountValue": 0,
      "discountAmount": 0
    }
  ],
  "paymentType": "CASH"
}
```

## Migration

### Flyway Migration File
**Location**: `pos-backend/src/main/resources/db/migration/V3__Add_Discount_Support.sql`

The migration:
1. Adds discount columns to `orders` and `order_items` tables
2. Creates indexes for discount queries
3. Migrates existing data (sets default values)

Run migration:
```bash
mvn flyway:migrate
```

Or start the application (auto-migrates if `flyway.enabled=true`)

## Testing Checklist

### Backend Tests
- [ ] Order creation with no discounts
- [ ] Order with line-item discount only
- [ ] Order with invoice discount only
- [ ] Order with both discount types
- [ ] Percentage discount calculation
- [ ] Fixed amount discount calculation
- [ ] Discount exceeding item price (should cap at item price)
- [ ] Order persistence with discount data
- [ ] Order retrieval includes discount fields

### Frontend Tests
- [ ] Line-item discount UI appears
- [ ] Discount popover opens/closes
- [ ] Discount type selection works
- [ ] Discount value input validation
- [ ] Discount applied updates cart total
- [ ] Invoice discount UI works
- [ ] Both discounts can coexist
- [ ] Cart summary shows correct totals
- [ ] Payment dialog shows correct total
- [ ] Order submission includes discount data

### Integration Tests
- [ ] Create order with discounts via API
- [ ] Verify discount data persisted in database
- [ ] Retrieve order and check discount fields
- [ ] View order history shows discounts
- [ ] Reports include discount data

## UI Components

### Line-Item Discount Button
```jsx
<Popover>
  <PopoverTrigger>
    <Button variant="outline" size="sm">
      <Percent className="w-4 h-4" />
    </Button>
  </PopoverTrigger>
  <PopoverContent>
    <RadioGroup value={discountType}>
      <RadioGroupItem value="none" />
      <RadioGroupItem value="percentage" />
      <RadioGroupItem value="fixed" />
    </RadioGroup>
    <Input type="number" value={discountValue} />
    <Button onClick={applyDiscount}>Apply</Button>
  </PopoverContent>
</Popover>
```

### Invoice Discount Section
Already implemented in `DiscountSection.jsx`

## Troubleshooting

### Discount not saving
- Check browser console for API errors
- Verify backend receives discount data
- Check Flyway migration ran successfully

### Incorrect calculation
- Verify calculation order: line → subtotal → invoice → tax
- Check discount type mapping (frontend → backend)
- Ensure rounding is consistent

### Migration fails
- Check if columns already exist
- Verify database user has ALTER permissions
- Review Flyway migration logs

## Future Enhancements

1. **Discount Rules Engine**
   - Automatic discounts based on rules
   - Buy X get Y free
   - Minimum purchase discounts

2. **Coupon Codes**
   - Promo code entry
   - Code validation
   - Usage tracking

3. **Discount Approval Workflow**
   - Require manager approval for large discounts
   - Discount authorization levels

4. **Analytics Dashboard**
   - Total discounts given
   - Discount trends
   - Revenue impact analysis

5. **Customer-Specific Discounts**
   - VIP customer discounts
   - Loyalty program integration
   - Birthday discounts

## Files Modified

### Backend
- `com/ng/domain/DiscountType.java` (new)
- `com/ng/modal/Order.java`
- `com/ng/modal/OrderItem.java`
- `com/ng/payload/dto/OrderDTO.java`
- `com/ng/payload/dto/OrderItemDTO.java`
- `com/ng/service/impl/OrderServiceImpl.java`
- `com/ng/mapper/OrderMapper.java`
- `com/ng/mapper/OrderItemMapper.java`
- `db/migration/V3__Add_Discount_Support.sql` (new)

### Frontend
- `src/Redux Toolkit/features/cart/cartSlice.js`
- `src/pages/cashier/cart/CartItem.jsx`
- `src/pages/cashier/cart/CartSection.jsx`
- `src/pages/cashier/payment/PaymentDialog.jsx`

## Status

**Backend**: ✅ Complete
**Frontend**: ✅ Complete
**Database Migration**: ✅ Created
**Testing**: ⏳ Pending (requires Maven/npm build)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-14
**Author**: Claude Code
