package com.ng.domain;

/**
 * Type of discount applied
 */
public enum DiscountType {
    /**
     * Percentage discount (e.g., 10% off)
     */
    PERCENTAGE,

    /**
     * Fixed amount discount (e.g., $5 off)
     */
    FIXED_AMOUNT,

    /**
     * No discount applied
     */
    NONE
}
