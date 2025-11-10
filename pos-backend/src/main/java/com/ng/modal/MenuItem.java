package com.ng.modal;

import com.ng.domain.CourseType;
import com.ng.domain.KitchenStation;
import com.ng.domain.ProductType;
import com.ng.domain.SpiceLevel;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "menu_items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MenuItem implements IProduct {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(unique = true, nullable = false)
    private String sku; // Stock Keeping Unit

    private String description;

    @Column(nullable = false)
    private Double mrp; // Maximum Retail Price

    @Column(nullable = false)
    private Double sellingPrice; // Actual sale price

    /**
     * Cost price for profit calculation
     */
    @Column(name = "cost_price")
    private Double costPrice;

    private String image;

    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;

    @ManyToOne
    @JoinColumn(name = "store_id", nullable = false)
    private Store store;

    // ========== F&B Specific Fields ==========

    /**
     * Preparation time in minutes
     */
    @Column(name = "preparation_time")
    private Integer preparationTime;

    /**
     * Item availability status (can be toggled by restaurant)
     */
    @Column(name = "is_available", nullable = false)
    private Boolean isAvailable = true;

    /**
     * Calories information (optional nutritional data)
     */
    private Integer calories;

    /**
     * Dietary information
     */
    @Column(name = "is_vegetarian")
    private Boolean isVegetarian = false;

    @Column(name = "is_vegan")
    private Boolean isVegan = false;

    @Column(name = "contains_nuts")
    private Boolean containsNuts = false;

    @Column(name = "is_gluten_free")
    private Boolean isGlutenFree = false;

    /**
     * Spice level for the dish
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "spice_level")
    private SpiceLevel spiceLevel;

    /**
     * Course type (Appetizer, Main, Dessert, etc.)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "course_type")
    private CourseType courseType;

    /**
     * Number of people this item serves
     */
    private Integer serves;

    /**
     * Kitchen station responsible for preparing this item
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "kitchen_station")
    private KitchenStation kitchenStation;

    /**
     * Chef's special notes or preparation instructions
     */
    @Column(name = "preparation_notes", length = 500)
    private String preparationNotes;

    /**
     * Portion size description (e.g., "Regular", "Large", "500g")
     */
    @Column(name = "portion_size")
    private String portionSize;

    /**
     * Whether this item can be customized with modifiers
     */
    @Column(name = "allows_modifiers")
    private Boolean allowsModifiers = true;

    /**
     * Allergens information (comma-separated or JSON)
     */
    @Column(length = 500)
    private String allergens;

    // ========== Audit Fields ==========

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // ========== Interface Implementation ==========

    @Override
    public ProductType getProductType() {
        return ProductType.MENU_ITEM;
    }

    // ========== Helper Methods ==========

    /**
     * Get price (alias for sellingPrice)
     */
    public Double getPrice() {
        return sellingPrice;
    }

    /**
     * Get image URL (alias for image)
     */
    public String getImageUrl() {
        return image;
    }

    /**
     * Get allergens
     */
    public String getAllergens() {
        return allergens;
    }
}
