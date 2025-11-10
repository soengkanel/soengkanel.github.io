package com.ng.modal;

import jakarta.persistence.*;
import lombok.*;

/**
 * Represents modifiers/customizations for menu items in F&B orders
 * Examples: "Extra Cheese", "No Onions", "Spicy", "Large Size"
 */
@Entity
@Table(name = "order_item_modifiers")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemModifier {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Modifier name (e.g., "Extra Cheese", "No Ice")
     */
    @Column(nullable = false)
    private String name;

    /**
     * Additional price for this modifier
     */
    @Column(nullable = false)
    private Double additionalPrice;

    /**
     * Special instructions or notes
     */
    private String notes;

    /**
     * Reference to the order item this modifier belongs to
     */
    @ManyToOne
    @JoinColumn(name = "order_item_id", nullable = false)
    private OrderItem orderItem;
}
