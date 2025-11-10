package com.ng.modal;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.ng.domain.BusinessType;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;

@Entity
@Table(name = "branches")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Branch {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    private String name;

    private String address;

    private String phone;

    private String email;

    /**
     * Whether the branch is active
     */
    @Column(name = "is_active")
    private Boolean isActive = true;

    /**
     * Example: ["MONDAY", "TUESDAY", "WEDNESDAY"]
     */
    @ElementCollection
    private List<String> workingDays;

    private LocalTime openTime;

    private LocalTime closeTime;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    /**
     * Many-to-One relationship with Store
     * Each branch belongs to one store
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "store_id", nullable = false)
    @JsonBackReference
    private Store store;

    @OneToOne(cascade = CascadeType.REMOVE)
    @JsonIgnore
    private User manager;

    /**
     * Business type - MUST match parent store's businessType
     * This is automatically set when creating a branch
     * Cannot be changed independently from store
     *
     * RETAIL = Retail products only
     * FNB = Food & Beverage (Restaurant) only
     * HYBRID = Both retail and F&B
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "business_type")
    @Builder.Default
    private BusinessType businessType = BusinessType.RETAIL; // Default for existing data

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();

        // Auto-inherit businessType from store if not set
        if (businessType == null && store != null) {
            businessType = store.getBusinessType();
        }

        // Validate businessType matches store
        validateBusinessTypeConsistency();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();

        // Validate businessType matches store
        validateBusinessTypeConsistency();
    }

    /**
     * Validation to ensure businessType matches store
     * Called from @PrePersist and @PreUpdate hooks
     */
    private void validateBusinessTypeConsistency() {
        if (store != null && businessType != null && !store.getBusinessType().equals(businessType)) {
            throw new IllegalStateException(
                "Branch businessType (" + businessType + ") must match Store businessType (" +
                store.getBusinessType() + ")"
            );
        }
    }
}
