package com.ng.modal;

import com.ng.domain.ProductType;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "inventories")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Inventory {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "branch_id", nullable = false)
    private Branch branch;

    /**
     * Product ID - can reference either RetailProduct or MenuItem
     * Typically only RetailProducts have inventory tracking
     */
    @Column(name = "product_id", nullable = false)
    private Long productId;

    /**
     * Product type to determine which table to reference
     * Usually RETAIL, as menu items don't typically track inventory
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "product_type", nullable = false)
    private ProductType productType = ProductType.RETAIL;

    /**
     * Product name snapshot (for historical record)
     */
    @Column(name = "product_name")
    private String productName;

    /**
     * Product SKU snapshot
     */
    @Column(name = "product_sku")
    private String productSku;

    @Column(nullable = false)
    private Integer quantity;

    private LocalDateTime lastUpdated;

    @PrePersist
    @PreUpdate
    protected void onUpdate() {
        lastUpdated = LocalDateTime.now();
    }

    // Legacy support - keep old relationship for backward compatibility during migration
    @ManyToOne
    @JoinColumn(name = "product_id", insertable = false, updatable = false)
    private Product product;
}
