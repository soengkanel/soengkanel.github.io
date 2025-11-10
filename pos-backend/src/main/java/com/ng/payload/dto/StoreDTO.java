package com.ng.payload.dto;

import com.ng.domain.BusinessType;
import com.ng.domain.StoreStatus;
import com.ng.modal.StoreContact;
import lombok.*;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StoreDTO {
    private Long id;
    private String brand;
    private Long storeAdminId;
    private UserDTO storeAdmin;
    private String storeType; // Legacy field - use businessType instead
    private BusinessType businessType;
    private StoreStatus status;
    private String description;
    private StoreContact contact;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /**
     * Total number of branches for this store
     * This is a computed field to avoid circular reference issues
     */
    private Integer totalBranches;
}
