# NGPOS Data Architecture - Branch Relationships

## Overview
This document explains how data entities (tables, menu items, categories) are related to stores and branches in the NGPOS system.

## Data Hierarchy

```
Store (Organization)
  └── Branches (Physical Locations)
      ├── Tables (Branch-specific)
      ├── Employees (Branch-specific)
      └── Sales (Branch-specific)

  └── Menu Categories (Store-wide, shared across branches)
      └── Menu Items (Store-wide, shared across branches)
```

## Entity Relationships

### 1. **Tables → Branch** (One-to-Many)
**Status**: ✅ **IMPLEMENTED**

Each table belongs to ONE specific branch.

```javascript
{
  id: 1,
  tableNumber: "T1",
  branchId: 1,  // ← Links to branch
  branchName: "Phnom Penh Central Branch",
  capacity: 2,
  status: "AVAILABLE"
}
```

**Helper Functions**:
- `getTablesByBranch(branchId)` - Get all tables for a branch
- `getAvailableTablesByBranch(branchId)` - Get available tables for a branch
- `getBranchTableStats(branchId)` - Get table statistics for a branch

**Use Cases**:
- QR code generation (one QR per table per branch)
- Table management page (filter by branch)
- Seating assignment (within a branch)

### 2. **Menu Categories → Store** (Store-wide)
**Status**: ⚠️ **STORE-WIDE (Shared Across All Branches)**

Currently, menu categories are shared across ALL branches of a store.

```javascript
{
  id: 1,
  name: "Appetizers",
  description: "Start your meal with these delicious starters",
  // NO branchId - applies to all branches
}
```

**Rationale**:
- Chain restaurants typically have standardized menus
- Easier menu management
- Consistent customer experience

**If you need branch-specific categories**:
Add `branchId` or `availableBranches: [1, 2, 3]` to each category.

### 3. **Menu Items → Store** (Store-wide)
**Status**: ⚠️ **STORE-WIDE (Shared Across All Branches)**

Menu items are shared across all branches, but can be toggled available/unavailable per branch.

```javascript
{
  id: 1,
  name: "Classic Bruschetta",
  price: 8.99,
  categoryId: 1,
  isAvailable: true,
  // NO branchId - available at all branches
}
```

**Future Enhancement Option**:
```javascript
{
  id: 1,
  name: "Classic Bruschetta",
  price: 8.99,
  categoryId: 1,
  availableBranches: [1, 2, 4],  // Only available at these branches
  branchPricing: {
    1: 8.99,  // Phnom Penh Central
    2: 9.99,  // Aeon Mall (higher price)
    4: 7.99   // Riverside Cafe (lower price)
  }
}
```

### 4. **Employees → Branch** (One-to-Many)
**Status**: ✅ **IMPLEMENTED** (in mockEmployees.js)

Each employee is assigned to ONE branch (or store-wide if `branchId` is null).

```javascript
{
  id: 6,
  fullName: "Dara Pich",
  role: "ROLE_BRANCH_CASHIER",
  branchId: 1,  // ← Assigned to specific branch
  branchName: "Phnom Penh Central"
}
```

### 5. **Sales → Branch** (One-to-Many)
**Status**: ✅ **IMPLEMENTED** (in mockSales.js)

Each sale is recorded at a specific branch.

```javascript
{
  id: 1,
  orderNumber: "ORD-000001",
  branchId: 1,  // ← Sale happened at this branch
  branchName: "Phnom Penh Central",
  totalAmount: 50000
}
```

## Implementation Status

| Entity | Branch Relationship | Status |
|--------|-------------------|--------|
| Tables | Branch-specific (branchId) | ✅ Done |
| Employees | Branch-specific (branchId) | ✅ Done |
| Sales | Branch-specific (branchId) | ✅ Done |
| Branches | Store-specific (storeId) | ✅ Done |
| Menu Categories | Store-wide (shared) | ⚠️ Store-wide |
| Menu Items | Store-wide (shared) | ⚠️ Store-wide |

## Usage Examples

### Example 1: Get Tables for a Branch
```javascript
import { getTablesByBranch } from '@/data/mockFnBData';

// Get all tables for Phnom Penh Central (Branch ID: 1)
const tables = getTablesByBranch(1);
// Returns: 5 tables (T1, T2, T3, T4, T5)
```

### Example 2: Filter Tables in Component
```javascript
// In your table management component
const { branches } = useSelector((state) => state.branch);
const [selectedBranch, setSelectedBranch] = useState(null);

const filteredTables = useMemo(() => {
  if (!selectedBranch) return tables;
  return tables.filter(table => table.branchId === selectedBranch);
}, [tables, selectedBranch]);
```

### Example 3: Branch Table Statistics
```javascript
import { getBranchTableStats } from '@/data/mockFnBData';

// Get stats for Riverside Cafe (Branch ID: 4)
const stats = getBranchTableStats(4);
// Returns: { total: 3, available: 1, occupied: 1, reserved: 1, cleaning: 0 }
```

## Cambodia Branch Data

Current mock data includes tables for these branches:

| Branch ID | Branch Name | Tables | Location |
|-----------|------------|--------|----------|
| 1 | Phnom Penh Central | 5 | Main Dining, VIP, Outdoor |
| 2 | Aeon Mall | 3 | Food Court |
| 3 | Pochentong Airport | 2 | Terminal 1 |
| 4 | Riverside Cafe | 3 | Riverside View, Indoor |

## Recommendations

### For Food & Beverage (F&B) Stores:
1. ✅ **Tables**: Branch-specific (already implemented)
2. ⚠️ **Menu**: Consider branch-specific pricing or availability
3. ✅ **Orders**: Branch-specific (track where order came from)

### For Retail Stores:
1. ✅ **Inventory**: Branch-specific stock levels
2. ⚠️ **Products**: Store-wide catalog, branch-specific availability
3. ✅ **Sales**: Branch-specific (track performance per location)

### For Hybrid (Retail + F&B):
1. ✅ **Tables**: Branch-specific
2. ✅ **Inventory**: Branch-specific
3. ⚠️ **Menu & Products**: Store-wide catalog
4. ✅ **Sales**: Branch-specific with category breakdown

## Migration Path (If Needed)

If you need to make menu items branch-specific in the future:

1. Add `branchId` or `availableBranches` array to menu items
2. Update components to filter by branch
3. Add branch selection in menu management
4. Update API endpoints to accept branch context

Example migration:
```javascript
// Before (store-wide)
const menuItems = mockMenuItems;

// After (branch-specific)
const menuItems = mockMenuItems.filter(item =>
  item.availableBranches.includes(currentBranchId)
);
```

## Questions to Consider

1. **Should different branches have different menu items?**
   - Example: Airport branch might not serve breakfast
   - Example: Riverside cafe might have special cocktails

2. **Should prices vary by branch?**
   - Example: Airport pricing might be higher
   - Example: Mall location might have promotional pricing

3. **Should categories be branch-specific?**
   - Example: Some branches might not have "Breakfast" category
   - Example: Bar-only branches might only have "Beverages"

## Current Decision: Store-Wide Menu

**Why**: Easier to manage, consistent customer experience, less complexity.

**Trade-off**: Less flexibility per branch, but simpler implementation.

---

*Last Updated: 2025-10-15*
*For questions, consult the development team*
