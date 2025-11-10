package com.ng.domain;

/**
 * Reasons for voiding an invoice/order
 */
public enum VoidReason {
    /**
     * Customer complaint or dissatisfaction
     */
    CUSTOMER_COMPLAINT,

    /**
     * Order entry error by staff
     */
    ENTRY_ERROR,

    /**
     * Wrong items sent to customer
     */
    WRONG_ORDER,

    /**
     * Kitchen/preparation error
     */
    KITCHEN_ERROR,

    /**
     * Customer cancelled before service
     */
    CUSTOMER_CANCELLATION,

    /**
     * Payment issue or dispute
     */
    PAYMENT_ISSUE,

    /**
     * Duplicate order
     */
    DUPLICATE_ORDER,

    /**
     * Manager discretion/goodwill
     */
    MANAGER_DISCRETION,

    /**
     * System error
     */
    SYSTEM_ERROR,

    /**
     * Other reason (must provide details)
     */
    OTHER
}
