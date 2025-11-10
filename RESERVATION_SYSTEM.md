# Restaurant Reservation System Documentation

## Overview
This document provides comprehensive information about the reservation system implemented for F&B/Restaurant business types in the NGPOS system.

## Features

### Core Functionality
- **Create Reservations**: Book tables for customers with specific date, time, and party size
- **Manage Reservations**: View, edit, confirm, cancel, and track reservation status
- **Table Assignment**: Automatically check table availability and assign tables to reservations
- **Customer Management**: Link reservations to existing customers or create new customers during booking
- **Status Tracking**: Track reservation lifecycle from pending to completion
- **Email Notifications**: Automatic confirmation emails and reminders sent to customers
- **Special Requests**: Capture dietary restrictions, accessibility needs, and special occasions

### Reservation Statuses
- **PENDING**: Initial state when reservation is created
- **CONFIRMED**: Reservation confirmed by staff
- **SEATED**: Customer has arrived and been seated at their table
- **COMPLETED**: Reservation completed (customer has left)
- **CANCELLED**: Cancelled by customer or staff
- **NO_SHOW**: Customer did not show up for reservation

## Backend Implementation

### Database Schema

#### Reservation Entity
Location: `pos-backend/src/main/java/com/ng/modal/Reservation.java`

**Key Fields:**
- `id`: Unique identifier
- `customer`: Reference to Customer entity
- `branch`: Reference to Branch entity
- `table`: Reference to TableLayout entity (optional)
- `reservationDate`: Date of reservation
- `reservationTime`: Time of reservation
- `numberOfGuests`: Party size
- `status`: Current reservation status
- `confirmationCode`: Unique code for customer reference
- `specialRequests`: Special requirements or notes
- `durationMinutes`: Expected duration (default: 120 minutes)
- `seatedAt`: Timestamp when customer was seated
- `completedAt`: Timestamp when reservation was completed
- `cancellationReason`: Reason if cancelled
- `reminderSent`: Flag indicating if reminder email was sent

### API Endpoints

**Base URL**: `/api/reservations`

#### Reservation Management
- `POST /api/reservations` - Create new reservation
- `GET /api/reservations/{id}` - Get reservation by ID
- `GET /api/reservations/confirmation/{code}` - Get reservation by confirmation code
- `PUT /api/reservations/{id}` - Update reservation details
- `DELETE /api/reservations/{id}` - Delete reservation (pending/cancelled only)

#### Query Endpoints
- `GET /api/reservations/branch/{branchId}` - Get all reservations for a branch
- `GET /api/reservations/branch/{branchId}/date/{date}` - Get reservations for specific date
- `GET /api/reservations/branch/{branchId}/status/{status}` - Get reservations by status
- `GET /api/reservations/branch/{branchId}/upcoming` - Get upcoming reservations
- `GET /api/reservations/branch/{branchId}/range?startDate={date}&endDate={date}` - Get reservations in date range
- `GET /api/reservations/customer/{customerId}` - Get customer's reservations

#### Status Management
- `PATCH /api/reservations/{id}/status` - Update reservation status
- `POST /api/reservations/{id}/confirm` - Confirm reservation
- `POST /api/reservations/{id}/cancel?reason={text}` - Cancel reservation
- `POST /api/reservations/{id}/seat?tableId={id}` - Mark customer as seated
- `POST /api/reservations/{id}/complete` - Complete reservation
- `POST /api/reservations/{id}/no-show` - Mark as no-show

#### Availability Check
- `GET /api/reservations/availability/table/{tableId}?date={date}&startTime={time}&durationMinutes={minutes}` - Check table availability
- `GET /api/reservations/availability/branch/{branchId}/tables?date={date}&time={time}&guests={number}&duration={minutes}` - Get available tables

### Service Layer

Location: `pos-backend/src/main/java/com/ng/service/impl/ReservationServiceImpl.java`

**Key Methods:**
- `createReservation()`: Creates new reservation with validation
- `updateReservation()`: Updates reservation details with table availability check
- `updateReservationStatus()`: Handles status changes and associated logic (table status updates, notifications)
- `isTableAvailable()`: Checks if table is available for given time slot
- `getAvailableTables()`: Returns list of available tables matching criteria
- `sendReservationReminders()`: Batch process to send reminders for upcoming reservations

### Repository Layer

Location: `pos-backend/src/main/java/com/ng/repository/ReservationRepository.java`

**Custom Queries:**
- `findByConfirmationCode()`: Lookup by confirmation code
- `findUpcomingReservations()`: Get future reservations
- `hasOverlappingReservation()`: Check for time slot conflicts
- `findReservationsNeedingReminders()`: Find reservations needing reminder emails

## Frontend Implementation

### UI Components

Location: `pos-frontend-vite/src/pages/Branch Manager/Reservations/`

#### Main Pages

**1. ReservationsPage (index.jsx)**
- Main container component
- Manages state for create/edit forms
- Integrates list and form components

**2. ReservationList (ReservationList.jsx)**
- Displays reservations in card layout
- Supports filtering by date and status
- Quick actions for status changes (confirm, cancel, seat, complete)
- Shows customer details, time, party size, and special requests
- Color-coded status badges

**3. CreateReservationForm (CreateReservationForm.jsx)**
- Form for creating/editing reservations
- Customer selection or creation
- Date/time picker with validation
- Table availability check and assignment
- Duration selection
- Special requests text area
- Real-time table availability display

### API Integration

Location: `pos-frontend-vite/src/utils/reservationApi.js`

JavaScript API client wrapping all backend endpoints with axios. Provides methods for:
- CRUD operations
- Status management
- Availability checking
- Customer lookup

### Key Features

**Smart Table Assignment:**
- Automatically filters available tables based on:
  - Party size (capacity)
  - Date and time
  - Reservation duration
  - Existing bookings

**Status Management:**
- Color-coded status badges
- Contextual action buttons based on current status
- Confirmation dialogs for destructive actions

**Customer Management:**
- Quick customer selection
- Inline customer creation
- Customer history view

## Usage Guide

### Creating a Reservation

1. Click "New Reservation" button
2. Select existing customer or create new one
3. Choose reservation date (today or future)
4. Select time slot
5. Enter number of guests
6. Choose duration (optional, defaults to 2 hours)
7. Assign table (optional, can be done later)
8. Add special requests if any
9. Click "Create Reservation"
10. Customer receives automatic confirmation email

### Managing Reservations

**Pending Reservations:**
- Confirm or Cancel

**Confirmed Reservations:**
- Seat Customer (assigns table if not already assigned)
- Mark as No-Show
- Cancel

**Seated Reservations:**
- Complete (frees up table)

### Table Management Integration

When a reservation is:
- **CONFIRMED** with table: Table status → RESERVED
- **SEATED**: Table status → OCCUPIED
- **COMPLETED**: Table status → AVAILABLE
- **CANCELLED/NO_SHOW**: Table status → AVAILABLE (if was RESERVED)

## Email Notifications

### Confirmation Email
Sent automatically when reservation is created:
- Confirmation code
- Date and time
- Number of guests
- Branch name
- Contact information

### Reminder Email
Sent 24 hours before reservation (configurable):
- Reminder of upcoming reservation
- Confirmation details
- Request to confirm or cancel if plans changed

## Configuration

### Duration Options
Default: 120 minutes (2 hours)
Available: 60, 90, 120, 150, 180 minutes

### Validation Rules
- Minimum guests: 1
- Maximum guests: 50
- Date: Today or future
- Special requests: Max 500 characters
- Cancellation: Requires reason

## Database Indexes (Recommended)

For optimal performance, consider adding indexes on:
- `reservation_date, reservation_time`
- `branch_id, reservation_date`
- `branch_id, status`
- `confirmation_code` (unique)
- `customer_id`

## Future Enhancements

Potential improvements to consider:
1. **Online Booking Portal**: Customer-facing reservation system
2. **SMS Notifications**: Text message confirmations and reminders
3. **Recurring Reservations**: For regular customers
4. **Waitlist Management**: Queue system for walk-ins
5. **Capacity Planning**: Analytics on popular times
6. **Deposit/Payment**: Require deposits for large parties
7. **Cancellation Policy**: Automated enforcement of policies
8. **Floor Plan View**: Visual table selection on restaurant layout
9. **Multi-language Support**: Internationalization
10. **Integration with Calendar**: Sync with external calendars

## Testing

### Backend Testing
Test the API endpoints using:
```bash
# Create reservation
POST http://localhost:5000/api/reservations
Content-Type: application/json

{
  "customerId": 1,
  "branchId": 1,
  "reservationDate": "2025-10-20",
  "reservationTime": "19:00",
  "numberOfGuests": 4,
  "durationMinutes": 120
}

# Get reservations for branch
GET http://localhost:5000/api/reservations/branch/1/upcoming
```

### Frontend Testing
1. Navigate to Branch Manager → Reservations
2. Test create, edit, status changes
3. Verify table availability checks
4. Test customer creation flow

## Troubleshooting

**Common Issues:**

1. **No tables available**
   - Check branch has active tables defined
   - Verify table capacity meets guest requirement
   - Check for overlapping reservations

2. **Email not sending**
   - Verify EmailService configuration
   - Check customer email address is valid
   - Review email service logs

3. **Cannot update reservation**
   - Only PENDING/CONFIRMED reservations can be edited
   - Check permissions for the current user

4. **Table status not updating**
   - Verify TableLayout entity relationships
   - Check service transaction boundaries

## Support

For issues or questions regarding the reservation system:
1. Check this documentation
2. Review API endpoint documentation
3. Examine service layer implementation
4. Contact development team

---

**Last Updated**: October 2025
**Version**: 1.0.0
