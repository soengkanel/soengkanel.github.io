package com.ng.repository;


import com.ng.modal.Product;
import com.ng.payload.StoreAnalysis.CategorySalesDTO;
import com.ng.payload.dto.ProductDTO;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByStoreId(Long storeId);

    @Query("SELECT p FROM Product p " +
            "WHERE p.store.id = :storeId AND (" +
            "LOWER(p.name) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(p.brand) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(p.category.name) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(p.sku) LIKE LOWER(CONCAT('%', :query, '%'))" +
            ")"
    )
    List<Product> searchByKeyword(@Param("storeId") Long storeId,
                                  @Param("query") String query);


// store analysis

    @Query("SELECT COUNT(p) FROM Product p WHERE p.store.storeAdmin.id = :storeAdminId")
    int countByStoreAdminId(@Param("storeAdminId") Long storeAdminId);

    @Query("""
        SELECT new com.ng.payload.StoreAnalysis.CategorySalesDTO(
            p.category.name,
            SUM(oi.quantity * oi.price)
        )
        FROM OrderItem oi
        JOIN Product p ON p.id = oi.productId
        WHERE p.store.storeAdmin.id = :storeAdminId
        AND oi.productType = 'RETAIL'
        GROUP BY p.category.name
    """)
    List<CategorySalesDTO> getSalesGroupedByCategory(@Param("storeAdminId") Long storeAdminId);

    @Query("""
        SELECT new com.ng.payload.dto.ProductDTO(
                p.id,
                p.name,
                p.sku,
                p.description,
                p.mrp,
                p.sellingPrice,
                p.brand,
                p.category.id,
                p.category.name,
                p.store.id,
                p.image,
                p.createdAt,
                p.updatedAt
            )
        FROM Product p
        WHERE p.store.storeAdmin.id = :storeAdminId
        AND NOT EXISTS (
            SELECT 1
            FROM Inventory i
            WHERE i.productId = p.id
            AND i.quantity > 0
        )
    """)
    List<ProductDTO> findLowStockProducts(@Param("storeAdminId") Long storeAdminId);
}
