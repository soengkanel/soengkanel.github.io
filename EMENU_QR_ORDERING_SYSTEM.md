# eMenu QR Code Ordering System Documentation

## Overview

The eMenu system allows restaurant customers to scan a QR code at their table, view the menu on their mobile device, and place orders directly without needing a waiter to take the order. This contactless ordering solution improves efficiency and customer experience.

## Features

### Customer Features
- **QR Code Scanning**: Scan table QR code to access menu
- **Browse Menu**: View all available menu items with descriptions, prices, and dietary information
- **Add to Cart**: Select items and quantities
- **Place Orders**: Submit orders directly to the kitchen
- **View Orders**: See order history for the current session
- **Contactless**: No app download required, works in browser

### Staff Features
- **QR Code Generation**: Create unique QR codes for each table
- **QR Code Printing**: Print formatted QR codes with table information
- **Token Regeneration**: Regenerate QR codes for security
- **Order Management**: Receive and process customer orders

## Architecture

### Backend Components

#### 1. QR Code Generator (`QRCodeGenerator.java`)
**Location**: `pos-backend/src/main/java/com/ng/util/QRCodeGenerator.java`

**Purpose**: Generates QR codes using ZXing library

**Key Methods**:
- `generateQRCodeBytes()`: Creates QR code image as byte array
- `generateMenuUrl()`: Creates eMenu URL with table parameters
- `generateTableToken()`: Creates secure token for table access

#### 2. eMenu Service (`EMenuService.java` & Implementation)
**Location**: `pos-backend/src/main/java/com/ng/service/`

**Key Methods**:
- `getMenuForBranch()`: Retrieves menu items for a branch
- `validateTableToken()`: Validates QR code token
- `placeEMenuOrder()`: Processes customer order
- `generateTableQRCode()`: Generates QR code for table
- `getTableInfo()`: Returns table and branch information

#### 3. eMenu Controller (`EMenuController.java`)
**Location**: `pos-backend/src/main/java/com/ng/controller/EMenuController.java`

**Endpoints**:
```
GET  /api/emenu/menu/{branchId}                    - Get menu items
GET  /api/emenu/menu/{branchId}/category/{id}      - Get menu by category
GET  /api/emenu/table                               - Get table info (validate token)
POST /api/emenu/order                               - Place order
GET  /api/emenu/orders/table/{tableId}              - Get table orders
GET  /api/emenu/qr-code/table/{tableId}             - Generate QR code (staff)
POST /api/emenu/qr-code/table/{tableId}/regenerate - Regenerate token (staff)
```

### Frontend Components

#### 1. eMenu Page (Customer-Facing)
**Location**: `pos-frontend-vite/src/pages/emenu/EMenuPage.jsx`

**Features**:
- Responsive mobile-first design
- Menu item display with images and descriptions
- Shopping cart functionality
- Order placement
- Success confirmation

**URL Format**:
```
http://yourdomain.com/emenu?branch=1&table=5&token=ABC123...
```

#### 2. QR Code Management (Staff)
**Location**: `pos-frontend-vite/src/pages/Branch Manager/Tables/QRCodeManagement.jsx`

**Features**:
- Table selection
- QR code generation
- Download QR code as PNG
- Print formatted QR code with table info
- Token regeneration for security

#### 3. API Client
**Location**: `pos-frontend-vite/src/utils/emenuApi.js`

Provides JavaScript functions for all eMenu API interactions.

## Database Schema

### Table: `table_layouts`
**New Column Added**:
```sql
qr_code VARCHAR(255) - Secure token for QR code access
```

### Migration
**File**: `V2__Add_EMenu_QR_Code_Support.sql`

Adds QR code support to existing tables and creates necessary indexes.

## Dependencies

### Backend Dependencies (Maven)
```xml
<!-- QR Code Generation -->
<dependency>
    <groupId>com.google.zxing</groupId>
    <artifactId>core</artifactId>
    <version>3.5.3</version>
</dependency>
<dependency>
    <groupId>com.google.zxing</groupId>
    <artifactId>javase</artifactId>
    <version>3.5.3</version>
</dependency>
```

### Frontend Dependencies
- React Router (for URL parameters)
- Lucide React (for icons)
- Axios (for API calls)

## Setup Instructions

### 1. Backend Setup

**a. Update Dependencies**
```bash
cd pos-backend
mvn clean install
```

**b. Configure Base URL**
Add to `application.yml`:
```yaml
app:
  emenu:
    base-url: http://yourdomain.com  # Your production URL
```

**c. Run Database Migration**
```bash
mvn flyway:migrate
# Or simply start the application - Flyway runs automatically
mvn spring-boot:run
```

### 2. Frontend Setup

**a. Add Route**
In your React Router configuration, add:
```jsx
import EMenuPage from './pages/emenu/EMenuPage';

<Route path="/emenu" element={<EMenuPage />} />
```

**b. Add QR Management to Navigation**
Add link in Branch Manager menu:
```jsx
<Link to="/branch/qr-codes">QR Code Management</Link>
```

### 3. Generate QR Codes

1. Login as Branch Manager
2. Navigate to QR Code Management
3. Select each table
4. Download or print QR codes
5. Place QR codes on tables

## Usage Workflow

### For Customers

1. **Scan QR Code**
   - Customer sits at table
   - Scans QR code with phone camera
   - Opens link in browser (no app needed)

2. **Browse Menu**
   - Sees restaurant name and table number
   - Browses menu items with photos and descriptions
   - Views prices and dietary information

3. **Add Items to Cart**
   - Clicks "Add" button on desired items
   - Adjusts quantities in cart
   - Reviews total price

4. **Place Order**
   - Clicks shopping cart button
   - Reviews order
   - Clicks "Place Order"
   - Receives confirmation

5. **Order Processing**
   - Order sent to kitchen system
   - Staff prepares and delivers food
   - Customer can continue browsing/ordering

### For Staff

1. **Initial Setup**
   - Generate QR code for each table
   - Print and laminate QR codes
   - Place on tables

2. **Receiving Orders**
   - Orders appear in kitchen system
   - Process like regular orders
   - Mark as completed when delivered

3. **Security Management**
   - Regenerate QR codes periodically
   - Replace compromised codes immediately
   - Update printed materials

## Security Features

### Token-Based Access
- Each table has unique secure token
- Tokens validated on every request
- Prevents unauthorized access

### Token Regeneration
- Staff can regenerate tokens anytime
- Invalidates old QR codes
- Useful if QR code is compromised

### No Authentication Required
- Customers don't need accounts
- Frictionless ordering experience
- Optional: Capture phone for order tracking

## Customization Options

### 1. Customer Information Collection

Modify `EMenuOrderRequest.java` to require customer details:
```java
@NotNull(message = "Customer name is required")
private String customerName;

@NotNull(message = "Customer phone is required")
private String customerPhone;
```

### 2. Menu Filtering

Add category filtering in `EMenuPage.jsx`:
```jsx
const [selectedCategory, setSelectedCategory] = useState(null);

// Filter menu items by category
const filteredItems = selectedCategory
  ? menuItems.filter(item => item.categoryId === selectedCategory)
  : menuItems;
```

### 3. Order Modifiers

Support add-ons and customizations:
```java
// In EMenuOrderItemRequest
private List<Long> modifierIds;
private String specialInstructions;
```

### 4. Multi-Language Support

Add language parameter to QR code URL:
```
/emenu?branch=1&table=5&token=ABC&lang=es
```

### 5. Custom Branding

Customize colors and styling in `EMenuPage.jsx`:
```jsx
// Use your brand colors
className="bg-brand-primary text-white"
```

## Integration Points

### With Kitchen Display System
Orders from eMenu have `orderType = "DINE_IN"` and include table information.

### With POS System
- Orders sync automatically
- Table status updates
- Payment processing at table or counter

### With Inventory
- Menu items show availability
- Out-of-stock items automatically hidden

## Best Practices

### QR Code Placement
- **Eye Level**: Easy to scan
- **Protected**: Laminated or in stand
- **Visible**: Clear from seating position
- **Clean**: Replace if damaged

### Menu Management
- **Photos**: High-quality images boost orders
- **Descriptions**: Clear, appetizing descriptions
- **Prices**: Always up to date
- **Availability**: Mark items out of stock promptly

### Customer Experience
- **WiFi**: Provide free WiFi for smooth ordering
- **Instructions**: Brief instructions on QR code
- **Support**: Staff available to help if needed
- **Feedback**: Collect feedback via QR code

### Security
- **Regular Regeneration**: Monthly token regeneration
- **Monitor Usage**: Check for unusual patterns
- **HTTPS**: Always use HTTPS in production
- **Rate Limiting**: Implement on order endpoints

## Troubleshooting

### Issue: QR Code Not Scanning

**Solutions**:
- Ensure QR code is clear and not damaged
- Check lighting - avoid glare
- Try different QR code scanner apps
- Verify URL is accessible

### Issue: Invalid Token Error

**Solutions**:
- QR code may have been regenerated
- Print new QR code for table
- Check database for correct token

### Issue: Menu Not Loading

**Solutions**:
- Verify branch ID is correct
- Check menu items are marked as available
- Ensure API endpoint is accessible
- Check browser console for errors

### Issue: Orders Not Appearing

**Solutions**:
- Verify order was submitted successfully
- Check order status in database
- Ensure kitchen display is running
- Check for network issues

## Performance Optimization

### Caching
Implement caching for menu items:
```java
@Cacheable("menu")
public List<MenuItemDTO> getMenuForBranch(Long branchId) {
    // ...
}
```

### Image Optimization
- Use CDN for menu item images
- Compress images (WebP format)
- Lazy load images

### Database Indexing
Ensure indexes exist:
```sql
CREATE INDEX idx_table_qr_code ON table_layouts(qr_code);
CREATE INDEX idx_menu_items_branch ON menu_items(branch_id);
```

## Analytics & Reporting

### Track Metrics
- QR code scans per table
- Conversion rate (scans to orders)
- Popular menu items via eMenu
- Average order value
- Peak ordering times

### Implementation
Add analytics tracking in `EMenuPage.jsx`:
```jsx
// Track page view
useEffect(() => {
  analytics.track('eMenu Viewed', {
    branchId, tableId
  });
}, []);

// Track order placement
const placeOrder = async () => {
  // ... place order
  analytics.track('eMenu Order Placed', {
    orderValue: getCartTotal(),
    items Count: cart.length
  });
};
```

## Future Enhancements

Potential improvements to consider:

1. **Payment Integration**: Allow customers to pay via QR code
2. **Split Bill**: Split payments among multiple customers
3. **Loyalty Program**: Integrate with customer loyalty
4. **Recommendations**: Suggest popular or complementary items
5. **Allergies Filter**: Filter menu by dietary restrictions
6. **Order Tracking**: Show order status (preparing, ready)
7. **Call Waiter**: Button to request service
8. **Reviews**: Collect dish reviews from customers
9. **Multi-Language**: Support multiple languages
10. **Voice Ordering**: Voice-activated ordering for accessibility

## Support & Maintenance

### Regular Tasks
- **Weekly**: Review order analytics
- **Monthly**: Regenerate QR codes
- **Quarterly**: Update menu photos and descriptions
- **Annually**: Review and optimize entire system

### Monitoring
Set up alerts for:
- Failed orders
- High error rates
- Slow API responses
- Invalid token attempts

## Conclusion

The eMenu QR code ordering system provides a modern, contactless ordering experience that benefits both customers and staff. It reduces wait times, minimizes errors, and allows staff to focus on food quality and service rather than order taking.

For questions or support, refer to:
- Backend code documentation
- API endpoint documentation
- Frontend component documentation
- This guide

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Status**: Production Ready
