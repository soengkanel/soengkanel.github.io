package com.ng.service;

import com.ng.domain.CourseType;
import com.ng.modal.MenuItem;
import com.ng.payload.dto.MenuItemDTO;

import java.util.List;

public interface MenuItemService {

    /**
     * Create a new menu item
     */
    MenuItem createMenuItem(MenuItemDTO menuItemDTO, Long storeId);

    /**
     * Update an existing menu item
     */
    MenuItem updateMenuItem(Long menuItemId, MenuItemDTO menuItemDTO);

    /**
     * Get menu item by ID
     */
    MenuItem getMenuItemById(Long id);

    /**
     * Get all menu items for a store
     */
    List<MenuItem> getMenuItemsByStore(Long storeId);

    /**
     * Get available menu items for a store
     */
    List<MenuItem> getAvailableMenuItems(Long storeId);

    /**
     * Search menu items by keyword
     */
    List<MenuItem> searchMenuItems(Long storeId, String keyword);

    /**
     * Get menu items by course type
     */
    List<MenuItem> getMenuItemsByCourseType(Long storeId, CourseType courseType);

    /**
     * Toggle menu item availability
     */
    MenuItem toggleAvailability(Long menuItemId, Boolean isAvailable);

    /**
     * Get quick preparation items (preparation time <= specified minutes)
     */
    List<MenuItem> getQuickMenuItems(Long storeId, Integer maxMinutes);

    /**
     * Delete menu item
     */
    void deleteMenuItem(Long id);

    /**
     * Convert entity to DTO
     */
    MenuItemDTO convertToDTO(MenuItem menuItem);
}
