package com.ng.domain;

public enum KitchenOrderStatus {
    PENDING,      // Order received, not started
    PREPARING,    // Currently being prepared
    READY,        // Ready for pickup/serve
    COMPLETED,    // Alias for SERVED
    SERVED,       // Delivered to customer
    CANCELLED     // Order cancelled
}
