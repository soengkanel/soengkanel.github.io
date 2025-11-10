package com.ng.payload.dto;

import com.ng.domain.CourseType;
import com.ng.domain.KitchenStation;
import com.ng.domain.SpiceLevel;
import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MenuItemDTO {
    private Long id;
    private String name;
    private String sku;
    private String description;
    private Double mrp;
    private Double sellingPrice;
    private Double price;  // Alias for sellingPrice
    private String image;
    private String imageUrl;  // Alias for image
    private String allergens;  // Allergen information

    // F&B Specific
    private Integer preparationTime;
    private Boolean isAvailable;
    private Integer calories;
    private Boolean isVegetarian;
    private Boolean isVegan;
    private Boolean containsNuts;
    private Boolean isGlutenFree;
    private SpiceLevel spiceLevel;
    private CourseType courseType;
    private Integer serves;
    private KitchenStation kitchenStation;
    private String preparationNotes;
    private String portionSize;
    private Boolean allowsModifiers;

    // Category
    private Long categoryId;
    private String categoryName;

    // Store
    private Long storeId;

    // Timestamps
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
