package com.ng.repository;

import com.ng.domain.TableStatus;
import com.ng.modal.TableLayout;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface TableLayoutRepository extends JpaRepository<TableLayout, Long> {

    /**
     * Find all tables for a branch
     */
    List<TableLayout> findByBranchId(Long branchId);

    /**
     * Find active tables for a branch
     */
    List<TableLayout> findByBranchIdAndIsActiveTrue(Long branchId);

    /**
     * Find tables by status
     */
    List<TableLayout> findByBranchIdAndStatus(Long branchId, TableStatus status);

    /**
     * Find available tables
     */
    List<TableLayout> findByBranchIdAndStatusAndIsActiveTrue(Long branchId, TableStatus status);

    /**
     * Find table by number
     */
    Optional<TableLayout> findByBranchIdAndTableNumber(Long branchId, String tableNumber);

    /**
     * Find tables by location
     */
    List<TableLayout> findByBranchIdAndLocation(Long branchId, String location);

    /**
     * Find tables by capacity range
     */
    @Query("SELECT t FROM TableLayout t WHERE t.branch.id = :branchId " +
            "AND t.capacity >= :minCapacity AND t.capacity <= :maxCapacity " +
            "AND t.isActive = true")
    List<TableLayout> findByCapacityRange(@Param("branchId") Long branchId,
                                          @Param("minCapacity") Integer minCapacity,
                                          @Param("maxCapacity") Integer maxCapacity);

    /**
     * Count tables by status
     */
    long countByBranchIdAndStatus(Long branchId, TableStatus status);

    /**
     * Find occupied tables with current order
     */
    @Query("SELECT t FROM TableLayout t WHERE t.branch.id = :branchId " +
            "AND t.status = 'OCCUPIED' AND t.currentOrder IS NOT NULL")
    List<TableLayout> findOccupiedTablesWithOrders(@Param("branchId") Long branchId);
}
