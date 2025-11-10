package com.ng.payload.request;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Request to split a bill into multiple orders
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SplitBillRequest {

    @NotNull(message = "Original order ID is required")
    private Long originalOrderId;

    @NotEmpty(message = "Split groups cannot be empty")
    private List<SplitGroup> splitGroups;

    private String reason; // Optional reason for split

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class SplitGroup {
        @NotEmpty(message = "Order item IDs cannot be empty")
        private List<Long> orderItemIds;

        private Long customerId; // Optional customer assignment
    }
}
