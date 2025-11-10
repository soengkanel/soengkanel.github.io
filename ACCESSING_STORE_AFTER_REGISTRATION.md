# Accessing Your Store After Registration - Complete Guide

## Registration Flow

After completing the onboarding process, here's what happens:

### **Step-by-Step Flow:**

```
1. Owner Details Form (Step 1)
   ├── Create account (signup)
   ├── Save JWT to localStorage
   └── Move to Step 2

2. Store Details Form (Step 2)
   ├── Submit store info (name, type, businessType, address)
   ├── Backend creates store
   ├── If FNB/HYBRID: Initialize sample data
   └── Frontend navigates to: /store

3. App.jsx Route Logic
   ├── Check: User role = ROLE_STORE_ADMIN?
   ├── Check: Store exists?
   ├── If YES: Load StoreRoutes (/store/*)
   └── If NO: Redirect to /auth/onboarding

4. StoreRoutes
   ├── Load StoreDashboard layout
   └── Show Dashboard (index route)
```

---

## How to Access Your Store

### **Method 1: Direct URL (After Registration)**

After completing onboarding, the system automatically navigates you to:

```
http://localhost:5173/store
```

This is the **Store Dashboard** where you can:
- View store overview
- Manage products/menu items
- View tables (for F&B stores)
- Manage categories
- Add branches
- View sales reports

---

### **Method 2: Login (If You Logged Out)**

If you logged out or closed the browser:

1. **Go to:** `http://localhost:5173/login`
2. **Enter credentials:**
   - Email: (your registered email)
   - Password: (your password)
3. **Auto-redirect to:** `/store` dashboard

The app checks your role (`ROLE_STORE_ADMIN`) and automatically routes you to the store dashboard.

---

## Dashboard Navigation

Once you're in the store dashboard (`/store`), you have access to:

### **Main Menu Items:**

| Route | Page | Description |
|-------|------|-------------|
| `/store` or `/store/dashboard` | Dashboard | Overview of sales, analytics |
| `/store/products` | Products | Manage retail products or menu items |
| `/store/categories` | Categories | Manage product/menu categories |
| `/store/branches` | Branches | Manage store branches |
| `/store/employees` | Employees | Manage staff members |
| `/store/sales` | Sales | View sales history |
| `/store/reports` | Reports | Generate reports |
| `/store/stores` | Store Info | Update store details |
| `/store/settings` | Settings | Store settings |
| `/store/alerts` | Alerts | System notifications |
| `/store/upgrade` | Upgrade | Subscription plans |

---

## Viewing F&B Sample Data

If you registered as **FNB** or **HYBRID** business type, you should see:

### **1. Menu Items (16 items)**

**Navigation:** Go to `/store/products`

You'll see sample menu items organized by category:
- **Appetizers:** Spring Rolls, Garlic Bread, Chicken Wings
- **Main Course:** Grilled Chicken, Beef Burger, Pasta Carbonara, Fish & Chips
- **Desserts:** Chocolate Cake, Ice Cream Sundae, Cheesecake
- **Beverages:** Orange Juice, Coca Cola, Mineral Water
- **Coffee & Tea:** Cappuccino, Espresso, Green Tea

Each item shows:
- Name & SKU
- Price
- Category
- Preparation time
- Kitchen station
- Availability status

---

### **2. Categories (6 categories)**

**Navigation:** Go to `/store/categories`

You'll see:
1. Appetizers
2. Main Course
3. Desserts
4. Beverages
5. Coffee & Tea
6. Salads

---

### **3. Tables (10 tables)**

**Navigation:** This depends on your implementation. Typically:
- `/store/tables` (if route exists)
- Or through Branch management: `/store/branches` → Select branch → View tables

You'll see 10 tables:
- **T1-T5:** Indoor (various capacities)
- **T6-T7:** Outdoor
- **T8-T9:** VIP Section
- **T10:** Bar Area

Each table shows:
- Table number
- Capacity (seats)
- Status (AVAILABLE/OCCUPIED)
- Location

---

### **4. Default Branch**

**Navigation:** Go to `/store/branches`

You'll see:
- **"Main Branch"** (auto-created)
- Address from your store details
- Active status

---

## Troubleshooting

### **Problem 1: Redirected back to onboarding after registration**

**Cause:** Store data not properly fetched from backend

**Solution:**
1. Check browser console for errors
2. Verify JWT is in localStorage:
   - Open DevTools → Application → Local Storage
   - Look for key: `jwt`
3. Check Network tab for API calls:
   - Look for `/api/stores/admin` call
   - Should return your store data

**Fix:**
```javascript
// The app fetches store data in App.jsx:
useEffect(() => {
  if (userProfile && userProfile.role === "ROLE_STORE_ADMIN") {
    dispatch(getStoreByAdmin(userProfile.jwt));
  }
}, [dispatch, userProfile]);
```

If store data isn't loading, refresh the page:
```
Press F5 or Ctrl+R
```

---

### **Problem 2: Can't see menu items/tables**

**Cause:** Sample data initialization didn't run

**Check:**
1. Verify your businessType is FNB or HYBRID (not RETAIL)
2. Check backend logs for:
   ```
   INFO: Initializing F&B sample data for store: {storeName}
   INFO: Created 6 categories
   INFO: Created 16 sample menu items
   INFO: Created 10 sample tables
   ```

**Solution:**
- If logs show errors, check database permissions
- Ensure all tables exist (categories, menu_items, table_layouts)
- Try deleting and recreating the store

---

### **Problem 3: Products page is empty**

**Possible Reasons:**

1. **Wrong Route/Component:**
   - F&B menu items might be on a different page
   - Check if there's a "Menu Items" vs "Products" distinction

2. **Filter Applied:**
   - Check if there's a filter set (e.g., showing only retail products)
   - Look for a businessType filter on the products page

3. **Database Not Migrated:**
   - Ensure `menu_items` table exists
   - Run database migrations

**Quick Fix:**
```sql
-- Check if menu items exist
SELECT * FROM menu_items;

-- Check if categories exist
SELECT * FROM categories;

-- Check if tables exist
SELECT * FROM table_layouts;
```

---

### **Problem 4: 404 Page Not Found**

**Cause:** Route doesn't exist yet

**Check:**
- Is the route defined in `StoreRoutes.jsx`?
- Current routes available:
  - ✅ /store/dashboard
  - ✅ /store/products
  - ✅ /store/categories
  - ✅ /store/branches
  - ✅ /store/employees
  - ✅ /store/sales
  - ✅ /store/reports
  - ✅ /store/settings
  - ❓ /store/tables (may not exist yet)
  - ❓ /store/menu-items (may not exist yet)

**Solution:**
- If tables/menu routes don't exist, they might be:
  - Integrated into products page
  - Under branches page
  - In a separate F&B section

---

## Testing Your Access

### **Test Checklist:**

1. **Login Test:**
   - [ ] Can login with registered credentials
   - [ ] JWT saved in localStorage
   - [ ] Redirected to `/store`

2. **Dashboard Test:**
   - [ ] Dashboard loads without errors
   - [ ] Store name displays correctly
   - [ ] Navigation menu visible

3. **F&B Data Test (FNB/HYBRID only):**
   - [ ] Categories page shows 6 categories
   - [ ] Products/Menu page shows 16 items
   - [ ] Branches page shows "Main Branch"
   - [ ] Tables visible (check branches or separate page)

4. **Navigation Test:**
   - [ ] Can navigate to all menu items
   - [ ] No 404 errors on main routes
   - [ ] Sidebar/navigation works correctly

---

## API Endpoints Reference

Your store dashboard uses these endpoints:

### **Store Management:**
```
GET  /api/stores/admin          - Get store by admin
GET  /api/stores/{id}            - Get store by ID
PUT  /api/stores/{id}            - Update store
```

### **Categories:**
```
GET  /api/category/{storeId}     - Get all categories
POST /api/category               - Create category
```

### **Menu Items (F&B):**
```
GET  /api/menu-items/store/{storeId}  - Get all menu items
POST /api/menu-items                   - Create menu item
```

### **Tables (F&B):**
```
GET  /api/tables/branch/{branchId}    - Get tables by branch
POST /api/tables                       - Create table
```

### **Branches:**
```
GET  /api/branches/store/{storeId}    - Get branches
POST /api/branches                     - Create branch
```

---

## Quick Access Guide

### **After Registration:**

1. **You're automatically logged in** - JWT saved
2. **Redirected to** `/store` - Store dashboard
3. **Default view** - Dashboard overview

### **After Logout:**

1. **Go to** `http://localhost:5173/login`
2. **Login** with your credentials
3. **Auto-redirect** to `/store`

### **Direct Access:**

Just bookmark: `http://localhost:5173/store`

---

## Common URLs

```
Home/Landing:          http://localhost:5173/
Login:                 http://localhost:5173/login
Onboarding:           http://localhost:5173/auth/onboarding
Store Dashboard:       http://localhost:5173/store
Products/Menu:         http://localhost:5173/store/products
Categories:            http://localhost:5173/store/categories
Branches:              http://localhost:5173/store/branches
```

---

## Next Steps After Accessing Store

Once you're in the store dashboard:

1. **Review Sample Data (F&B):**
   - Browse through menu items
   - Check table layouts
   - Review categories

2. **Customize Your Store:**
   - Update store information
   - Add/edit categories
   - Create your own menu items
   - Configure tables

3. **Add Staff:**
   - Go to Employees
   - Add cashiers, managers

4. **Set Up Branches:**
   - Create additional branches
   - Assign staff to branches

5. **Start Using POS:**
   - Create orders
   - Process payments
   - Track sales

---

## Summary

**To access your store after registration:**

✅ **Automatic:** You're redirected to `/store` after onboarding
✅ **Manual:** Login at `/login` → Auto-redirect to `/store`
✅ **Direct:** Navigate to `http://localhost:5173/store` (if logged in)

**Sample data is visible at:**
- `/store/categories` - 6 categories
- `/store/products` - 16 menu items (check if products page shows menu items)
- `/store/branches` - Main Branch with 10 tables

If you're not seeing sample data, check:
1. Your businessType is FNB or HYBRID
2. Backend logs show successful initialization
3. Database has the records

🎉 Your store is ready to use!
