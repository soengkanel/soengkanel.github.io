# Multi-Branch Architecture Design

## 🎯 Problem Statement

**Current Issue:**
- Different entities use different patterns for branch relationships
- Confusing data structure (arrays vs objects vs single IDs)
- Hard to understand "what belongs where"

**Example Scenario:**
- Branch A (Downtown): 10 tables, sells Pizza, Pasta, Coffee
- Branch B (Airport): 5 tables, sells Coffee, Sandwiches only (quick service)
- Branch C (Mall): 8 tables, sells full menu with premium pricing

---

## 🏗️ Proposed Architecture: TWO Clear Patterns

### **Pattern 1: OWNERSHIP (Belongs To ONE Branch)**

Used for: **Tables**

```javascript
// Table belongs to EXACTLY ONE branch
{
  id: 1,
  tableNumber: "T1",
  branchId: 1,        // ← Single ID (OWNS this table)
  branchName: "Downtown",
  capacity: 4,
  status: "AVAILABLE"
}
```

**Identifier:** `branchId` (singular)
**Meaning:** "This table BELONGS TO this branch"

---

### **Pattern 2: AVAILABILITY (Available At Multiple Branches)**

Used for: **Categories & Menu Items**

#### **Option A: Simple Array (Recommended)**

```javascript
// Category available at multiple branches
{
  id: 1,
  name: "Breakfast",
  branchIds: [1, 4],  // ← Array (AVAILABLE at these branches)
  // Empty array [] = Available at ALL branches
}

// Menu Item with branch-specific pricing
{
  id: 1,
  name: "Grilled Salmon",
  basePrice: 24.99,
  branchPricing: [    // ← Array of objects
    { branchId: 2, price: 27.99, available: true },  // Aeon Mall (premium)
    { branchId: 3, price: null, available: false }   // Airport (disabled)
  ]
  // Branches not in array = use basePrice & available
}
```

**Identifier:** `branchIds` (plural array) or `branchPricing` (array of objects)
**Meaning:** "This item is AVAILABLE at these branches"

---

## 📊 Data Model Comparison

### **Before (Inconsistent):**
```javascript
// Table
{ branchId: 1 }  // ✓ Clear

// Category
{ branchIds: [] }  // ✓ OK but confusing when empty

// MenuItem
{
  branchAvailability: {  // ❌ Complex object
    1: { available: true, price: 8.99 },
    2: { available: true, price: 9.99 }
  }
}
```

### **After (Consistent):**
```javascript
// Table
{ branchId: 1 }  // ✓ OWNS this branch

// Category
{
  branchIds: [1, 4],  // ✓ AVAILABLE at these branches
  // [] = all branches
}

// MenuItem
{
  basePrice: 24.99,
  branchPricing: [  // ✓ AVAILABLE with custom pricing
    { branchId: 2, price: 27.99, available: true },
    { branchId: 3, price: null, available: false }
  ]
  // Not in array = use basePrice
}
```

---

## 🎨 UI/UX Implications

### **For Tables (OWNERSHIP):**
```
┌─────────────────────────────────┐
│ Branch *                        │
│ ┌─────────────────────────────┐ │
│ │ Select branch ▼             │ │ ← Single dropdown (required)
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### **For Categories (AVAILABILITY):**
```
┌─────────────────────────────────┐
│ Branch Availability             │
│ ┌─────────────────────────────┐ │
│ │ ☑ All Branches (Default)    │ │
│ │ ☐ Downtown                  │ │
│ │ ☐ Airport                   │ │ ← Checkboxes (optional)
│ │ ☑ Mall                      │ │
│ └─────────────────────────────┘ │
│ Note: Unchecked = not available │
└─────────────────────────────────┘
```

### **For Menu Items (AVAILABILITY + PRICING):**
```
┌─────────────────────────────────┐
│ Base Price: $24.99              │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Branch-Specific Pricing         │
├─────────────────────────────────┤
│ Downtown      ✓ Available  Base │
│ Airport       ✗ Disabled        │
│ Mall          ✓ Available  $27.99 (+$3.00) │
└─────────────────────────────────┘
```

---

## 🔄 Query Patterns

### **Get Tables for Branch:**
```javascript
// Simple filter
tables.filter(t => t.branchId === selectedBranchId)
```

### **Get Categories for Branch:**
```javascript
// Empty array = all branches, or check if includes
categories.filter(c =>
  c.branchIds.length === 0 ||
  c.branchIds.includes(selectedBranchId)
)
```

### **Get Menu Items for Branch with Pricing:**
```javascript
menuItems
  .filter(item => {
    // Check if available at this branch
    const branchData = item.branchPricing.find(bp => bp.branchId === selectedBranchId);
    return !branchData || branchData.available !== false;
  })
  .map(item => {
    // Apply branch-specific price
    const branchData = item.branchPricing.find(bp => bp.branchId === selectedBranchId);
    return {
      ...item,
      price: branchData?.price || item.basePrice
    };
  })
```

---

## 🎯 Recommendation: Unified Approach

### **Final Data Structure:**

```javascript
// Store
{
  id: 1,
  brand: "My Restaurant",
  businessType: "FNB"
}

// Branch (belongs to Store)
{
  id: 1,
  storeId: 1,
  name: "Downtown",
  tableCount: 10,
  businessType: "FNB" // Inherited from store
}

// Table (OWNS branch)
{
  id: 1,
  branchId: 1,  // ← OWNERSHIP
  tableNumber: "T1"
}

// Category (AVAILABLE at branches)
{
  id: 1,
  storeId: 1,
  name: "Breakfast",
  branchIds: [1, 4]  // ← AVAILABILITY (empty = all)
}

// MenuItem (AVAILABLE at branches with pricing)
{
  id: 1,
  storeId: 1,
  categoryId: 1,
  name: "Pancakes",
  basePrice: 9.99,
  branchPricing: [  // ← AVAILABILITY + PRICING
    { branchId: 2, price: 11.99, available: true },
    { branchId: 3, price: null, available: false }
  ]
}
```

---

## ✅ Benefits of This Approach

1. **Consistent Naming:**
   - `branchId` = ownership (singular)
   - `branchIds` = availability (plural array)
   - `branchPricing` = availability + pricing (array of objects)

2. **Clear Semantics:**
   - Table → "belongs to" → `branchId`
   - Category → "available at" → `branchIds`
   - Menu Item → "available at with price" → `branchPricing`

3. **Easy Queries:**
   - Simple filters and maps
   - Clear boolean logic
   - Efficient lookups

4. **Flexible:**
   - Can easily add/remove branches
   - Pricing changes don't affect structure
   - Empty arrays have clear meaning

5. **Scalable:**
   - Works with 2 branches or 200 branches
   - No performance issues
   - Easy to cache and optimize

---

## 🚀 Implementation Plan

1. Update `mockFnBData.js` to use new structure
2. Create helper functions for branch queries
3. Update all form components to use consistent patterns
4. Add TypeScript interfaces for type safety
5. Update Redux actions/reducers
6. Migrate any existing data

---

## 📝 Naming Convention Summary

| Entity | Pattern | Field Name | Example |
|--------|---------|------------|---------|
| **Table** | Ownership | `branchId` | `{ branchId: 1 }` |
| **Category** | Availability | `branchIds` | `{ branchIds: [1, 4] }` |
| **Menu Item** | Availability + Pricing | `branchPricing` | `{ branchPricing: [{ branchId: 2, price: 27.99 }] }` |

**Rule of Thumb:**
- Singular `branchId` = OWNS (belongs to one)
- Plural `branchIds` = AVAILABLE AT (many)
- Array of objects = AVAILABLE AT + extra data (pricing, etc.)
