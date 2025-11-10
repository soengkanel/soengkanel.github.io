package com.ng.service.impl;

import com.ng.domain.*;
import com.ng.modal.*;
import com.ng.repository.*;
import com.ng.service.FnbInitializationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class FnbInitializationServiceImpl implements FnbInitializationService {

    private final CategoryRepository categoryRepository;
    private final MenuItemRepository menuItemRepository;
    private final TableLayoutRepository tableLayoutRepository;
    private final BranchRepository branchRepository;

    @Override
    @Transactional
    public void initializeFnbSampleData(Store store, Branch branch) {
        log.info("Initializing F&B sample data for store: {} (Business Type: {})",
                store.getBrand(), store.getBusinessType());

        // If branch is null, create a default main branch
        if (branch == null) {
            branch = createDefaultBranch(store);
        }

        // Create sample categories
        List<Category> categories = createSampleCategories(store);

        // Create sample menu items
        createSampleMenuItems(store, categories);

        // Create sample tables (only if branch exists)
        if (branch != null) {
            createSampleTables(branch);
        }

        log.info("Successfully initialized F&B sample data for store: {}", store.getBrand());
    }

    private Branch createDefaultBranch(Store store) {
        log.info("Creating default main branch for store: {}", store.getBrand());

        Branch branch = Branch.builder()
                .name("Main Branch")
                .store(store)
                .address(store.getContact() != null ? store.getContact().getAddress() : "Not specified")
                .phone(store.getContact() != null ? store.getContact().getPhone() : null)
                .email(store.getContact() != null ? store.getContact().getEmail() : null)
                .isActive(true)
                .build();

        return branchRepository.save(branch);
    }

    private List<Category> createSampleCategories(Store store) {
        log.info("Creating sample categories for store: {}", store.getBrand());

        List<Category> categories = new ArrayList<>();

        String[] categoryNames = {
                "Appetizers",
                "Main Course",
                "Desserts",
                "Beverages",
                "Coffee & Tea",
                "Salads"
        };

        for (String name : categoryNames) {
            Category category = Category.builder()
                    .name(name)
                    .store(store)
                    .build();
            categories.add(categoryRepository.save(category));
        }

        log.info("Created {} categories", categories.size());
        return categories;
    }

    private void createSampleMenuItems(Store store, List<Category> categories) {
        log.info("Creating sample menu items for store: {}", store.getBrand());

        // Get categories by name
        Category appetizers = categories.stream()
                .filter(c -> c.getName().equals("Appetizers"))
                .findFirst().orElse(categories.get(0));

        Category mainCourse = categories.stream()
                .filter(c -> c.getName().equals("Main Course"))
                .findFirst().orElse(categories.get(0));

        Category desserts = categories.stream()
                .filter(c -> c.getName().equals("Desserts"))
                .findFirst().orElse(categories.get(0));

        Category beverages = categories.stream()
                .filter(c -> c.getName().equals("Beverages"))
                .findFirst().orElse(categories.get(0));

        Category coffee = categories.stream()
                .filter(c -> c.getName().equals("Coffee & Tea"))
                .findFirst().orElse(categories.get(0));

        // Appetizers
        createMenuItem(store, appetizers, "Spring Rolls", "MENU-APP-001",
                "Crispy vegetable spring rolls served with sweet chili sauce",
                8.99, CourseType.APPETIZER, 10, KitchenStation.FRY);

        createMenuItem(store, appetizers, "Garlic Bread", "MENU-APP-002",
                "Toasted bread with garlic butter and herbs",
                5.99, CourseType.APPETIZER, 5, KitchenStation.GRILL);

        createMenuItem(store, appetizers, "Chicken Wings", "MENU-APP-003",
                "Spicy buffalo chicken wings with ranch dip",
                12.99, CourseType.APPETIZER, 15, KitchenStation.FRY);

        // Main Course
        createMenuItem(store, mainCourse, "Grilled Chicken", "MENU-MAIN-001",
                "Herb-marinated grilled chicken with vegetables",
                18.99, CourseType.MAIN, 20, KitchenStation.GRILL);

        createMenuItem(store, mainCourse, "Beef Burger", "MENU-MAIN-002",
                "Juicy beef burger with cheese, lettuce, and fries",
                15.99, CourseType.MAIN, 15, KitchenStation.GRILL);

        createMenuItem(store, mainCourse, "Pasta Carbonara", "MENU-MAIN-003",
                "Creamy pasta with bacon and parmesan",
                14.99, CourseType.MAIN, 18, KitchenStation.HOT_STATION);

        createMenuItem(store, mainCourse, "Fish and Chips", "MENU-MAIN-004",
                "Beer-battered fish with crispy fries",
                16.99, CourseType.MAIN, 20, KitchenStation.FRY);

        // Desserts
        createMenuItem(store, desserts, "Chocolate Cake", "MENU-DES-001",
                "Rich chocolate cake with chocolate ganache",
                7.99, CourseType.DESSERT, 5, KitchenStation.PASTRY);

        createMenuItem(store, desserts, "Ice Cream Sundae", "MENU-DES-002",
                "Vanilla ice cream with chocolate sauce and nuts",
                6.99, CourseType.DESSERT, 3, KitchenStation.COLD_STATION);

        createMenuItem(store, desserts, "Cheesecake", "MENU-DES-003",
                "New York style cheesecake with berry compote",
                8.99, CourseType.DESSERT, 5, KitchenStation.PASTRY);

        // Beverages
        createMenuItem(store, beverages, "Fresh Orange Juice", "MENU-BEV-001",
                "Freshly squeezed orange juice",
                4.99, CourseType.BEVERAGE, 3, KitchenStation.BEVERAGE);

        createMenuItem(store, beverages, "Coca Cola", "MENU-BEV-002",
                "Chilled Coca Cola (330ml)",
                2.99, CourseType.BEVERAGE, 1, KitchenStation.BEVERAGE);

        createMenuItem(store, beverages, "Mineral Water", "MENU-BEV-003",
                "Still mineral water (500ml)",
                1.99, CourseType.BEVERAGE, 1, KitchenStation.BEVERAGE);

        // Coffee & Tea
        createMenuItem(store, coffee, "Cappuccino", "MENU-COF-001",
                "Italian cappuccino with steamed milk",
                4.99, CourseType.BEVERAGE, 5, KitchenStation.BEVERAGE);

        createMenuItem(store, coffee, "Espresso", "MENU-COF-002",
                "Strong Italian espresso",
                3.99, CourseType.BEVERAGE, 3, KitchenStation.BEVERAGE);

        createMenuItem(store, coffee, "Green Tea", "MENU-COF-003",
                "Premium jasmine green tea",
                3.49, CourseType.BEVERAGE, 5, KitchenStation.BEVERAGE);

        log.info("Created 16 sample menu items");
    }

    private void createMenuItem(Store store, Category category, String name, String sku,
                                  String description, Double price, CourseType courseType,
                                  Integer prepTime, KitchenStation station) {
        MenuItem menuItem = MenuItem.builder()
                .name(name)
                .sku(sku)
                .description(description)
                .sellingPrice(price)
                .costPrice(price * 0.4) // 60% margin
                .category(category)
                .store(store)
                .isAvailable(true)
                .preparationTime(prepTime)
                .courseType(courseType)
                .kitchenStation(station)
                .spiceLevel(SpiceLevel.NONE)
                .isVegetarian(name.contains("Vegetable") || name.contains("Salad"))
                .build();

        menuItemRepository.save(menuItem);
    }

    private void createSampleTables(Branch branch) {
        log.info("Creating sample tables for branch: {}", branch.getName());

        // Create 10 sample tables with different capacities
        String[] locations = {"Indoor", "Indoor", "Indoor", "Indoor", "Indoor",
                              "Outdoor", "Outdoor", "VIP Section", "VIP Section", "Bar Area"};
        Integer[] capacities = {2, 4, 4, 6, 2, 4, 4, 8, 6, 4};

        for (int i = 0; i < 10; i++) {
            TableLayout table = TableLayout.builder()
                    .tableNumber("T" + (i + 1))
                    .capacity(capacities[i])
                    .location(locations[i])
                    .status(TableStatus.AVAILABLE)
                    .branch(branch)
                    .isActive(true)
                    .notes(i < 2 ? "Window seat" : null)
                    .build();

            tableLayoutRepository.save(table);
        }

        log.info("Created 10 sample tables");
    }
}
