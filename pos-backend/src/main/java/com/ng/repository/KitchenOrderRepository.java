package com.ng.repository;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import com.ng.modal.KitchenOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface KitchenOrderRepository extends JpaRepository<KitchenOrder, Long> {

    /**
     * Find kitchen orders by status
     */
    List<KitchenOrder> findByStatus(KitchenOrderStatus status);

    /**
     * Find kitchen orders by station
     */
    List<KitchenOrder> findByKitchenStation(KitchenStation kitchenStation);

    /**
     * Find kitchen orders by station and status
     */
    List<KitchenOrder> findByKitchenStationAndStatus(KitchenStation kitchenStation, KitchenOrderStatus status);

    /**
     * Find pending kitchen orders ordered by priority and creation time
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.status = 'PENDING' " +
            "ORDER BY ko.priority DESC, ko.createdAt ASC")
    List<KitchenOrder> findPendingOrdersByPriority();

    /**
     * Find kitchen orders for a specific order
     */
    List<KitchenOrder> findByOrderId(Long orderId);

    /**
     * Find active kitchen orders (pending or preparing)
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.status IN ('PENDING', 'PREPARING') " +
            "ORDER BY ko.priority DESC, ko.createdAt ASC")
    List<KitchenOrder> findActiveOrders();

    /**
     * Find kitchen orders by station with active status
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.kitchenStation = :station " +
            "AND ko.status IN ('PENDING', 'PREPARING') " +
            "ORDER BY ko.priority DESC, ko.createdAt ASC")
    List<KitchenOrder> findActiveOrdersByStation(@Param("station") KitchenStation station);

    /**
     * Find orders by time range
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.createdAt >= :startTime " +
            "AND ko.createdAt <= :endTime")
    List<KitchenOrder> findByTimeRange(@Param("startTime") LocalDateTime startTime,
                                       @Param("endTime") LocalDateTime endTime);

    /**
     * Find delayed orders (taking longer than estimated time)
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.status = 'PREPARING' " +
            "AND ko.preparationStartedAt IS NOT NULL " +
            "AND TIMESTAMPDIFF(MINUTE, ko.preparationStartedAt, CURRENT_TIMESTAMP) > ko.estimatedTime")
    List<KitchenOrder> findDelayedOrders();

    /**
     * Get average preparation time by station
     */
    @Query("SELECT AVG(ko.actualTime) FROM KitchenOrder ko " +
            "WHERE ko.kitchenStation = :station AND ko.actualTime IS NOT NULL")
    Double getAveragePreparationTime(@Param("station") KitchenStation station);

    /**
     * Count orders by status
     */
    long countByStatus(KitchenOrderStatus status);

    /**
     * Find ready orders for pickup
     */
    List<KitchenOrder> findByStatusOrderByPreparationCompletedAtAsc(KitchenOrderStatus status);

    /**
     * Find kitchen orders by station, branch, and statuses (for KDS)
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.kitchenStation = :station " +
            "AND ko.order.branch.id = :branchId " +
            "AND ko.status IN :statuses " +
            "ORDER BY ko.priority DESC, ko.createdAt ASC")
    List<KitchenOrder> findByKitchenStationAndOrderBranchIdAndStatusIn(
            @Param("station") KitchenStation station,
            @Param("branchId") Long branchId,
            @Param("statuses") List<KitchenOrderStatus> statuses);

    /**
     * Find kitchen orders by branch excluding a status
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.order.branch.id = :branchId " +
            "AND ko.status <> :status " +
            "ORDER BY ko.priority DESC, ko.createdAt ASC")
    List<KitchenOrder> findByOrderBranchIdAndStatusNot(
            @Param("branchId") Long branchId,
            @Param("status") KitchenOrderStatus status);

    /**
     * Find kitchen orders by branch and status
     */
    @Query("SELECT ko FROM KitchenOrder ko WHERE ko.order.branch.id = :branchId " +
            "AND ko.status = :status " +
            "ORDER BY ko.preparationCompletedAt ASC")
    List<KitchenOrder> findByOrderBranchIdAndStatus(
            @Param("branchId") Long branchId,
            @Param("status") KitchenOrderStatus status);
}
