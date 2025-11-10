# Kitchen Display System (KDS) - Real-Time Order Routing

## Overview

The Kitchen Display System enables real-time order routing to different kitchen stations (Chef, Barista, etc.) with WebSocket-based notifications. Orders are automatically split by menu item type and sent to the appropriate station instantly.

## Architecture

### Real-Time Flow
```
Waiter/Customer Order → Auto-Route by Item Type → Real-Time WebSocket Notification → Kitchen Station Display
```

**Example**:
- Order: Noodles + Coca-Cola
- Noodles → CHEF station (real-time)
- Coca-Cola → BEVERAGE station/Barista (real-time)

## Components Created

### Backend

1. **WebSocketConfig.java** - WebSocket configuration
   - Endpoint: `/ws/kitchen`
   - Topics: `/topic/kitchen/{station}`, `/topic/service`

2. **KitchenDisplayService** - Core business logic
   - `routeOrderToKitchen()` - Auto-splits & routes orders
   - `startPreparation()` - Chef marks as started
   - `markAsReady()` - Chef marks ready for pickup
   - `markAsServed()` - Waiter confirms delivery
   - `createWaiterOrder()` - Service staff creates order

3. **KitchenDisplayController** - REST API
   ```
   GET  /api/kitchen/station/{station}/branch/{id}  - Get orders for station
   GET  /api/kitchen/active/branch/{id}             - All active orders (waiter view)
   GET  /api/kitchen/ready/branch/{id}              - Ready orders (pickup)
   POST /api/kitchen/{id}/start                     - Start preparation
   POST /api/kitchen/{id}/ready                     - Mark ready
   POST /api/kitchen/{id}/served                    - Mark served
   POST /api/kitchen/waiter-order                   - Create order
   ```

4. **DTOs**
   - `KitchenOrderDTO` - Kitchen order data
   - `KitchenOrderItemDTO` - Order item details
   - `WaiterOrderRequest` - Service staff order creation

### Kitchen Stations

Defined in `KitchenStation` enum:
- **HOT_KITCHEN** - Main chef station (noodles, rice, etc.)
- **COLD_KITCHEN** - Salads, cold dishes
- **GRILL** - Grilled items
- **FRY** - Fried items
- **BEVERAGE** - Barista/drinks (Coca-Cola, coffee, etc.)
- **DESSERT** - Desserts station
- **EXPEDITOR** - Quality check/coordination

## How It Works

### 1. Order Placement
```java
// Waiter creates order
WaiterOrderRequest request = {
  branchId: 1,
  tableId: 5,
  items: [
    { menuItemId: 10, quantity: 1 },  // Noodles (HOT_KITCHEN)
    { menuItemId: 25, quantity: 2 }   // Coca-Cola (BEVERAGE)
  ]
};
```

### 2. Automatic Routing
System reads `kitchenStation` from each MenuItem and creates separate kitchen orders:
```
KitchenOrder 1:
  - Station: HOT_KITCHEN (Chef)
  - Items: Noodles x1
  - Status: PENDING
  - WebSocket → /topic/kitchen/hot_kitchen

KitchenOrder 2:
  - Station: BEVERAGE (Barista)
  - Items: Coca-Cola x2
  - Status: PENDING
  - WebSocket → /topic/kitchen/beverage
```

### 3. Real-Time Notifications
```javascript
// Chef's display auto-updates
WebSocket message received on /topic/kitchen/hot_kitchen:
{
  event: "new-order",
  order: {
    id: 123,
    orderNumber: "ORD5678",
    tableNumber: "5",
    items: [{ itemName: "Noodles", quantity: 1 }]
  }
}
```

### 4. Station Workflow

**Chef Display:**
1. New order appears instantly
2. Chef clicks "Start" → Status: PREPARING
3. Chef prepares food
4. Chef clicks "Ready" → Notification to waiters
5. Order moves to "Ready" queue

**Barista Display:**
1. Beverage order appears
2. Barista prepares drink
3. Marks as "Ready"

**Waiter Display:**
1. Sees all orders for their tables
2. Gets notification when items ready
3. Picks up from kitchen
4. Marks as "Served"
5. Order auto-bumps from kitchen display

## Frontend Pages Needed

### 1. Chef Display (`/kitchen/chef`)
```jsx
Features:
- Real-time WebSocket connection
- Grid of pending orders
- Color-coded by priority
- Timer showing elapsed time
- Actions: Start, Ready
- Audio alert for new orders
```

### 2. Barista Display (`/kitchen/barista`)
```jsx
Features:
- Same as chef but filtered to BEVERAGE station
- Simpler interface for drink orders
- Quick actions
```

### 3. Service/Waiter Display (`/service/orders`)
```jsx
Features:
- Table-based view
- Shows all orders by table
- Ready-for-pickup section
- Mark as served
- Call kitchen for special requests
```

### 4. Expeditor Display (`/kitchen/expeditor`)
```jsx
Features:
- Overview of all stations
- Coordinate between stations
- Adjust priorities
- Monitor timing
```

## WebSocket Integration

### Frontend Connection
```javascript
import SockJS from 'sockjs-client';
import { Stomp } from '@stomp/stompjs';

const socket = new SockJS('http://localhost:5000/ws/kitchen');
const stompClient = Stomp.over(socket);

stomp Client.connect({}, () => {
  // Subscribe to chef station
  stompClient.subscribe('/topic/kitchen/hot_kitchen', (message) => {
    const data = JSON.parse(message.body);
    if (data.event === 'new-order') {
      // Add order to display
      // Play notification sound
    }
  });
});
```

## Configuration

### Menu Items Setup
Each menu item must have `kitchenStation` set:
```sql
UPDATE menu_items
SET kitchen_station = 'HOT_KITCHEN'
WHERE name LIKE '%noodle%' OR name LIKE '%rice%';

UPDATE menu_items
SET kitchen_station = 'BEVERAGE'
WHERE name LIKE '%cola%' OR name LIKE '%coffee%';
```

### Application Properties
```yaml
# WebSocket config is auto-configured
# Adjust CORS if needed in WebSocketConfig.java
```

## API Usage Examples

### Create Waiter Order
```bash
POST /api/kitchen/waiter-order
{
  "branchId": 1,
  "tableId": 5,
  "items": [
    {
      "menuItemId": 10,
      "quantity": 1,
      "specialInstructions": "Extra spicy"
    }
  ]
}
```

### Get Chef Orders
```bash
GET /api/kitchen/station/HOT_KITCHEN/branch/1
Response: [
  {
    "id": 123,
    "orderNumber": "ORD5678",
    "tableNumber": "5",
    "status": "PENDING",
    "items": [...]
  }
]
```

### Mark Order Ready
```bash
POST /api/kitchen/123/ready
```

## Key Features

✅ **Real-Time Updates** - WebSocket instant notifications
✅ **Auto-Routing** - Splits orders by station automatically
✅ **Station-Specific** - Each station sees only their orders
✅ **Priority Management** - Urgent orders highlighted
✅ **Time Tracking** - Monitors preparation time
✅ **Service Coordination** - Waiters know when items ready
✅ **Bump System** - Clean displays after serving

## Production Checklist

- [ ] Set up dedicated displays for each station
- [ ] Configure audio alerts
- [ ] Set kitchen stations for all menu items
- [ ] Train staff on workflow
- [ ] Test WebSocket connectivity
- [ ] Set up printer integration (optional)
- [ ] Configure backup procedures

## Future Enhancements

1. **Printer Integration** - Auto-print tickets
2. **Mobile App** - Chef/waiter mobile interface
3. **Analytics Dashboard** - Preparation time analytics
4. **Video Calls** - Kitchen-to-floor communication
5. **Inventory Integration** - Auto-update stock
6. **Recipe Display** - Show recipes on chef display
7. **Multi-Language** - Support multiple languages

---

**Status**: Backend Complete ✅
**Next**: Implement frontend displays
**Version**: 1.0.0
