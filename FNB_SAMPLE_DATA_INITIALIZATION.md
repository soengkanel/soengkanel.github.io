# F&B Sample Data Initialization - Complete Implementation

## Overview
When a store with `businessType` = **FNB** or **HYBRID** is created, the system now automatically initializes sample data including:
- **Categories** (6 categories)
- **Menu Items** (16 items)
- **Tables** (10 tables)
- **Default Branch** (if not exists)

This gives F&B store owners immediate example data to explore the POS system.

---

## Files Created

### 1. **FnbInitializationService.java** ✅
**Path:** `pos-backend/src/main/java/com/ng/service/FnbInitializationService.java`

**Purpose:** Interface for F&B initialization service

```java
public interface FnbInitializationService {
    void initializeFnbSampleData(Store store, Branch branch);
}
```

---

### 2. **FnbInitializationServiceImpl.java** ✅
**Path:** `pos-backend/src/main/java/com/ng/service/impl/FnbInitializationServiceImpl.java`

**Purpose:** Implementation of F&B sample data initialization

**Dependencies:**
- CategoryRepository
- MenuItemRepository
- TableLayoutRepository
- BranchRepository

**Key Methods:**

#### `initializeFnbSampleData(Store store, Branch branch)`
Main entry point that:
1. Creates default branch if none exists
2. Creates 6 sample categories
3. Creates 16 sample menu items
4. Creates 10 sample tables

#### `createDefaultBranch(Store store)`
Creates a "Main Branch" with:
- Name: "Main Branch"
- Address/Phone/Email from store contact info
- Auto-activated

#### `createSampleCategories(Store store)`
Creates 6 categories:
1. **Appetizers**
2. **Main Course**
3. **Desserts**
4. **Beverages**
5. **Coffee & Tea**
6. **Salads**

#### `createSampleMenuItems(Store store, List<Category> categories)`
Creates 16 menu items across categories:

**Appetizers (3 items):**
- Spring Rolls ($8.99) - 10min prep, FRY station
- Garlic Bread ($5.99) - 5min prep, GRILL station
- Chicken Wings ($12.99) - 15min prep, FRY station

**Main Course (4 items):**
- Grilled Chicken ($18.99) - 20min prep, GRILL station
- Beef Burger ($15.99) - 15min prep, GRILL station
- Pasta Carbonara ($14.99) - 18min prep, HOT_STATION
- Fish and Chips ($16.99) - 20min prep, FRY station

**Desserts (3 items):**
- Chocolate Cake ($7.99) - 5min prep, PASTRY station
- Ice Cream Sundae ($6.99) - 3min prep, COLD_STATION
- Cheesecake ($8.99) - 5min prep, PASTRY station

**Beverages (3 items):**
- Fresh Orange Juice ($4.99) - 3min prep
- Coca Cola ($2.99) - 1min prep
- Mineral Water ($1.99) - 1min prep

**Coffee & Tea (3 items):**
- Cappuccino ($4.99) - 5min prep
- Espresso ($3.99) - 3min prep
- Green Tea ($3.49) - 5min prep

**All menu items include:**
- SKU (e.g., MENU-APP-001)
- Description
- Cost price (40% of selling price = 60% margin)
- Preparation time
- Course type
- Kitchen station
- Spice level (NONE by default)
- Vegetarian flag

#### `createSampleTables(Branch branch)`
Creates 10 tables with varied configurations:

| Table | Capacity | Location | Notes |
|-------|----------|----------|-------|
| T1 | 2 | Indoor | Window seat |
| T2 | 4 | Indoor | Window seat |
| T3 | 4 | Indoor | - |
| T4 | 6 | Indoor | - |
| T5 | 2 | Indoor | - |
| T6 | 4 | Outdoor | - |
| T7 | 4 | Outdoor | - |
| T8 | 8 | VIP Section | - |
| T9 | 6 | VIP Section | - |
| T10 | 4 | Bar Area | - |

**All tables:**
- Status: AVAILABLE
- Active: true
- Ready for immediate use

---

## Files Modified

### 3. **StoreServiceImpl.java** ✅
**Path:** `pos-backend/src/main/java/com/ng/service/impl/StoreServiceImpl.java`

**Changes:**

1. **Added imports:**
```java
import com.ng.domain.BusinessType;
import com.ng.service.FnbInitializationService;
```

2. **Added dependency injection:**
```java
private final FnbInitializationService fnbInitializationService;
```

3. **Updated `createStore` method:**
```java
@Override
public StoreDTO createStore(StoreDTO storeDto, User user) {
    System.out.println(storeDto);

    Store store = StoreMapper.toEntity(storeDto, user);
    Store savedStore = storeRepository.save(store);

    // ✅ Initialize F&B sample data if business type is FNB or HYBRID
    if (savedStore.getBusinessType() == BusinessType.FNB ||
        savedStore.getBusinessType() == BusinessType.HYBRID) {

        // Get the main branch if it exists, or pass null to create one
        Branch mainBranch = branchRepository.findByStoreId(savedStore.getId())
                .stream()
                .findFirst()
                .orElse(null);

        fnbInitializationService.initializeFnbSampleData(savedStore, mainBranch);
    }

    return StoreMapper.toDto(savedStore);
}
```

---

## Flow Diagram

```
User completes onboarding
         |
         v
Creates Store with businessType = FNB or HYBRID
         |
         v
StoreServiceImpl.createStore()
         |
         v
Check: businessType == FNB || HYBRID?
         |
    Yes  |  No
         |   └──> Return store (no initialization)
         v
FnbInitializationService.initializeFnbSampleData()
         |
         ├──> Create/Get Main Branch
         |
         ├──> Create 6 Categories
         |         (Appetizers, Main Course, Desserts, etc.)
         |
         ├──> Create 16 Menu Items
         |         (With prices, prep times, kitchen stations)
         |
         └──> Create 10 Tables
                  (Various capacities and locations)
```

---

## Sample Data Summary

### Categories Created: 6
1. Appetizers
2. Main Course
3. Desserts
4. Beverages
5. Coffee & Tea
6. Salads

### Menu Items Created: 16
- **Price Range:** $1.99 - $18.99
- **Prep Time Range:** 1-20 minutes
- **Kitchen Stations:** FRY, GRILL, HOT_STATION, PASTRY, COLD_STATION, BEVERAGE
- **Cost Margin:** 60% (cost price = 40% of selling price)

### Tables Created: 10
- **Total Capacity:** 44 seats
- **Locations:** Indoor (5), Outdoor (2), VIP Section (2), Bar Area (1)
- **Sizes:** 2-8 people per table
- **Status:** All AVAILABLE

### Branch Created: 1
- **Name:** "Main Branch"
- **Status:** Active
- **Inherits store contact information**

---

## Business Logic

### When Sample Data is Created:
✅ **FNB stores** → Full initialization (categories, menu items, tables, branch)
✅ **HYBRID stores** → Full initialization (supports both retail and F&B)
❌ **RETAIL stores** → No F&B initialization

### Branch Handling:
- If branch already exists → Use existing branch for tables
- If no branch exists → Create "Main Branch" automatically
- Tables are always linked to a specific branch

### Data Relationships:
```
Store (FNB/HYBRID)
  ├── Branch (Main Branch)
  │     └── Tables (10 tables)
  │
  ├── Categories (6 categories)
  │     └── Menu Items (16 items)
  │
  └── All linked via store reference
```

---

## Testing Checklist

After deploying this feature:

- [ ] Create new store with businessType = RETAIL
  - Verify: No menu items, categories, or tables created

- [ ] Create new store with businessType = FNB
  - Verify: 6 categories created
  - Verify: 16 menu items created across categories
  - Verify: 10 tables created
  - Verify: "Main Branch" created if none existed
  - Verify: All items are visible in frontend

- [ ] Create new store with businessType = HYBRID
  - Verify: Same as FNB (full initialization)

- [ ] Check menu items
  - Verify: All have correct prices
  - Verify: All have SKUs (e.g., MENU-APP-001)
  - Verify: All have preparation times
  - Verify: All have kitchen stations assigned

- [ ] Check tables
  - Verify: All are AVAILABLE
  - Verify: All are linked to branch
  - Verify: All have correct capacities

---

## Logging

The service includes comprehensive logging:

```
INFO: Initializing F&B sample data for store: {storeName} (Business Type: {type})
INFO: Creating default main branch for store: {storeName}
INFO: Creating sample categories for store: {storeName}
INFO: Created 6 categories
INFO: Creating sample menu items for store: {storeName}
INFO: Created 16 sample menu items
INFO: Creating sample tables for branch: {branchName}
INFO: Created 10 sample tables
INFO: Successfully initialized F&B sample data for store: {storeName}
```

Check application logs to verify initialization is running correctly.

---

## Future Enhancements

Potential improvements for future versions:

1. **Customizable Templates**
   - Allow users to choose cuisine type (Italian, Chinese, etc.)
   - Different menu templates per cuisine

2. **Sample Orders**
   - Create example orders to populate analytics

3. **Sample Customers**
   - Create demo customer profiles

4. **Configurable Initialization**
   - Admin setting to enable/disable sample data
   - Option to clear sample data after testing

5. **Localized Sample Data**
   - Different menu items based on region/language
   - Localized prices

---

## Summary

✅ **Problem Solved:** F&B stores now get immediate sample data
✅ **Files Created:** 2 new service files
✅ **Files Modified:** 1 existing service
✅ **Sample Data:** 6 categories, 16 menu items, 10 tables, 1 branch
✅ **Automatic:** Triggers on store creation for FNB/HYBRID types

Store owners can now immediately explore the F&B features with realistic sample data! 🎉
