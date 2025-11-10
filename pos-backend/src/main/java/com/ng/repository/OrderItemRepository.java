package com.ng.repository;

import com.ng.modal.OrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {

    @Query("""
        SELECT oi.productId, oi.productName, SUM(oi.quantity)
        FROM OrderItem oi
        JOIN oi.order o
        WHERE o.branch.id = :branchId
        GROUP BY oi.productId, oi.productName
        ORDER BY SUM(oi.quantity) DESC
    """)
    List<Object[]> getTopProductsByQuantity(@Param("branchId") Long branchId);

    @Query("""
        SELECT
            CASE
                WHEN oi.productType = 'RETAIL' THEN rp.category.name
                WHEN oi.productType = 'MENU_ITEM' THEN mi.category.name
                ELSE 'Unknown'
            END,
            SUM(oi.quantity * oi.price),
            SUM(oi.quantity)
        FROM OrderItem oi
        LEFT JOIN RetailProduct rp ON rp.id = oi.productId AND oi.productType = 'RETAIL'
        LEFT JOIN MenuItem mi ON mi.id = oi.productId AND oi.productType = 'MENU_ITEM'
        JOIN oi.order o
        WHERE o.branch.id = :branchId AND o.createdAt BETWEEN :start AND :end
        GROUP BY
            CASE
                WHEN oi.productType = 'RETAIL' THEN rp.category.name
                WHEN oi.productType = 'MENU_ITEM' THEN mi.category.name
                ELSE 'Unknown'
            END
        ORDER BY SUM(oi.quantity * oi.price) DESC
    """)
    List<Object[]> getCategoryWiseSales(
            @Param("branchId") Long branchId,
            @Param("start") LocalDateTime start,
            @Param("end") LocalDateTime end
    );




}
