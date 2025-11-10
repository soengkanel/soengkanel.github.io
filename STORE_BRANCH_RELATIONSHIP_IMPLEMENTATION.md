# Store-Branch One-to-Many Relationship Implementation

## Date: 2025-10-15

## Overview

Implemented a complete **One-to-Many (1:N)** relationship between Store and Branch entities, where:
- **One Store** can have **Many Branches**
- **One Branch** belongs to **One Store**
- All branches **automatically inherit** the parent store's `businessType`

---

## Backend Changes

### 1. Store Model (`Store.java`)

#### Added:
```java
@OneToMany(mappedBy = "store", cascade = CascadeType.ALL, orphanRemoval = true)
@JsonManagedReference
@Builder.Default
private List<Branch> branches = new ArrayList<>();

// Helper methods
public void addBranch(Branch branch) {
    if (branches == null) {
        branches = new ArrayList<>();
    }
    branches.add(branch);
    branch.setStore(this);
    branch.setBusinessType(this.businessType); // Auto-inherit
}

public void removeBranch(Branch branch) {
    if (branches != null) {
        branches.remove(branch);
        branch.setStore(null);
    }
}
```

#### Key Features:
- `cascade = CascadeType.ALL` - When store is deleted, all branches are deleted
- `orphanRemoval = true` - Orphaned branches are automatically removed
- `@JsonManagedReference` - Prevents circular JSON serialization

### 2. Branch Model (`Branch.java`)

#### Added:
```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "store_id", nullable = false)
@JsonBackReference
private Store store;

@Enumerated(EnumType.STRING)
@Column(name = "business_type", nullable = false)
private BusinessType businessType;

@PrePersist
protected void onCreate() {
    createdAt = updatedAt = LocalDateTime.now();

    // Auto-inherit businessType from store if not set
    if (businessType == null && store != null) {
        businessType = store.getBusinessType();
    }
}

@PrePersist
@PreUpdate
private void validateBusinessType() {
    if (store != null && businessType != null && !store.getBusinessType().equals(businessType)) {
        throw new IllegalStateException(
            "Branch businessType must match Store businessType"
        );
    }
}
```

#### Key Features:
- `fetch = FetchType.LAZY` - Performance optimization (loads store only when needed)
- `@JsonBackReference` - Prevents circular JSON serialization
- Auto-inherits `businessType` from store on creation
- Validation ensures `businessType` always matches store

### 3. BranchService (`BranchServiceImpl.java`)

#### Updated `createBranch()`:
```java
@Override
public BranchDTO createBranch(BranchDTO branchDto, User user) {
    Store store = storeRepository.findByStoreAdminId(user.getId());

    Branch branch = BranchMapper.toEntity(branchDto, store);

    // CRITICAL: Auto-set businessType from store
    if (store != null) {
        branch.setBusinessType(store.getBusinessType());
    }

    return BranchMapper.toDto(branchRepository.save(branch));
}
```

### 4. BranchMapper (`BranchMapper.java`)

#### Updated:
```java
public static BranchDTO toDto(Branch branch) {
    return BranchDTO.builder()
            // ... other fields ...
            .businessType(branch.getBusinessType()) // ✅ Include businessType
            .managerId(branch.getManager() != null ? branch.getManager().getId() : null)
            .build();
}

public static Branch toEntity(BranchDTO dto, Store store) {
    return Branch.builder()
            // ... other fields ...
            .businessType(store != null ? store.getBusinessType() : null)
            .build();
}
```

### 5. StoreMapper (`StoreMapper.java`)

#### Updated:
```java
public static StoreDTO toDto(Store store) {
    if (store == null) {
        return null;
    }

    return StoreDTO.builder()
            // ... other fields ...
            .totalBranches(store.getBranches() != null ? store.getBranches().size() : 0)
            .build();
}
```

### 6. DTOs Updated

#### BranchDTO.java:
```java
private BusinessType businessType; // ✅ Added
private Long managerId; // ✅ Added
```

#### StoreDTO.java:
```java
private Integer totalBranches; // ✅ Added
```

---

## Database Migration

### File: `database_migration_add_business_type_to_branches.sql`

#### Steps:
1. Add `business_type` column (allow NULL initially)
2. Update existing branches to inherit from parent store
3. Set default `RETAIL` for any branches without a store
4. Make column NOT NULL
5. Add index for query performance
6. Verification queries included

#### Run:
```sql
-- Execute the SQL script in your database
-- File: pos-backend/database_migration_add_business_type_to_branches.sql
```

---

## Frontend Changes

### 1. New Component: `BranchesSection.jsx`

Located: `pos-frontend-vite/src/pages/store/storeInformation/components/BranchesSection.jsx`

#### Features:
- Displays total branch count
- Shows store's business type
- Explains one-to-many relationship
- Quick actions to view/add branches
- Beautiful card-based UI with statistics

#### Key UI Elements:
- **Statistics Cards**: Total branches, business type, inheritance info
- **Information Box**: Explains relationship in plain language
- **Quick Actions**: Buttons to manage branches
- **Visual Indicators**: Icons and badges for business types

### 2. Updated Store Information Page

Added the `BranchesSection` component to `Stores.jsx`:

```jsx
<div className="grid gap-6">
  <StoreInfoCard storeData={storeData} onEditClick={handleEditClick} />
  <BranchesSection storeData={storeData} />
</div>
```

### 3. Updated Store Form

Changed "Store Type" to "Business Type" in:
- `EditStoreForm.jsx`
- `BasicInformation.jsx`
- `validation.js`
- `formUtils.js`

#### Business Type Options:
- **FNB**: Food & Beverage (Restaurant, Cafe, Bar)
- **RETAIL**: Retail (Shop, Store, Boutique)
- **HYBRID**: Hybrid (F&B + Retail)

### 4. Updated Branch Components

#### BranchForm.jsx:
```javascript
const storeBusinessType = store?.businessType || "RETAIL";

const branchData = {
  ...values,
  storeId: store.id,
  businessType: storeBusinessType, // Automatically set from store
};
```

#### BranchTable.jsx:
```javascript
const storeBusinessType = store?.businessType || "RETAIL";

const getBusinessTypeBadge = (businessType) => {
  // If businessType is missing, fallback to store's business type
  return typeConfig[businessType] || typeConfig[storeBusinessType] || typeConfig.RETAIL;
};
```

---

## How It Works

### Creating a Branch:

1. **User** fills out branch form (name, address, phone, manager)
2. **Frontend** sends request without `businessType` field
3. **Backend Service** looks up the parent store
4. **Backend Service** auto-sets `businessType` from store
5. **Backend Model** validates businessType matches store (in `@PrePersist`)
6. **Database** saves branch with inherited businessType
7. **Response** includes the branch with correct businessType
8. **Frontend** displays branch with proper badge (F&B, Retail, or Hybrid)

### Business Rule Enforcement:

- ✅ Branch `businessType` is **automatically set** from store
- ✅ Branch `businessType` is **NOT user-editable**
- ✅ Validation ensures branch and store types **always match**
- ✅ Frontend shows businessType as **read-only information**

---

## UI Screenshots (Conceptual)

### Store Information Page:
```
┌─────────────────────────────────────────────────────┐
│ Store Information                       [Edit Details]│
├─────────────────────────────────────────────────────┤
│ Store Name: Khmer Delight Restaurant                 │
│ Business Type: [Food & Beverage]                     │
│ Description: A modern Cambodian restaurant...        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Branches                          [View All Branches]│
├─────────────────────────────────────────────────────┤
│  ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│  │  [Icon]   │ │  [Icon]   │ │  [Icon]   │         │
│  │     5     │ │   F&B     │ │  Inherit  │         │
│  │  Branches │ │Business Type│ │  from     │         │
│  └───────────┘ └───────────┘ └───────────┘         │
│                                                       │
│  ┌─────────────────────────────────────────────────┐│
│  │ One Store, Many Branches                         ││
│  │ This store has 5 branches. All branches          ││
│  │ automatically inherit the Food & Beverage        ││
│  │ business type from the parent store.             ││
│  │ [Manage branches →]                              ││
│  └─────────────────────────────────────────────────┘│
│                                                       │
│  [View All Branches] [+ Add New Branch]              │
└─────────────────────────────────────────────────────┘
```

### Branch Management Page:
```
┌─────────────────────────────────────────────────────┐
│ Branch Management                      [+ Add Branch]│
│ 5 of 5 branches                                      │
├─────────────────────────────────────────────────────┤
│ Branch               Location      Business   Status │
│ ────────────────────────────────────────────────────│
│ Phnom Penh Central   Street 51    [F&B]    [Active] │
│ Riverside Cafe       Sisowath Quay [F&B]   [Active] │
│ Airport Branch       Terminal 1    [F&B]    [Active] │
└─────────────────────────────────────────────────────┘
```

---

## Testing Checklist

### Backend:
- [ ] Run database migration script
- [ ] Restart backend application
- [ ] Verify `business_type` column exists in `branches` table
- [ ] Verify existing branches have correct businessType
- [ ] Test creating new branch (should auto-set businessType)
- [ ] Test that validation prevents businessType mismatch

### Frontend:
- [ ] Visit Store Information page
- [ ] Verify new "Branches" section appears
- [ ] Verify branch count is correct
- [ ] Click "View All Branches" - should navigate to branch list
- [ ] Create new branch - should show inherited businessType
- [ ] Verify branch list shows correct businessType badges

### Integration:
- [ ] Create FNB store → Create branch → Verify branch has FNB type
- [ ] Create RETAIL store → Create branch → Verify branch has RETAIL type
- [ ] Create HYBRID store → Create branch → Verify branch has HYBRID type
- [ ] Edit store businessType (if allowed) → Verify existing branches keep their type

---

## Files Modified

### Backend:
1. `pos-backend/src/main/java/com/ng/modal/Store.java`
2. `pos-backend/src/main/java/com/ng/modal/Branch.java`
3. `pos-backend/src/main/java/com/ng/service/impl/BranchServiceImpl.java`
4. `pos-backend/src/main/java/com/ng/mapper/BranchMapper.java`
5. `pos-backend/src/main/java/com/ng/mapper/StoreMapper.java`
6. `pos-backend/src/main/java/com/ng/payload/dto/BranchDTO.java`
7. `pos-backend/src/main/java/com/ng/payload/dto/StoreDTO.java`

### Frontend:
1. `pos-frontend-vite/src/pages/store/storeInformation/components/BranchesSection.jsx` (NEW)
2. `pos-frontend-vite/src/pages/store/storeInformation/components/index.js`
3. `pos-frontend-vite/src/pages/store/storeInformation/Stores.jsx`
4. `pos-frontend-vite/src/pages/store/storeInformation/components/EditStoreForm.jsx`
5. `pos-frontend-vite/src/pages/store/storeInformation/components/BasicInformation.jsx`
6. `pos-frontend-vite/src/pages/store/storeInformation/components/validation.js`
7. `pos-frontend-vite/src/pages/store/storeInformation/components/formUtils.js`
8. `pos-frontend-vite/src/pages/store/Branch/BranchForm.jsx`
9. `pos-frontend-vite/src/pages/store/Branch/BranchTable.jsx`

### Database:
1. `pos-backend/database_migration_add_business_type_to_branches.sql` (NEW)

---

## Summary

✅ **Backend**: Complete one-to-many relationship with automatic businessType inheritance
✅ **Frontend**: Beautiful UI showing store-branch relationship
✅ **Database**: Migration script ready to execute
✅ **Validation**: Business rules enforced at model level
✅ **Documentation**: Comprehensive guide for implementation

The system now properly models the relationship where one store has many branches, and all branches automatically inherit the parent store's business type!
