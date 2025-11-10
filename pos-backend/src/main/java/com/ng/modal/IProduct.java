package com.ng.modal;

import com.ng.domain.ProductType;

/**
 * Common interface for all product types (Retail, Menu Items, etc.)
 * Provides abstraction layer for polymorphic product handling
 */
public interface IProduct {
    Long getId();
    String getName();
    String getSku();
    String getDescription();
    Double getMrp();
    Double getSellingPrice();
    String getImage();
    Category getCategory();
    Store getStore();
    ProductType getProductType();
}
