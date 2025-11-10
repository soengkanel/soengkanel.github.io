package com.ng.modal;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents an order in the kitchen for preparation
 * Part of Kitchen Display System (KDS)
 */
@Entity
@Table(name = "kitchen_orders")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KitchenOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    /**
     * Reference to the main order
     */
    @ManyToOne
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    /**
     * Kitchen station responsible for this order
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "kitchen_station", nullable = false)
    private KitchenStation kitchenStation;

    /**
     * Current status of kitchen order
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private KitchenOrderStatus status = KitchenOrderStatus.PENDING;

    /**
     * Order items for this kitchen station
     */
    @OneToMany(mappedBy = "kitchenOrder", cascade = CascadeType.ALL)
    @Builder.Default
    private List<KitchenOrderItem> items = new ArrayList<>();

    /**
     * Table number (for dine-in orders)
     */
    @Column(name = "table_number")
    private String tableNumber;

    /**
     * Order number for kitchen display
     */
    @Column(name = "order_number", nullable = false)
    private String orderNumber;

    /**
     * Priority level (1-5, 5 being highest)
     */
    private Integer priority = 3;

    /**
     * Special instructions for kitchen
     */
    @Column(name = "special_instructions", length = 500)
    private String specialInstructions;

    /**
     * When preparation started
     */
    @Column(name = "preparation_started_at")
    private LocalDateTime preparationStartedAt;

    /**
     * When preparation completed
     */
    @Column(name = "preparation_completed_at")
    private LocalDateTime preparationCompletedAt;

    /**
     * Estimated preparation time in minutes
     */
    @Column(name = "estimated_time")
    private Integer estimatedTime;

    /**
     * Actual time taken (in minutes)
     */
    @Column(name = "actual_time")
    private Integer actualTime;

    /**
     * Server/waiter assigned to deliver
     */
    @ManyToOne
    @JoinColumn(name = "assigned_to")
    private User assignedTo;

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

    /**
     * Calculate actual time taken
     */
    public void calculateActualTime() {
        if (preparationStartedAt != null && preparationCompletedAt != null) {
            long minutes = java.time.Duration.between(preparationStartedAt, preparationCompletedAt).toMinutes();
            this.actualTime = (int) minutes;
        }
    }
}
