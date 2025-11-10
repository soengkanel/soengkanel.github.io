package com.ng.domain;

public enum ReservationStatus {
    PENDING,      // Reservation is pending confirmation
    CONFIRMED,    // Reservation is confirmed
    SEATED,       // Customer has arrived and been seated
    COMPLETED,    // Reservation completed (customer left)
    CANCELLED,    // Cancelled by customer
    NO_SHOW       // Customer did not show up
}
