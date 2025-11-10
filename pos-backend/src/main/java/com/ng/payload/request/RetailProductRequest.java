package com.ng.payload.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

@Data
public class RetailProductRequest {
    @NotBlank(message = "Product name is required")
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

    private String brand;
    private String barcode;
    private String manufacturer;
    private String warranty;
    private Double weight;
    private String dimensions;
    private Integer reorderLevel;
    private Integer maxStockLevel;
    private String hsnCode;
    private Double taxRate;
    private String modelNumber;
    private String color;
    private String size;
    private String material;
    private Boolean hasExpiry;
    private Integer shelfLifeDays;
    private String image;
    private Long categoryId;
}
