package com.ng.controller;

import com.ng.domain.CourseType;
import com.ng.modal.MenuItem;
import com.ng.payload.dto.MenuItemDTO;
import com.ng.payload.request.MenuItemRequest;
import com.ng.service.MenuItemService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/menu-items")
@RequiredArgsConstructor
public class MenuItemController {

    private final MenuItemService menuItemService;

    /**
     * Create a new menu item
     */
    @PostMapping
    public ResponseEntity<MenuItemDTO> createMenuItem(
            @Valid @RequestBody MenuItemRequest request,
            @RequestParam Long storeId) {

        MenuItemDTO dto = mapRequestToDTO(request);
        MenuItem menuItem = menuItemService.createMenuItem(dto, storeId);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(menuItemService.convertToDTO(menuItem));
    }

    /**
     * Update an existing menu item
     */
    @PutMapping("/{id}")
    public ResponseEntity<MenuItemDTO> updateMenuItem(
            @PathVariable Long id,
            @Valid @RequestBody MenuItemRequest request) {

        MenuItemDTO dto = mapRequestToDTO(request);
        MenuItem menuItem = menuItemService.updateMenuItem(id, dto);
        return ResponseEntity.ok(menuItemService.convertToDTO(menuItem));
    }

    /**
     * Get menu item by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<MenuItemDTO> getMenuItemById(@PathVariable Long id) {
        MenuItem menuItem = menuItemService.getMenuItemById(id);
        return ResponseEntity.ok(menuItemService.convertToDTO(menuItem));
    }

    /**
     * Get all menu items for a store
     */
    @GetMapping
    public ResponseEntity<List<MenuItemDTO>> getMenuItemsByStore(@RequestParam Long storeId) {
        List<MenuItem> menuItems = menuItemService.getMenuItemsByStore(storeId);
        List<MenuItemDTO> dtos = menuItems.stream()
                .map(menuItemService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Get available menu items for a store
     */
    @GetMapping("/available")
    public ResponseEntity<List<MenuItemDTO>> getAvailableMenuItems(@RequestParam Long storeId) {
        List<MenuItem> menuItems = menuItemService.getAvailableMenuItems(storeId);
        List<MenuItemDTO> dtos = menuItems.stream()
                .map(menuItemService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Search menu items by keyword
     */
    @GetMapping("/search")
    public ResponseEntity<List<MenuItemDTO>> searchMenuItems(
            @RequestParam Long storeId,
            @RequestParam String keyword) {

        List<MenuItem> menuItems = menuItemService.searchMenuItems(storeId, keyword);
        List<MenuItemDTO> dtos = menuItems.stream()
                .map(menuItemService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Get menu items by course type
     */
    @GetMapping("/course/{courseType}")
    public ResponseEntity<List<MenuItemDTO>> getMenuItemsByCourseType(
            @PathVariable CourseType courseType,
            @RequestParam Long storeId) {

        List<MenuItem> menuItems = menuItemService.getMenuItemsByCourseType(storeId, courseType);
        List<MenuItemDTO> dtos = menuItems.stream()
                .map(menuItemService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Toggle menu item availability
     */
    @PatchMapping("/{id}/availability")
    public ResponseEntity<MenuItemDTO> toggleAvailability(
            @PathVariable Long id,
            @RequestParam Boolean isAvailable) {

        MenuItem menuItem = menuItemService.toggleAvailability(id, isAvailable);
        return ResponseEntity.ok(menuItemService.convertToDTO(menuItem));
    }

    /**
     * Get quick preparation menu items
     */
    @GetMapping("/quick")
    public ResponseEntity<List<MenuItemDTO>> getQuickMenuItems(
            @RequestParam Long storeId,
            @RequestParam(defaultValue = "15") Integer maxMinutes) {

        List<MenuItem> menuItems = menuItemService.getQuickMenuItems(storeId, maxMinutes);
        List<MenuItemDTO> dtos = menuItems.stream()
                .map(menuItemService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Delete menu item
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteMenuItem(@PathVariable Long id) {
        menuItemService.deleteMenuItem(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Helper method to map request to DTO
     */
    private MenuItemDTO mapRequestToDTO(MenuItemRequest request) {
        return MenuItemDTO.builder()
                .name(request.getName())
                .sku(request.getSku())
                .description(request.getDescription())
                .mrp(request.getMrp())
                .sellingPrice(request.getSellingPrice())
                .image(request.getImage())
                .preparationTime(request.getPreparationTime())
                .isAvailable(request.getIsAvailable())
                .calories(request.getCalories())
                .isVegetarian(request.getIsVegetarian())
                .isVegan(request.getIsVegan())
                .containsNuts(request.getContainsNuts())
                .isGlutenFree(request.getIsGlutenFree())
                .spiceLevel(request.getSpiceLevel())
                .courseType(request.getCourseType())
                .serves(request.getServes())
                .kitchenStation(request.getKitchenStation())
                .preparationNotes(request.getPreparationNotes())
                .portionSize(request.getPortionSize())
                .allowsModifiers(request.getAllowsModifiers())
                .categoryId(request.getCategoryId())
                .build();
    }
}
