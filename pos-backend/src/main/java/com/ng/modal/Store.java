package com.ng.modal;


import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.ng.domain.BusinessType;
import com.ng.domain.StoreStatus;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "stores")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Store {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @Column(nullable = false)
    @NotBlank(message = "brand name is required")
    private String brand;

    @OneToOne
    private User storeAdmin;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private String description;

    // Legacy field - kept for backward compatibility, use businessType instead
    private String storeType;

    /**
     * Business type determines which modules are available
     * RETAIL = Retail products only
     * FNB = Food & Beverage (Restaurant) only
     * HYBRID = Both retail and F&B
     *
     * All branches automatically inherit this businessType
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "business_type", nullable = false)
    private BusinessType businessType = BusinessType.RETAIL; // Default to retail for existing stores

    private StoreStatus status;

    // Contact Information
    @Embedded
    private StoreContact contact=new StoreContact();

    /**
     * One-to-Many relationship with branches
     * When store is deleted, all branches are deleted (cascade)
     */
    @OneToMany(mappedBy = "store", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    @Builder.Default
    private List<Branch> branches = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();
        status=StoreStatus.PENDING;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Helper method to add a branch and automatically set its businessType
     */
    public void addBranch(Branch branch) {
        if (branches == null) {
            branches = new ArrayList<>();
        }
        branches.add(branch);
        branch.setStore(this);
        branch.setBusinessType(this.businessType); // Auto-inherit
    }

    /**
     * Helper method to remove a branch
     */
    public void removeBranch(Branch branch) {
        if (branches != null) {
            branches.remove(branch);
            branch.setStore(null);
        }
    }
}
