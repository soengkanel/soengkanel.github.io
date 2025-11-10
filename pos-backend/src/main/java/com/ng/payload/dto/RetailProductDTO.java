package com.ng.payload.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RetailProductDTO {
    private Long id;
    private String name;
    private String sku;
    private String description;
    private Double mrp;
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

    // Category
    private Long categoryId;
    private String categoryName;

    // Store
    private Long storeId;

    // Timestamps
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
