package com.ng.repository;

import com.ng.modal.RetailProduct;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface RetailProductRepository extends JpaRepository<RetailProduct, Long> {

    /**
     * Find all retail products for a specific store
     */
    List<RetailProduct> findByStoreId(Long storeId);

    /**
     * Find retail product by SKU
     */
    Optional<RetailProduct> findBySku(String sku);

    /**
     * Find retail product by barcode
     */
    Optional<RetailProduct> findByBarcode(String barcode);

    /**
     * Find retail products by brand
     */
    List<RetailProduct> findByBrand(String brand);

    /**
     * Find retail products by category
     */
    List<RetailProduct> findByCategoryId(Long categoryId);

    /**
     * Search retail products by keyword (name, brand, sku, barcode)
     */
    @Query("SELECT rp FROM RetailProduct rp " +
            "WHERE rp.store.id = :storeId AND (" +
            "LOWER(rp.name) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(rp.brand) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(rp.category.name) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(rp.sku) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(rp.barcode) LIKE LOWER(CONCAT('%', :query, '%'))" +
            ")")
    List<RetailProduct> searchByKeyword(@Param("storeId") Long storeId,
                                        @Param("query") String query);

    /**
     * Find products below reorder level (for inventory alerts)
     */
    @Query("SELECT rp FROM RetailProduct rp " +
            "JOIN Inventory i ON i.productId = rp.id " +
            "WHERE rp.store.id = :storeId " +
            "AND i.productType = 'RETAIL' " +
            "AND i.quantity <= rp.reorderLevel")
    List<RetailProduct> findLowStockProducts(@Param("storeId") Long storeId);

    /**
     * Count retail products by store
     */
    long countByStoreId(Long storeId);

    /**
     * Find products by manufacturer
     */
    List<RetailProduct> findByManufacturer(String manufacturer);

    /**
     * Find products with expiry tracking enabled
     */
    List<RetailProduct> findByHasExpiryTrue();

    /**
     * Find products by HSN code (for tax reporting)
     */
    List<RetailProduct> findByHsnCode(String hsnCode);
}
