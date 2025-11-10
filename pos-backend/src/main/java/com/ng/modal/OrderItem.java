package com.ng.modal;


import com.ng.domain.DiscountType;
import com.ng.domain.ProductType;
import jakarta.persistence.*;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "order_items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Integer quantity;

    private Double price;

    /**
     * Line-item discount type
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "discount_type")
    private DiscountType discountType;

    /**
     * Line-item discount value
     * - For PERCENTAGE: value is percentage (e.g., 10 for 10%)
     * - For FIXED_AMOUNT: value is dollar amount per item (e.g., 1.00 for $1)
     */
    @Column(name = "discount_value")
    private Double discountValue;

    /**
     * Calculated discount amount in dollars (total for all quantity)
     */
    @Column(name = "discount_amount")
    private Double discountAmount;

    /**
     * Optional reason for line-item discount
     */
    @Column(name = "discount_reason", length = 500)
    private String discountReason;

    /**
     * Product ID - can reference either RetailProduct or MenuItem
     */
    @Column(name = "product_id", nullable = false)
    private Long productId;

    /**
     * Product type to determine which table to reference
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "product_type", nullable = false)
    private ProductType productType;

    /**
     * Product name snapshot (for historical record)
     */
    @Column(name = "product_name", nullable = false)
    private String productName;

    /**
     * Product SKU snapshot (for historical record)
     */
    @Column(name = "product_sku")
    private String productSku;

    /**
     * Special instructions or notes for this item (mainly for F&B)
     */
    @Column(name = "special_instructions", length = 500)
    private String specialInstructions;

    /**
     * Modifiers for menu items (e.g., Extra Cheese, No Onions)
     */
    @OneToMany(mappedBy = "orderItem", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<OrderItemModifier> modifiers = new ArrayList<>();

    @ManyToOne
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    /**
     * Transient field to hold MenuItem reference (not persisted)
     */
    @Transient
    private MenuItem product;

    /**
     * Notes/special instructions (alias for specialInstructions)
     */
    public String getNotes() {
        return specialInstructions;
    }

    public void setNotes(String notes) {
        this.specialInstructions = notes;
    }

    /**
     * Get product reference
     */
    public MenuItem getProduct() {
        return product;
    }

    public void setProduct(MenuItem product) {
        this.product = product;
        if (product != null) {
            this.productId = product.getId();
            this.productName = product.getName();
            this.productSku = product.getSku();
            this.productType = ProductType.MENU_ITEM;
        }
    }

    /**
     * Get subtotal before discount
     */
    public Double getSubtotal() {
        Double basePrice = price * quantity;
        Double modifierPrice = modifiers.stream()
                .mapToDouble(OrderItemModifier::getAdditionalPrice)
                .sum() * quantity;
        return basePrice + modifierPrice;
    }

    /**
     * Calculate total price including modifiers and discount
     */
    public Double getTotalPrice() {
        Double basePrice = price * quantity;
        Double modifierPrice = modifiers.stream()
                .mapToDouble(OrderItemModifier::getAdditionalPrice)
                .sum() * quantity;
        Double subtotal = basePrice + modifierPrice;

        // Apply line-item discount if exists
        if (discountAmount != null && discountAmount > 0) {
            subtotal -= discountAmount;
        }

        return Math.max(0, subtotal); // Ensure non-negative
    }

    /**
     * Calculate line-item discount amount based on type and value
     */
    public void calculateDiscountAmount() {
        if (discountType == null || discountType == DiscountType.NONE || discountValue == null || discountValue == 0) {
            this.discountAmount = 0.0;
            return;
        }

        Double basePrice = price * quantity;
        Double modifierPrice = modifiers.stream()
                .mapToDouble(OrderItemModifier::getAdditionalPrice)
                .sum() * quantity;
        Double subtotal = basePrice + modifierPrice;

        if (discountType == DiscountType.PERCENTAGE) {
            this.discountAmount = subtotal * (discountValue / 100.0);
        } else if (discountType == DiscountType.FIXED_AMOUNT) {
            this.discountAmount = Math.min(discountValue * quantity, subtotal);
        }

        this.discountAmount = Math.round(this.discountAmount * 100.0) / 100.0; // Round to 2 decimals
    }

    /**
     * Helper method to add modifier
     */
    public void addModifier(OrderItemModifier modifier) {
        modifiers.add(modifier);
        modifier.setOrderItem(this);
    }

    /**
     * Helper method to remove modifier
     */
    public void removeModifier(OrderItemModifier modifier) {
        modifiers.remove(modifier);
        modifier.setOrderItem(null);
    }
}
