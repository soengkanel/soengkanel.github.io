package com.ng.modal;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.ng.domain.DiscountType;
import com.ng.domain.OrderStatus;
import com.ng.domain.PaymentType;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "orders")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Double subtotal;

    private Double totalAmount;

    /**
     * Invoice-level discount type
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "discount_type")
    private DiscountType discountType;

    /**
     * Invoice-level discount value
     * - For PERCENTAGE: value is percentage (e.g., 10 for 10%)
     * - For FIXED_AMOUNT: value is dollar amount (e.g., 5.00 for $5)
     */
    @Column(name = "discount_value")
    private Double discountValue;

    /**
     * Calculated discount amount in dollars
     */
    @Column(name = "discount_amount")
    private Double discountAmount;

    /**
     * Optional reason or description for the discount
     */
    @Column(name = "discount_reason", length = 500)
    private String discountReason;

    private Double taxAmount;

    private LocalDateTime createdAt;

    @ManyToOne
    @JsonIgnore
    private Branch branch;

    @ManyToOne
    @JsonIgnore
    private User cashier;

    @ManyToOne
    private Customer customer;

    /**
     * Table assignment for dine-in orders
     */
    @ManyToOne
    @JoinColumn(name = "table_id")
    private TableLayout table;

    /**
     * Order type: DINE_IN, TAKEOUT, DELIVERY
     */
    @Column(name = "order_type")
    private String orderType;

    /**
     * Parent order ID for split bills (references the original order)
     */
    @Column(name = "parent_order_id")
    private Long parentOrderId;

    /**
     * Indicates if this is a split bill
     */
    @Column(name = "is_split")
    private Boolean isSplit = false;

    /**
     * Split number (e.g., 1 of 3, 2 of 3)
     */
    @Column(name = "split_number")
    private Integer splitNumber;

    private PaymentType paymentType;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> items;

    private OrderStatus status=OrderStatus.COMPLETED;

    /**
     * Indicates if this order/invoice has been voided
     */
    @Column(name = "is_voided")
    private Boolean isVoided = false;

    /**
     * Reason for voiding the order
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "void_reason")
    private com.ng.domain.VoidReason voidReason;

    /**
     * Detailed explanation for void
     */
    @Column(name = "void_notes", length = 1000)
    private String voidNotes;

    /**
     * User who voided the order
     */
    @ManyToOne
    @JoinColumn(name = "voided_by")
    private User voidedBy;

    /**
     * Timestamp when order was voided
     */
    @Column(name = "voided_at")
    private LocalDateTime voidedAt;

    /**
     * Manager who approved the void (optional)
     */
    @ManyToOne
    @JoinColumn(name = "void_approved_by")
    private User voidApprovedBy;

    @PrePersist
    public void onCreate() {
        createdAt = LocalDateTime.now();
    }

    /**
     * Get order items
     */
    public List<OrderItem> getOrderItems() {
        return items;
    }
}

