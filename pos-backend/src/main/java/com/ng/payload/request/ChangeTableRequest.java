package com.ng.payload.request;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request to change table for an active order
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChangeTableRequest {

    @NotNull(message = "Order ID is required")
    private Long orderId;

    @NotNull(message = "New table ID is required")
    private Long newTableId;

    private String reason; // Optional reason for table change
}
