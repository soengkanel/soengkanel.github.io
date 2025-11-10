package com.ng.payload.request;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EMenuOrderRequest {

    @NotNull(message = "Branch ID is required")
    private Long branchId;

    @NotNull(message = "Table ID is required")
    private Long tableId;

    @NotNull(message = "Table token is required")
    private String tableToken;

    @NotEmpty(message = "Order items cannot be empty")
    private List<EMenuOrderItemRequest> items;

    private String customerName;
    private String customerPhone;
    private String specialInstructions;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class EMenuOrderItemRequest {
        @NotNull(message = "Menu item ID is required")
        private Long menuItemId;

        @NotNull(message = "Quantity is required")
        private Integer quantity;

        private String specialInstructions;
        private List<Long> modifierIds; // For add-ons, extra cheese, etc.
    }
}
