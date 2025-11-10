# NGPOS Business Rules - Store & Branch Types

## Critical Business Rule

**✅ IMPLEMENTED: Store Business Type → Branch Business Type Alignment**

If a store has a certain business type (Restaurant/F&B), then ALL branches under that store must have the same **`businessType`**.

## Simple Design

### Only One Type Field: `businessType`

Branches have only **ONE** type field:

**`businessType`** (FNB, RETAIL, HYBRID) - **Automatically inherited from store**
- Determines what capabilities the branch has (tables, menu, inventory)
- **NOT user-selectable** - automatically inherited from store
- Cannot be changed independently from store type
- This is the ONLY type classification needed

### Example:
```javascript
// Restaurant Store
{
  storeType: "FNB" // or businessType: "FNB"
}

// All branches automatically get:
{
  Branch 1: {
    businessType: "FNB"  // Auto-set from store
  },
  Branch 2: {
    businessType: "FNB"  // Auto-set from store (MUST be same)
  }
}
```

## Store Types

### 1. **Food & Beverage (F&B) Store**
- **Business Model**: Restaurant, Cafe, Fast Food
- **All Branches**: Must be F&B branches
- **Required Features**:
  - ✅ Tables (branch-specific)
  - ✅ Menu Categories (branch-specific availability)
  - ✅ Menu Items (branch-specific pricing & availability)
  - ✅ Kitchen/Bar stations
  - ✅ Table reservations
  - ✅ Digital menu (QR codes per table)

### 2. **Retail Store**
- **Business Model**: Retail shop, Supermarket, Fashion store
- **All Branches**: Must be retail branches
- **Required Features**:
  - ✅ Products/Inventory (branch-specific stock)
  - ✅ Product categories
  - ❌ No tables
  - ❌ No menu items
  - ✅ Stock management per branch

### 3. **Hybrid Store (Retail + F&B)**
- **Business Model**: Department store with food court, Mall with cafe
- **All Branches**: Must be hybrid branches
- **Required Features**:
  - ✅ Tables (branch-specific)
  - ✅ Menu items (branch-specific)
  - ✅ Products/Inventory (branch-specific)
  - ✅ Both F&B and retail capabilities

## Current Mock Data Structure

### F&B Branches (businessType: "FNB")
| Branch ID | Name | Business Type | Has Tables | Has Menu |
|-----------|------|---------------|------------|----------|
| 3 | Pochentong Airport | FNB | ✅ (2 tables) | ✅ |
| 4 | Riverside Cafe | FNB | ✅ (3 tables) | ✅ |
| 9 | Olympic Stadium Outlet | FNB | ✅ | ✅ |

### Retail Branches (businessType: "RETAIL")
| Branch ID | Name | Business Type | Has Tables | Has Products |
|-----------|------|---------------|------------|--------------|
| 2 | Aeon Mall | RETAIL | ❌ | ✅ |
| 5 | BKK1 Express | RETAIL | ❌ | ✅ |
| 7 | Siem Reap Angkor | RETAIL | ❌ | ✅ |
| 10 | Bassac Lane Heritage | RETAIL | ❌ | ✅ |

### Hybrid Branches (businessType: "HYBRID")
| Branch ID | Name | Business Type | Has Tables | Has Menu | Has Products |
|-----------|------|---------------|------------|----------|--------------|
| 1 | Phnom Penh Central | HYBRID | ✅ (5 tables) | ✅ | ✅ |
| 6 | Royal University | HYBRID | ✅ | ✅ | ✅ |
| 8 | TK Avenue Tech Hub | HYBRID | ✅ | ✅ | ✅ |

## Branch-Specific Menu Implementation

### Menu Categories
```javascript
{
  id: 7,
  name: "Breakfast",
  branchIds: [1, 4] // Only available at Phnom Penh Central & Riverside Cafe
}
```

**Logic**:
- Empty `branchIds` = available at ALL branches
- Specified `branchIds` = only available at those branches

### Menu Items
```javascript
{
  id: 1,
  name: "Classic Bruschetta",
  price: 8.99, // Base price
  branchAvailability: {
    1: { available: true, price: 8.99 },  // Phnom Penh Central
    2: { available: true, price: 9.99 },  // Aeon Mall (premium pricing)
    3: { available: false, price: null }, // Airport (not available)
    4: { available: true, price: 8.99 }   // Riverside
  }
}
```

**Logic**:
- Different branches can have different prices
- Items can be unavailable at specific branches
- Airport might only serve quick items (no appetizers)

## Helper Functions Usage

### Get Branch-Specific Menu

```javascript
import { getMenuItemsByBranch, getCategoriesByBranch } from '@/data/mockFnBData';

// Get menu for Riverside Cafe (Branch ID: 4)
const categories = getCategoriesByBranch(4); // Includes Breakfast
const menuItems = getMenuItemsByBranch(4);   // With branch-specific pricing

// Get menu for Airport (Branch ID: 3)
const categories = getCategoriesByBranch(3); // No Breakfast category
const menuItems = getMenuItemsByBranch(3);   // Quick-service items only
```

### Check Item Availability

```javascript
import { isItemAvailableAtBranch, getItemPriceForBranch } from '@/data/mockFnBData';

// Check if Bruschetta is available at Airport
const available = isItemAvailableAtBranch(1, 3); // Returns: false

// Get Bruschetta price at Aeon Mall
const price = getItemPriceForBranch(1, 2); // Returns: 9.99
```

### Get Branch Statistics

```javascript
import { getBranchMenuStats, getBranchTableStats } from '@/data/mockFnBData';

// Get menu stats for Phnom Penh Central
const menuStats = getBranchMenuStats(1);
// Returns: { totalItems: 28, totalCategories: 7, vegetarianItems: 12, ... }

// Get table stats for Riverside Cafe
const tableStats = getBranchTableStats(4);
// Returns: { total: 3, available: 1, occupied: 1, reserved: 1, cleaning: 0 }
```

## Business Examples

### Example 1: Restaurant Chain (F&B Store)
```
Store: "Khmer Kitchen Restaurant"
Type: F&B
├── Branch 1: Phnom Penh Central (F&B)
│   ├── Tables: 15
│   ├── Menu: Full menu with breakfast
│   └── Inventory: No
├── Branch 2: Siem Reap (F&B)
│   ├── Tables: 10
│   ├── Menu: Full menu without breakfast
│   └── Inventory: No
└── Branch 3: Airport (F&B - Express)
    ├── Tables: 5
    ├── Menu: Quick-service items only
    └── Inventory: No
```

### Example 2: Retail Chain
```
Store: "Cambodia Fashion"
Type: RETAIL
├── Branch 1: Aeon Mall (RETAIL)
│   ├── Tables: No
│   ├── Menu: No
│   └── Inventory: 500 SKUs
└── Branch 2: BKK1 (RETAIL)
    ├── Tables: No
    ├── Menu: No
    └── Inventory: 300 SKUs
```

### Example 3: Hybrid Store
```
Store: "Phnom Penh Department Store"
Type: HYBRID
├── Branch 1: Central (HYBRID)
│   ├── Tables: 20 (Food Court)
│   ├── Menu: Full menu
│   └── Inventory: 1000 SKUs (Retail section)
└── Branch 2: University (HYBRID)
    ├── Tables: 15 (Cafe)
    ├── Menu: Cafe menu only
    └── Inventory: 300 SKUs (Convenience store)
```

## Validation Rules

### When Creating a Branch
1. **Check Store Type**:
   ```javascript
   if (store.type === "FNB") {
     // Branch MUST have: tables, menu access
     // Branch MUST NOT have: inventory
   } else if (store.type === "RETAIL") {
     // Branch MUST have: inventory
     // Branch MUST NOT have: tables, menu
   } else if (store.type === "HYBRID") {
     // Branch CAN have: tables, menu, inventory
   }
   ```

2. **Business Type Consistency**:
   - F&B Store → All branches `businessType: "FNB"`
   - Retail Store → All branches `businessType: "RETAIL"`
   - Hybrid Store → All branches `businessType: "HYBRID"`

### When Adding Menu Items
1. **Check if Store is F&B or HYBRID**:
   ```javascript
   if (store.type === "RETAIL") {
     // ERROR: Cannot add menu items to retail store
   }
   ```

2. **Set Branch Availability**:
   ```javascript
   menuItem.branchAvailability = {
     [branchId]: { available: true, price: basePrice }
   }
   ```

### When Adding Tables
1. **Check if Branch is F&B or HYBRID**:
   ```javascript
   if (branch.businessType === "RETAIL") {
     // ERROR: Cannot add tables to retail branch
   }
   ```

## API Integration Points

### Frontend Should Send
```javascript
// When creating menu item
POST /api/menu-items
{
  name: "Classic Bruschetta",
  price: 8.99,
  categoryId: 1,
  branchAvailability: {
    1: { available: true, price: 8.99 },
    4: { available: true, price: 8.99 }
  }
}

// When creating table
POST /api/tables
{
  tableNumber: "T1",
  capacity: 4,
  branchId: 1  // REQUIRED
}
```

### Backend Should Validate
```javascript
// When adding table to branch
if (branch.businessType === "RETAIL") {
  throw new Error("Cannot add tables to retail branches");
}

// When adding menu item
if (store.type === "RETAIL") {
  throw new Error("Cannot add menu items to retail stores");
}
```

## Migration Checklist

If you need to enforce this in the backend:

- [ ] Add `businessType` validation when creating branches
- [ ] Add store type check when adding menu items
- [ ] Add branch type check when creating tables
- [ ] Update API to accept `branchAvailability` for menu items
- [ ] Update API to require `branchId` for tables
- [ ] Add database indexes on `branchId` for tables
- [ ] Update menu queries to filter by branch
- [ ] Add branch selector in POS/cashier interface

---

*Last Updated: 2025-10-15*
*This document defines the core business logic for NGPOS multi-branch system*
