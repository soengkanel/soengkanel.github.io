package com.ng.service;

import com.ng.modal.RetailProduct;
import com.ng.payload.dto.RetailProductDTO;

import java.util.List;

public interface RetailProductService {

    /**
     * Create a new retail product
     */
    RetailProduct createRetailProduct(RetailProductDTO productDTO, Long storeId);

    /**
     * Update an existing retail product
     */
    RetailProduct updateRetailProduct(Long productId, RetailProductDTO productDTO);

    /**
     * Get retail product by ID
     */
    RetailProduct getRetailProductById(Long id);

    /**
     * Get all retail products for a store
     */
    List<RetailProduct> getRetailProductsByStore(Long storeId);

    /**
     * Search retail products by keyword
     */
    List<RetailProduct> searchRetailProducts(Long storeId, String keyword);

    /**
     * Get retail product by barcode
     */
    RetailProduct getRetailProductByBarcode(String barcode);

    /**
     * Get low stock retail products
     */
    List<RetailProduct> getLowStockProducts(Long storeId);

    /**
     * Delete retail product
     */
    void deleteRetailProduct(Long id);

    /**
     * Convert entity to DTO
     */
    RetailProductDTO convertToDTO(RetailProduct product);
}
