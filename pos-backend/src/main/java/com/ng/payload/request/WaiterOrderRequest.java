package com.ng.payload.request;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WaiterOrderRequest {

    @NotNull(message = "Branch ID is required")
    private Long branchId;

    @NotNull(message = "Table ID is required")
    private Long tableId;

    private Long customerId; // Optional

    @NotEmpty(message = "Order items cannot be empty")
    private List<WaiterOrderItemRequest> items;

    private String specialInstructions;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class WaiterOrderItemRequest {
        @NotNull(message = "Menu item ID is required")
        private Long menuItemId;

        @NotNull(message = "Quantity is required")
        private Integer quantity;

        private String specialInstructions;
    }
}
