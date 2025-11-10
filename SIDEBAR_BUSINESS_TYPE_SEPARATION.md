# Sidebar Menu Separation by Business Type - Implementation Guide

## Overview
The sidebar navigation now dynamically adapts based on the store's `businessType`, showing relevant menu items for **RETAIL**, **FNB** (Food & Beverage), or **HYBRID** businesses.

---

## Features Implemented

### **1. Dynamic Menu Filtering**
- Sidebar automatically shows/hides menu items based on business type
- Uses Redux store data to determine current business type
- Falls back to RETAIL if businessType is not set

### **2. Business Type Badge**
- Visual indicator at the top of sidebar showing store type
- Color-coded badges:
  - **RETAIL** - Blue badge with shopping cart icon
  - **F&B** - Orange badge with utensils icon
  - **HYBRID** - Purple badge with store icon

### **3. Section Separators**
- Clear visual separation between different sections
- Section headers for "Retail" and "Food & Beverage"
- Divider line before bottom menu items

### **4. Smart Icon Selection**
- Context-appropriate icons for each menu type
- Retail icons: ShoppingCart, Tag, Truck
- F&B icons: UtensilsCrossed, Coffee, TableProperties, ChefHat

---

## Sidebar Menu Structure

### **RETAIL Store Sidebar**

```
┌─────────────────────────┐
│ POS Admin               │
│ [RETAIL Store] 🔵       │
├─────────────────────────┤
│ 📊 Dashboard            │
│ 🏪 Stores               │
│ 🏢 Branches             │
│ 👥 Employees            │
│                         │
│ --- RETAIL ---          │
│ 🛒 Products             │
│ 🏷️  Categories          │
│ 🚚 Inventory Alerts     │
│                         │
│ ─────────────────────   │
│ 📈 Sales                │
│ 📄 Reports              │
│ 💵 Upgrade Plan         │
│ ⚙️  Settings            │
├─────────────────────────┤
│ [Logout]                │
└─────────────────────────┘
```

### **F&B Store Sidebar**

```
┌─────────────────────────┐
│ POS Admin               │
│ [F&B Store] 🟠          │
├─────────────────────────┤
│ 📊 Dashboard            │
│ 🏪 Stores               │
│ 🏢 Branches             │
│ 👥 Employees            │
│                         │
│ --- FOOD & BEVERAGE --- │
│ 🍽️  Menu Items          │
│ ☕ Menu Categories      │
│ 🪑 Tables               │
│ 👨‍🍳 Kitchen Orders       │
│                         │
│ ─────────────────────   │
│ 📈 Sales                │
│ 📄 Reports              │
│ 💵 Upgrade Plan         │
│ ⚙️  Settings            │
├─────────────────────────┤
│ [Logout]                │
└─────────────────────────┘
```

### **HYBRID Store Sidebar**

```
┌─────────────────────────┐
│ POS Admin               │
│ [HYBRID Store] 🟣       │
├─────────────────────────┤
│ 📊 Dashboard            │
│ 🏪 Stores               │
│ 🏢 Branches             │
│ 👥 Employees            │
│                         │
│ --- RETAIL ---          │
│ 🛒 Products             │
│ 🏷️  Categories          │
│ 🚚 Inventory Alerts     │
│                         │
│ --- FOOD & BEVERAGE --- │
│ 🍽️  Menu Items          │
│ ☕ Menu Categories      │
│ 🪑 Tables               │
│ 👨‍🍳 Kitchen Orders       │
│                         │
│ ─────────────────────   │
│ 📈 Sales                │
│ 📄 Reports              │
│ 💵 Upgrade Plan         │
│ ⚙️  Settings            │
├─────────────────────────┤
│ [Logout]                │
└─────────────────────────┘
```

---

## Menu Items by Business Type

### **Common Items (All Types)**
These appear for RETAIL, FNB, and HYBRID:

| Item | Icon | Route | Description |
|------|------|-------|-------------|
| Dashboard | 📊 | `/store/dashboard` | Main overview |
| Stores | 🏪 | `/store/stores` | Store information |
| Branches | 🏢 | `/store/branches` | Branch management |
| Employees | 👥 | `/store/employees` | Staff management |
| Sales | 📈 | `/store/sales` | Sales history |
| Reports | 📄 | `/store/reports` | Analytics & reports |
| Upgrade Plan | 💵 | `/store/upgrade` | Subscription plans |
| Settings | ⚙️ | `/store/settings` | Store settings |

---

### **Retail-Specific Items**
These appear for RETAIL and HYBRID only:

| Item | Icon | Route | Description |
|------|------|-------|-------------|
| Products | 🛒 | `/store/products` | Retail product catalog |
| Categories | 🏷️ | `/store/categories` | Product categories |
| Inventory Alerts | 🚚 | `/store/alerts` | Low stock alerts |

---

### **F&B-Specific Items**
These appear for FNB and HYBRID only:

| Item | Icon | Route | Description |
|------|------|-------|-------------|
| Menu Items | 🍽️ | `/store/menu-items` | Food & beverage menu |
| Menu Categories | ☕ | `/store/menu-categories` | Menu item categories |
| Tables | 🪑 | `/store/tables` | Table management |
| Kitchen Orders | 👨‍🍳 | `/store/kitchen-orders` | Kitchen display system |

---

## Technical Implementation

### **File Modified:**
`pos-frontend-vite/src/pages/store/Dashboard/StoreSidebar.jsx`

### **Key Changes:**

#### **1. Added Redux Selector**
```javascript
import { useSelector } from "react-redux";

const { store } = useSelector((state) => state.store);
const businessType = store?.businessType || "RETAIL";
```

#### **2. Menu Item Arrays**
```javascript
// Common items for all
const commonNavLinks = [
  { name: "Dashboard", path: "/store/dashboard", icon: <LayoutDashboard />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"] },
  // ...
];

// Retail-only items
const retailNavLinks = [
  { name: "Products", path: "/store/products", icon: <ShoppingCart />,
    businessTypes: ["RETAIL", "HYBRID"] },
  // ...
];

// F&B-only items
const fnbNavLinks = [
  { name: "Menu Items", path: "/store/menu-items", icon: <UtensilsCrossed />,
    businessTypes: ["FNB", "HYBRID"] },
  // ...
];
```

#### **3. Dynamic Filtering with useMemo**
```javascript
const navLinks = useMemo(() => {
  const filteredLinks = [
    ...commonNavLinks,
    ...retailNavLinks.filter((link) => link.businessTypes.includes(businessType)),
    ...fnbNavLinks.filter((link) => link.businessTypes.includes(businessType)),
    ...bottomNavLinks,
  ];

  return filteredLinks.filter((link) => link.businessTypes.includes(businessType));
}, [businessType]);
```

#### **4. Business Type Badge**
```javascript
const getBusinessTypeBadge = () => {
  const badges = {
    RETAIL: { label: "Retail", color: "bg-blue-500", icon: <ShoppingCart /> },
    FNB: { label: "F&B", color: "bg-orange-500", icon: <UtensilsCrossed /> },
    HYBRID: { label: "Hybrid", color: "bg-purple-500", icon: <Store /> },
  };
  return badges[businessType] || badges.RETAIL;
};
```

#### **5. Section Headers**
```javascript
{/* Retail Section */}
{(businessType === "RETAIL" || businessType === "HYBRID") && (
  <>
    <li className="pt-4 pb-2 px-2">
      <div className="text-xs font-semibold text-sidebar-foreground/50 uppercase">
        <ShoppingCart className="w-3 h-3" />
        Retail
      </div>
    </li>
    {retailNavLinks.map((link) => (/* render link */))}
  </>
)}
```

---

## Icon Reference

### **New Icons Added:**
```javascript
import {
  UtensilsCrossed,  // Food & Beverage main icon
  Coffee,           // Menu categories
  ChefHat,          // Kitchen orders
  TableProperties,  // Tables
} from "lucide-react";
```

### **Icon Usage:**

| Icon | Component | Used For |
|------|-----------|----------|
| `LayoutDashboard` | All | Dashboard |
| `Store` | All | Stores, Branches |
| `Users` | All | Employees |
| `ShoppingCart` | Retail | Products, Badge |
| `Tag` | Retail | Categories |
| `Truck` | Retail | Inventory Alerts |
| `UtensilsCrossed` | F&B | Menu Items, Badge |
| `Coffee` | F&B | Menu Categories |
| `TableProperties` | F&B | Tables |
| `ChefHat` | F&B | Kitchen Orders |
| `BarChart2` | All | Sales |
| `FileText` | All | Reports |
| `BadgeDollarSign` | All | Upgrade Plan |
| `Settings` | All | Settings |

---

## Badge Colors

### **Business Type Color Scheme:**

```css
RETAIL:  bg-blue-500   (#3B82F6)  - Professional, trustworthy
FNB:     bg-orange-500 (#F97316)  - Warm, appetizing
HYBRID:  bg-purple-500 (#A855F7)  - Versatile, premium
```

---

## State Management

### **Redux Store Structure:**

```javascript
store: {
  store: {
    id: 1,
    brand: "My Store",
    businessType: "FNB",  // "RETAIL" | "FNB" | "HYBRID"
    // ... other fields
  },
  loading: false,
  error: null
}
```

### **Accessing Business Type:**

```javascript
const { store } = useSelector((state) => state.store);
const businessType = store?.businessType || "RETAIL";
```

---

## User Experience

### **RETAIL Store Owner Experience:**
1. Sees badge: **"Retail Store"** (Blue)
2. Menu shows:
   - Common items (Dashboard, Stores, Branches, Employees)
   - Retail section (Products, Categories, Inventory Alerts)
   - Bottom items (Sales, Reports, Settings)
3. **Does NOT see:** Menu Items, Tables, Kitchen Orders

### **F&B Store Owner Experience:**
1. Sees badge: **"F&B Store"** (Orange)
2. Menu shows:
   - Common items (Dashboard, Stores, Branches, Employees)
   - F&B section (Menu Items, Menu Categories, Tables, Kitchen Orders)
   - Bottom items (Sales, Reports, Settings)
3. **Does NOT see:** Products, Categories, Inventory Alerts

### **HYBRID Store Owner Experience:**
1. Sees badge: **"Hybrid Store"** (Purple)
2. Menu shows:
   - Common items (Dashboard, Stores, Branches, Employees)
   - **Retail section** (Products, Categories, Inventory Alerts)
   - **F&B section** (Menu Items, Menu Categories, Tables, Kitchen Orders)
   - Bottom items (Sales, Reports, Settings)
3. **Sees everything!** Both retail and F&B features

---

## Navigation Routes

### **Routes to Implement (if not exist):**

The sidebar references these routes that may need to be created:

```javascript
// F&B Routes (NEW)
/store/menu-items        → Menu item management page
/store/menu-categories   → Menu category management page
/store/tables            → Table layout management page
/store/kitchen-orders    → Kitchen display system page
```

Add these to `StoreRoutes.jsx`:

```javascript
import MenuItems from "../pages/store/MenuItems/MenuItems";
import MenuCategories from "../pages/store/MenuCategories/MenuCategories";
import Tables from "../pages/store/Tables/Tables";
import KitchenOrders from "../pages/store/KitchenOrders/KitchenOrders";

<Route path="menu-items" element={<MenuItems />} />
<Route path="menu-categories" element={<MenuCategories />} />
<Route path="tables" element={<Tables />} />
<Route path="kitchen-orders" element={<KitchenOrders />} />
```

---

## Testing Checklist

### **Test RETAIL Store:**
- [ ] Badge shows "Retail Store" (Blue)
- [ ] Shows: Dashboard, Stores, Branches, Employees
- [ ] Shows: Products, Categories, Inventory Alerts (Retail section)
- [ ] Shows: Sales, Reports, Upgrade, Settings
- [ ] Does NOT show: Menu Items, Tables, Kitchen Orders

### **Test F&B Store:**
- [ ] Badge shows "F&B Store" (Orange)
- [ ] Shows: Dashboard, Stores, Branches, Employees
- [ ] Shows: Menu Items, Menu Categories, Tables, Kitchen Orders (F&B section)
- [ ] Shows: Sales, Reports, Upgrade, Settings
- [ ] Does NOT show: Products, Categories, Inventory Alerts

### **Test HYBRID Store:**
- [ ] Badge shows "Hybrid Store" (Purple)
- [ ] Shows: Dashboard, Stores, Branches, Employees
- [ ] Shows: Products, Categories, Inventory Alerts (Retail section)
- [ ] Shows: Menu Items, Menu Categories, Tables, Kitchen Orders (F&B section)
- [ ] Shows: Sales, Reports, Upgrade, Settings
- [ ] Both sections visible with headers

### **Test Switching Business Types:**
- [ ] Update store businessType in database
- [ ] Refresh page
- [ ] Sidebar updates correctly
- [ ] Badge color changes
- [ ] Menu items show/hide correctly

---

## Future Enhancements

### **Potential Improvements:**

1. **Collapsible Sections**
   - Allow users to collapse Retail/F&B sections
   - Remember collapsed state in localStorage

2. **Menu Item Counts**
   - Show number of products/menu items next to menu names
   - e.g., "Products (24)" or "Menu Items (16)"

3. **Quick Actions**
   - Add quick action buttons in sidebar
   - e.g., "New Product", "New Order"

4. **Search in Sidebar**
   - Add search box to quickly find menu items
   - Highlight matching items

5. **Keyboard Shortcuts**
   - Add keyboard shortcuts for quick navigation
   - Display shortcuts on hover

6. **Mobile Responsive**
   - Add hamburger menu for mobile
   - Collapsible sidebar on smaller screens

7. **Favorites**
   - Allow users to "favorite" frequently used pages
   - Show favorites at the top

---

## Summary

✅ **Sidebar now adapts based on businessType**
✅ **Visual badge indicates store type**
✅ **Clear section separators for RETAIL and F&B**
✅ **HYBRID stores see both sections**
✅ **Uses Redux store data automatically**
✅ **Optimized with useMemo for performance**

**Result:** Clean, organized sidebar that shows only relevant menu items for each business type! 🎉
