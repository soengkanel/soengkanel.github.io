# Query Migration Fixes

## Issue
After updating `OrderItem` to use polymorphic product references (productId + productType) instead of a direct @ManyToOne relationship to Product, several JPQL queries broke with the error:
```
PathElementException: Could not resolve attribute 'product' of 'com.ng.modal.OrderItem'
```

## Files Fixed

### 1. **ProductRepository.java** ✅
**Line 39:** Fixed `getSalesGroupedByCategory` query
- **Before:** `JOIN oi.product p`
- **After:** `JOIN Product p ON p.id = oi.productId`
- **Added:** Filter by `productType = 'RETAIL'`
- **Changed:** Use `oi.price` instead of `p.sellingPrice` (price is already stored in OrderItem)

**Line 64:** Fixed `findLowStockProducts` query
- **Before:** `SELECT i.product.id`
- **After:** `SELECT 1 ... WHERE i.product.id = p.id` (using EXISTS instead of NOT IN)

### 2. **MenuItemRepository.java** ✅
**Line 119:** Fixed `findPopularMenuItems` query
- **Before:** `JOIN OrderItem oi ON oi.product.id = mi.id`
- **After:** `JOIN OrderItem oi ON oi.productId = mi.id`
- **Added:** Filter by `productType = 'MENU_ITEM'`

### 3. **OrderItemRepository.java** ✅
**Line 16:** Fixed `getTopProductsByQuantity` query
- **Before:** `JOIN oi.product p` then access `p.id, p.name`
- **After:** Use `oi.productId, oi.productName` directly (snapshot fields in OrderItem)

**Line 33:** Fixed `getCategoryWiseSales` query
- **Before:** `JOIN oi.product p JOIN p.category c`
- **After:** `LEFT JOIN` both `RetailProduct` and `MenuItem` and use `CASE` statement to determine category
- **Why:** OrderItems can now reference either retail products or menu items

### 4. **Inventory.java** ✅
**Updated entity to support polymorphic reference**
- Added `productId` and `productType` fields
- Added snapshot fields (`productName`, `productSku`)
- Kept legacy `product` relationship for backward compatibility (read-only)

## Migration Impact

### Database Changes Required:
```sql
-- OrderItem table (already done in migration guide)
ALTER TABLE order_items ADD COLUMN product_type VARCHAR(20) NOT NULL DEFAULT 'RETAIL';
ALTER TABLE order_items ADD COLUMN product_name VARCHAR(255);
ALTER TABLE order_items ADD COLUMN product_sku VARCHAR(255);

-- Inventory table (new)
ALTER TABLE inventories ADD COLUMN product_type VARCHAR(20) NOT NULL DEFAULT 'RETAIL';
ALTER TABLE inventories ADD COLUMN product_name VARCHAR(255);
ALTER TABLE inventories ADD COLUMN product_sku VARCHAR(255);

-- Update existing data
UPDATE order_items oi
INNER JOIN products p ON oi.product_id = p.id
SET oi.product_name = p.name, oi.product_sku = p.sku, oi.product_type = 'RETAIL';

UPDATE inventories i
INNER JOIN products p ON i.product_id = p.id
SET i.product_name = p.name, i.product_sku = p.sku, i.product_type = 'RETAIL';
```

### Why These Changes?
1. **Historical Integrity:** OrderItems now store product snapshots, so even if a product is deleted/renamed, orders remain intact
2. **Flexibility:** Support for both retail products and menu items in the same order
3. **Performance:** No need for complex joins when displaying order history
4. **Type Safety:** `productType` enum ensures we query the correct table

## Query Patterns After Migration

### ✅ Correct Pattern - Retail Products
```java
@Query("SELECT oi FROM OrderItem oi " +
       "JOIN RetailProduct rp ON rp.id = oi.productId " +
       "WHERE oi.productType = 'RETAIL'")
```

### ✅ Correct Pattern - Menu Items
```java
@Query("SELECT oi FROM OrderItem oi " +
       "JOIN MenuItem mi ON mi.id = oi.productId " +
       "WHERE oi.productType = 'MENU_ITEM'")
```

### ✅ Correct Pattern - Both Types
```java
@Query("SELECT oi FROM OrderItem oi " +
       "LEFT JOIN RetailProduct rp ON rp.id = oi.productId AND oi.productType = 'RETAIL' " +
       "LEFT JOIN MenuItem mi ON mi.id = oi.productId AND oi.productType = 'MENU_ITEM'")
```

### ✅ Correct Pattern - Using Snapshots
```java
@Query("SELECT oi.productName, SUM(oi.quantity) " +
       "FROM OrderItem oi " +
       "GROUP BY oi.productName")
// No joins needed!
```

### ❌ Incorrect Pattern (Will Fail)
```java
@Query("SELECT oi FROM OrderItem oi " +
       "JOIN oi.product p")  // ❌ product relationship no longer exists
```

## Testing Checklist

After these fixes, test:
- [ ] Order creation with retail products
- [ ] Order creation with menu items
- [ ] Order creation with mixed product types
- [ ] Sales analytics queries
- [ ] Top products reports
- [ ] Category-wise sales reports
- [ ] Inventory queries
- [ ] Popular menu items query

## Additional Notes

### Backward Compatibility
- The `Inventory` entity still has a read-only `product` relationship for backward compatibility
- This allows existing code that reads inventory to continue working
- New code should use `productId` + `productType`

### Future Enhancements
Consider creating repository methods that handle the polymorphic logic:
```java
public interface OrderItemRepository {
    default IProduct getProduct(OrderItem orderItem) {
        if (orderItem.getProductType() == ProductType.RETAIL) {
            return retailProductRepository.findById(orderItem.getProductId()).orElse(null);
        } else {
            return menuItemRepository.findById(orderItem.getProductId()).orElse(null);
        }
    }
}
```

## Summary
All queries that referenced `orderItem.product` have been updated to use:
1. Direct snapshot fields (`productId`, `productName`, `productSku`)
2. Explicit joins with `productType` filters
3. CASE statements for polymorphic queries

✅ **All query errors are now fixed!**
