package com.ng.payload.request;

import com.ng.domain.CourseType;
import com.ng.domain.KitchenStation;
import com.ng.domain.SpiceLevel;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

@Data
public class MenuItemRequest {
    @NotBlank(message = "Menu item name is required")
    private String name;

    @NotBlank(message = "SKU is required")
    private String sku;

    private String description;

    @NotNull(message = "MRP is required")
    @Positive(message = "MRP must be positive")
    private Double mrp;

    @NotNull(message = "Selling price is required")
    @Positive(message = "Selling price must be positive")
    private Double sellingPrice;

    private String image;
    private Integer preparationTime;
    private Boolean isAvailable = true;
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
    private Boolean allowsModifiers = true;
    private Long categoryId;
}
