package com.ng.payload.request;

import com.ng.domain.VoidReason;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request to void an invoice/order
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VoidInvoiceRequest {

    @NotNull(message = "Order ID is required")
    private Long orderId;

    @NotNull(message = "Void reason is required")
    private VoidReason voidReason;

    @NotNull(message = "Void notes/explanation is required")
    private String voidNotes;

    /**
     * Manager ID for approval (optional based on settings)
     */
    private Long managerId;

    /**
     * Manager password for verification (optional)
     */
    private String managerPassword;
}
