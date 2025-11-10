package com.ng.repository;

import com.ng.domain.CourseType;
import com.ng.domain.KitchenStation;
import com.ng.domain.SpiceLevel;
import com.ng.modal.MenuItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface MenuItemRepository extends JpaRepository<MenuItem, Long> {

    /**
     * Find all menu items for a specific store
     */
    List<MenuItem> findByStoreId(Long storeId);

    /**
     * Find menu item by SKU
     */
    Optional<MenuItem> findBySku(String sku);

    /**
     * Find available menu items for a store
     */
    List<MenuItem> findByStoreIdAndIsAvailableTrue(Long storeId);

    /**
     * Find unavailable menu items
     */
    List<MenuItem> findByStoreIdAndIsAvailableFalse(Long storeId);

    /**
     * Find menu items by category
     */
    List<MenuItem> findByCategoryId(Long categoryId);

    /**
     * Find menu items by course type
     */
    List<MenuItem> findByCourseType(CourseType courseType);

    /**
     * Find menu items by kitchen station
     */
    List<MenuItem> findByKitchenStation(KitchenStation kitchenStation);

    /**
     * Find vegetarian menu items
     */
    List<MenuItem> findByStoreIdAndIsVegetarianTrue(Long storeId);

    /**
     * Find vegan menu items
     */
    List<MenuItem> findByStoreIdAndIsVeganTrue(Long storeId);

    /**
     * Find menu items by spice level
     */
    List<MenuItem> findBySpiceLevel(SpiceLevel spiceLevel);

    /**
     * Search menu items by keyword (name, description, category)
     */
    @Query("SELECT mi FROM MenuItem mi " +
            "WHERE mi.store.id = :storeId AND (" +
            "LOWER(mi.name) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(mi.description) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(mi.category.name) LIKE LOWER(CONCAT('%', :query, '%')) " +
            "OR LOWER(mi.sku) LIKE LOWER(CONCAT('%', :query, '%'))" +
            ")")
    List<MenuItem> searchByKeyword(@Param("storeId") Long storeId,
                                   @Param("query") String query);

    /**
     * Find menu items by course type for a specific store
     */
    @Query("SELECT mi FROM MenuItem mi " +
            "WHERE mi.store.id = :storeId " +
            "AND mi.courseType = :courseType " +
            "AND mi.isAvailable = true " +
            "ORDER BY mi.name")
    List<MenuItem> findAvailableItemsByCourseType(@Param("storeId") Long storeId,
                                                   @Param("courseType") CourseType courseType);

    /**
     * Find menu items with preparation time less than specified minutes
     */
    @Query("SELECT mi FROM MenuItem mi " +
            "WHERE mi.store.id = :storeId " +
            "AND mi.preparationTime <= :maxMinutes " +
            "AND mi.isAvailable = true")
    List<MenuItem> findQuickItems(@Param("storeId") Long storeId,
                                  @Param("maxMinutes") Integer maxMinutes);

    /**
     * Count menu items by store
     */
    long countByStoreId(Long storeId);

    /**
     * Count available menu items by store
     */
    long countByStoreIdAndIsAvailableTrue(Long storeId);

    /**
     * Find menu items that allow modifiers
     */
    List<MenuItem> findByStoreIdAndAllowsModifiersTrue(Long storeId);

    /**
     * Get popular menu items (based on order frequency)
     */
    @Query("SELECT mi FROM MenuItem mi " +
            "JOIN OrderItem oi ON oi.productId = mi.id " +
            "WHERE mi.store.id = :storeId " +
            "AND oi.productType = 'MENU_ITEM' " +
            "GROUP BY mi.id " +
            "ORDER BY COUNT(oi.id) DESC")
    List<MenuItem> findPopularMenuItems(@Param("storeId") Long storeId);

    /**
     * Find menu items by branch (for eMenu)
     */
    @Query("SELECT mi FROM MenuItem mi WHERE mi.store.id IN " +
            "(SELECT b.store.id FROM Branch b WHERE b.id = :branchId) " +
            "AND mi.isAvailable = true")
    List<MenuItem> findByBranchIdAndIsAvailableTrue(@Param("branchId") Long branchId);

    /**
     * Find menu items by branch and category (for eMenu)
     */
    @Query("SELECT mi FROM MenuItem mi WHERE mi.store.id IN " +
            "(SELECT b.store.id FROM Branch b WHERE b.id = :branchId) " +
            "AND mi.category.id = :categoryId " +
            "AND mi.isAvailable = true")
    List<MenuItem> findByBranchIdAndCategoryIdAndIsAvailableTrue(
            @Param("branchId") Long branchId,
            @Param("categoryId") Long categoryId);
}
