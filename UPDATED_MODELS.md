# Updated Store and Branch Models

## Changes Required:

### 1. Store.java - Add branches relationship and remove storeType

```java
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

    // ❌ REMOVE THIS - Use businessType instead
    // private String storeType;

    /**
     * Business type determines which modules are available
     * RETAIL = Retail products only
     * FNB = Food & Beverage (Restaurant) only
     * HYBRID = Both retail and F&B
     *
     * All branches inherit this businessType automatically
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "business_type", nullable = false)
    private BusinessType businessType = BusinessType.RETAIL;

    private StoreStatus status;

    // Contact Information
    @Embedded
    private StoreContact contact = new StoreContact();

    // ✅ ADD THIS - One-to-Many relationship with branches
    @OneToMany(mappedBy = "store", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    @Builder.Default
    private List<Branch> branches = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();
        status = StoreStatus.PENDING;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // Helper method to add branch
    public void addBranch(Branch branch) {
        branches.add(branch);
        branch.setStore(this);
        branch.setBusinessType(this.businessType); // Auto-inherit
    }
}
```

### 2. Branch.java - Add businessType field and update relationship

```java
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

    // ✅ Many-to-One relationship with Store
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "store_id", nullable = false)
    @JsonBackReference
    private Store store;

    @OneToOne(cascade = CascadeType.REMOVE)
    @JsonIgnore
    private User manager;

    // ✅ ADD THIS - Business type inherited from store
    /**
     * Business type - MUST match parent store's businessType
     * This is automatically set when creating a branch
     * Cannot be changed independently from store
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "business_type", nullable = false)
    private BusinessType businessType;

    @PrePersist
    protected void onCreate() {
        createdAt = updatedAt = LocalDateTime.now();

        // ✅ AUTO-INHERIT businessType from store if not set
        if (businessType == null && store != null) {
            businessType = store.getBusinessType();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // ✅ ADD THIS - Validation to ensure businessType matches store
    @PrePersist
    @PreUpdate
    private void validateBusinessType() {
        if (store != null && businessType != null && !store.getBusinessType().equals(businessType)) {
            throw new IllegalStateException(
                "Branch businessType (" + businessType + ") must match Store businessType (" +
                store.getBusinessType() + ")"
            );
        }
    }
}
```

## Database Migration Script

If you're using Flyway or Liquibase, here's the SQL to update your database:

```sql
-- Add business_type column to branches table
ALTER TABLE branches
ADD COLUMN business_type VARCHAR(20);

-- Update existing branches to inherit from their store
UPDATE branches b
SET business_type = (
    SELECT s.business_type
    FROM stores s
    WHERE s.id = b.store_id
)
WHERE b.store_id IS NOT NULL;

-- Make the column NOT NULL after populating it
ALTER TABLE branches
MODIFY COLUMN business_type VARCHAR(20) NOT NULL;

-- Optional: Remove the legacy storeType column from stores
-- (Do this AFTER ensuring all code uses businessType)
-- ALTER TABLE stores DROP COLUMN store_type;
```

## Service Layer Update - BranchServiceImpl.java

Update your `createBranch` method to automatically set businessType:

```java
@Override
public Branch createBranch(BranchDTO branchDTO) {
    // 1. Find the parent store
    Store store = storeRepository.findById(branchDTO.getStoreId())
        .orElseThrow(() -> new ResourceNotFoundException("Store not found"));

    // 2. Create branch
    Branch branch = Branch.builder()
        .name(branchDTO.getName())
        .address(branchDTO.getAddress())
        .phone(branchDTO.getPhone())
        .email(branchDTO.getEmail())
        .store(store)
        .businessType(store.getBusinessType()) // ✅ AUTO-INHERIT from store
        .isActive(true)
        .build();

    // 3. Set manager if provided
    if (branchDTO.getManagerId() != null) {
        User manager = userRepository.findById(branchDTO.getManagerId())
            .orElseThrow(() -> new ResourceNotFoundException("Manager not found"));
        branch.setManager(manager);
    }

    // 4. Save
    return branchRepository.save(branch);
}
```

## Mapper Update - BranchMapper.java

Ensure your mapper includes businessType:

```java
public static BranchDTO toBranchDTO(Branch branch) {
    return BranchDTO.builder()
        .id(branch.getId())
        .name(branch.getName())
        .address(branch.getAddress())
        .phone(branch.getPhone())
        .email(branch.getEmail())
        .storeId(branch.getStore() != null ? branch.getStore().getId() : null)
        .managerId(branch.getManager() != null ? branch.getManager().getId() : null)
        .businessType(branch.getBusinessType()) // ✅ Include this
        .isActive(branch.getIsActive())
        .workingDays(branch.getWorkingDays())
        .openTime(branch.getOpenTime())
        .closeTime(branch.getCloseTime())
        .createdAt(branch.getCreatedAt())
        .updatedAt(branch.getUpdatedAt())
        .build();
}
```

## Testing Checklist

After making these changes:

1. ✅ Create a new branch - should automatically have businessType from store
2. ✅ View branches list - should display correct businessType (FNB, RETAIL, HYBRID)
3. ✅ Try to change branch businessType manually - should fail validation
4. ✅ Change store businessType - all branches should remain with their original type (or implement cascading update if needed)

## Summary of Changes

### Store Model:
- ❌ Remove `storeType` field (legacy)
- ✅ Keep `businessType` field (already exists)
- ✅ Add `@OneToMany` relationship with branches

### Branch Model:
- ✅ Add `businessType` field
- ✅ Add `@JsonBackReference` to store relationship
- ✅ Add validation to ensure businessType matches store
- ✅ Auto-inherit businessType in `@PrePersist`

### Database:
- ✅ Add `business_type` column to `branches` table
- ✅ Populate with store's businessType
- ✅ Make it NOT NULL

This will fix the issue where branches show "Retail" even for restaurant stores!
