package com.ng.modal;

import com.ng.domain.TableStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * Represents a physical table in a restaurant
 */
@Entity
@Table(name = "table_layouts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TableLayout {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    /**
     * Table number or identifier (e.g., "T1", "A5", "Window-3")
     */
    @Column(nullable = false)
    private String tableNumber;

    /**
     * Seating capacity
     */
    @Column(nullable = false)
    private Integer capacity;

    /**
     * Current status of the table
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TableStatus status = TableStatus.AVAILABLE;

    /**
     * Physical location or zone (e.g., "Outdoor", "VIP Section", "Ground Floor")
     */
    private String location;

    /**
     * QR code for contactless ordering (optional)
     */
    @Column(name = "qr_code")
    private String qrCode;

    /**
     * Branch this table belongs to
     */
    @ManyToOne
    @JoinColumn(name = "branch_id", nullable = false)
    private Branch branch;

    /**
     * Currently active order (if occupied)
     */
    @OneToOne
    @JoinColumn(name = "current_order_id")
    private Order currentOrder;

    /**
     * Timestamp when table was occupied
     */
    @Column(name = "occupied_at")
    private LocalDateTime occupiedAt;

    /**
     * Is this table active/in use
     */
    @Column(name = "is_active")
    private Boolean isActive = true;

    /**
     * Special notes about the table
     */
    private String notes;

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
}
