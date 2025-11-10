package com.ng.modal;

import jakarta.persistence.*;
import lombok.*;

/**
 * Individual menu item in a kitchen order
 */
@Entity
@Table(name = "kitchen_order_items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KitchenOrderItem {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    /**
     * Reference to kitchen order
     */
    @ManyToOne
    @JoinColumn(name = "kitchen_order_id", nullable = false)
    private KitchenOrder kitchenOrder;

    /**
     * Reference to order item
     */
    @ManyToOne
    @JoinColumn(name = "order_item_id", nullable = false)
    private OrderItem orderItem;

    /**
     * Menu item name (snapshot)
     */
    @Column(name = "menu_item_name", nullable = false)
    private String menuItemName;

    /**
     * Quantity to prepare
     */
    @Column(nullable = false)
    private Integer quantity;

    /**
     * Special preparation instructions
     */
    @Column(name = "special_instructions", length = 500)
    private String specialInstructions;

    /**
     * Is this item completed
     */
    @Column(name = "is_completed")
    private Boolean isCompleted = false;

    /**
     * Modifiers/customizations
     */
    @Column(length = 500)
    private String modifiers;

    /**
     * Transient field to hold MenuItem reference
     */
    @Transient
    private MenuItem menuItem;

    /**
     * Get menu item
     */
    public MenuItem getMenuItem() {
        return menuItem;
    }

    /**
     * Set menu item
     */
    public void setMenuItem(MenuItem menuItem) {
        this.menuItem = menuItem;
        if (menuItem != null) {
            this.menuItemName = menuItem.getName();
        }
    }
}
