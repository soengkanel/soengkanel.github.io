package com.ng.payload.request;

import com.ng.domain.ReservationStatus;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateReservationStatusRequest {

    @NotNull(message = "Status is required")
    private ReservationStatus status;

    private String cancellationReason; // Required if status is CANCELLED

    private Long tableId; // Required if status is SEATED
}
