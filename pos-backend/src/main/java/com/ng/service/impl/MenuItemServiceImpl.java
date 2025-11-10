package com.ng.service.impl;

import com.ng.domain.CourseType;
import com.ng.exception.ResourceNotFoundException;
import com.ng.modal.Category;
import com.ng.modal.MenuItem;
import com.ng.modal.Store;
import com.ng.payload.dto.MenuItemDTO;
import com.ng.repository.CategoryRepository;
import com.ng.repository.MenuItemRepository;
import com.ng.repository.StoreRepository;
import com.ng.service.MenuItemService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MenuItemServiceImpl implements MenuItemService {

    private final MenuItemRepository menuItemRepository;
    private final StoreRepository storeRepository;
    private final CategoryRepository categoryRepository;

    @Override
    @Transactional
    public MenuItem createMenuItem(MenuItemDTO menuItemDTO, Long storeId) {
        Store store = storeRepository.findById(storeId)
                .orElseThrow(() -> new ResourceNotFoundException("Store not found"));

        Category category = null;
        if (menuItemDTO.getCategoryId() != null) {
            category = categoryRepository.findById(menuItemDTO.getCategoryId())
                    .orElseThrow(() -> new ResourceNotFoundException("Category not found"));
        }

        MenuItem menuItem = MenuItem.builder()
                .name(menuItemDTO.getName())
                .sku(menuItemDTO.getSku())
                .description(menuItemDTO.getDescription())
                .mrp(menuItemDTO.getMrp())
                .sellingPrice(menuItemDTO.getSellingPrice())
                .image(menuItemDTO.getImage())
                .preparationTime(menuItemDTO.getPreparationTime())
                .isAvailable(menuItemDTO.getIsAvailable() != null ? menuItemDTO.getIsAvailable() : true)
                .calories(menuItemDTO.getCalories())
                .isVegetarian(menuItemDTO.getIsVegetarian())
                .isVegan(menuItemDTO.getIsVegan())
                .containsNuts(menuItemDTO.getContainsNuts())
                .isGlutenFree(menuItemDTO.getIsGlutenFree())
                .spiceLevel(menuItemDTO.getSpiceLevel())
                .courseType(menuItemDTO.getCourseType())
                .serves(menuItemDTO.getServes())
                .kitchenStation(menuItemDTO.getKitchenStation())
                .preparationNotes(menuItemDTO.getPreparationNotes())
                .portionSize(menuItemDTO.getPortionSize())
                .allowsModifiers(menuItemDTO.getAllowsModifiers() != null ? menuItemDTO.getAllowsModifiers() : true)
                .category(category)
                .store(store)
                .build();

        return menuItemRepository.save(menuItem);
    }

    @Override
    @Transactional
    public MenuItem updateMenuItem(Long menuItemId, MenuItemDTO menuItemDTO) {
        MenuItem menuItem = menuItemRepository.findById(menuItemId)
                .orElseThrow(() -> new ResourceNotFoundException("Menu item not found"));

        if (menuItemDTO.getCategoryId() != null) {
            Category category = categoryRepository.findById(menuItemDTO.getCategoryId())
                    .orElseThrow(() -> new ResourceNotFoundException("Category not found"));
            menuItem.setCategory(category);
        }

        // Update fields
        menuItem.setName(menuItemDTO.getName());
        menuItem.setSku(menuItemDTO.getSku());
        menuItem.setDescription(menuItemDTO.getDescription());
        menuItem.setMrp(menuItemDTO.getMrp());
        menuItem.setSellingPrice(menuItemDTO.getSellingPrice());
        menuItem.setImage(menuItemDTO.getImage());
        menuItem.setPreparationTime(menuItemDTO.getPreparationTime());
        menuItem.setIsAvailable(menuItemDTO.getIsAvailable());
        menuItem.setCalories(menuItemDTO.getCalories());
        menuItem.setIsVegetarian(menuItemDTO.getIsVegetarian());
        menuItem.setIsVegan(menuItemDTO.getIsVegan());
        menuItem.setContainsNuts(menuItemDTO.getContainsNuts());
        menuItem.setIsGlutenFree(menuItemDTO.getIsGlutenFree());
        menuItem.setSpiceLevel(menuItemDTO.getSpiceLevel());
        menuItem.setCourseType(menuItemDTO.getCourseType());
        menuItem.setServes(menuItemDTO.getServes());
        menuItem.setKitchenStation(menuItemDTO.getKitchenStation());
        menuItem.setPreparationNotes(menuItemDTO.getPreparationNotes());
        menuItem.setPortionSize(menuItemDTO.getPortionSize());
        menuItem.setAllowsModifiers(menuItemDTO.getAllowsModifiers());

        return menuItemRepository.save(menuItem);
    }

    @Override
    public MenuItem getMenuItemById(Long id) {
        return menuItemRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Menu item not found"));
    }

    @Override
    public List<MenuItem> getMenuItemsByStore(Long storeId) {
        return menuItemRepository.findByStoreId(storeId);
    }

    @Override
    public List<MenuItem> getAvailableMenuItems(Long storeId) {
        return menuItemRepository.findByStoreIdAndIsAvailableTrue(storeId);
    }

    @Override
    public List<MenuItem> searchMenuItems(Long storeId, String keyword) {
        return menuItemRepository.searchByKeyword(storeId, keyword);
    }

    @Override
    public List<MenuItem> getMenuItemsByCourseType(Long storeId, CourseType courseType) {
        return menuItemRepository.findAvailableItemsByCourseType(storeId, courseType);
    }

    @Override
    @Transactional
    public MenuItem toggleAvailability(Long menuItemId, Boolean isAvailable) {
        MenuItem menuItem = getMenuItemById(menuItemId);
        menuItem.setIsAvailable(isAvailable);
        return menuItemRepository.save(menuItem);
    }

    @Override
    public List<MenuItem> getQuickMenuItems(Long storeId, Integer maxMinutes) {
        return menuItemRepository.findQuickItems(storeId, maxMinutes);
    }

    @Override
    @Transactional
    public void deleteMenuItem(Long id) {
        MenuItem menuItem = getMenuItemById(id);
        menuItemRepository.delete(menuItem);
    }

    @Override
    public MenuItemDTO convertToDTO(MenuItem menuItem) {
        return MenuItemDTO.builder()
                .id(menuItem.getId())
                .name(menuItem.getName())
                .sku(menuItem.getSku())
                .description(menuItem.getDescription())
                .mrp(menuItem.getMrp())
                .sellingPrice(menuItem.getSellingPrice())
                .image(menuItem.getImage())
                .preparationTime(menuItem.getPreparationTime())
                .isAvailable(menuItem.getIsAvailable())
                .calories(menuItem.getCalories())
                .isVegetarian(menuItem.getIsVegetarian())
                .isVegan(menuItem.getIsVegan())
                .containsNuts(menuItem.getContainsNuts())
                .isGlutenFree(menuItem.getIsGlutenFree())
                .spiceLevel(menuItem.getSpiceLevel())
                .courseType(menuItem.getCourseType())
                .serves(menuItem.getServes())
                .kitchenStation(menuItem.getKitchenStation())
                .preparationNotes(menuItem.getPreparationNotes())
                .portionSize(menuItem.getPortionSize())
                .allowsModifiers(menuItem.getAllowsModifiers())
                .categoryId(menuItem.getCategory() != null ? menuItem.getCategory().getId() : null)
                .categoryName(menuItem.getCategory() != null ? menuItem.getCategory().getName() : null)
                .storeId(menuItem.getStore().getId())
                .createdAt(menuItem.getCreatedAt())
                .updatedAt(menuItem.getUpdatedAt())
                .build();
    }
}
