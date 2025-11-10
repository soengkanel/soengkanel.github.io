package com.ng.modal;

import com.ng.domain.ProductType;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "retail_products")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RetailProduct implements IProduct {

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

    private String image;

    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;

    @ManyToOne
    @JoinColumn(name = "store_id", nullable = false)
    private Store store;

    // ========== Retail Specific Fields ==========

    /**
     * Product brand/manufacturer name
     */
    private String brand;

    /**
     * Barcode for retail scanning
     */
    @Column(unique = true)
    private String barcode;

    /**
     * Manufacturer/supplier name
     */
    private String manufacturer;

    /**
     * Warranty information (e.g., "1 year", "2 years", "Lifetime")
     */
    private String warranty;

    /**
     * Product weight in kilograms
     */
    private Double weight;

    /**
     * Product dimensions (e.g., "10x5x3 cm")
     */
    private String dimensions;

    /**
     * Minimum stock level for reorder alert
     */
    @Column(name = "reorder_level")
    private Integer reorderLevel;

    /**
     * Maximum stock level
     */
    @Column(name = "max_stock_level")
    private Integer maxStockLevel;

    /**
     * HSN Code for tax purposes (India)
     */
    @Column(name = "hsn_code")
    private String hsnCode;

    /**
     * Tax rate percentage
     */
    @Column(name = "tax_rate")
    private Double taxRate;

    /**
     * Product model number
     */
    @Column(name = "model_number")
    private String modelNumber;

    /**
     * Product color
     */
    private String color;

    /**
     * Product size (S, M, L, XL or numeric)
     */
    private String size;

    /**
     * Material composition
     */
    private String material;

    /**
     * Expiry date for perishable items (optional)
     */
    @Column(name = "has_expiry")
    private Boolean hasExpiry = false;

    /**
     * Shelf life in days (for perishable items)
     */
    @Column(name = "shelf_life_days")
    private Integer shelfLifeDays;

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
        return ProductType.RETAIL;
    }
}
