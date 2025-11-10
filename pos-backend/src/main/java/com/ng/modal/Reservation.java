package com.ng.modal;

import com.ng.domain.ReservationStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;

/**
 * Represents a table reservation in a restaurant
 */
@Entity
@Table(name = "reservations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Reservation {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    /**
     * Customer making the reservation
     */
    @ManyToOne
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    /**
     * Branch where reservation is made
     */
    @ManyToOne
    @JoinColumn(name = "branch_id", nullable = false)
    private Branch branch;

    /**
     * Table reserved (optional - can be assigned later)
     */
    @ManyToOne
    @JoinColumn(name = "table_id")
    private TableLayout table;

    /**
     * Reservation date
     */
    @Column(nullable = false)
    private LocalDate reservationDate;

    /**
     * Reservation time
     */
    @Column(nullable = false)
    private LocalTime reservationTime;

    /**
     * Number of guests
     */
    @Column(nullable = false)
    private Integer numberOfGuests;

    /**
     * Current status of the reservation
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ReservationStatus status = ReservationStatus.PENDING;

    /**
     * Special requests or notes
     */
    @Column(length = 500)
    private String specialRequests;

    /**
     * Duration of reservation in minutes (default: 120)
     */
    @Column(nullable = false)
    private Integer durationMinutes = 120;

    /**
     * Confirmation code for the reservation
     */
    @Column(unique = true)
    private String confirmationCode;

    /**
     * When customer was seated (actual arrival time)
     */
    private LocalDateTime seatedAt;

    /**
     * When reservation was completed
     */
    private LocalDateTime completedAt;

    /**
     * User who created the reservation (staff member or online booking)
     */
    @ManyToOne
    @JoinColumn(name = "created_by")
    private User createdBy;

    /**
     * Reminder sent flag
     */
    @Column(name = "reminder_sent")
    private Boolean reminderSent = false;

    /**
     * Cancellation reason
     */
    private String cancellationReason;

    /**
     * Cancelled at timestamp
     */
    private LocalDateTime cancelledAt;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();
        if (confirmationCode == null) {
            confirmationCode = generateConfirmationCode();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Generate a unique confirmation code
     */
    private String generateConfirmationCode() {
        return "RES" + System.currentTimeMillis() + (int)(Math.random() * 1000);
    }

    /**
     * Check if reservation is active (can still be modified)
     */
    public boolean isActive() {
        return status == ReservationStatus.PENDING ||
               status == ReservationStatus.CONFIRMED;
    }

    /**
     * Check if reservation is past due
     */
    public boolean isPastDue() {
        LocalDateTime reservationDateTime = LocalDateTime.of(reservationDate, reservationTime);
        return LocalDateTime.now().isAfter(reservationDateTime) &&
               (status == ReservationStatus.PENDING || status == ReservationStatus.CONFIRMED);
    }
}
