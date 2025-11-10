package com.ng.payload.dto;

import com.ng.domain.ReservationStatus;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReservationDTO {
    private Long id;
    private Long customerId;
    private String customerName;
    private String customerPhone;
    private String customerEmail;
    private Long branchId;
    private String branchName;
    private Long tableId;
    private String tableNumber;
    private LocalDate reservationDate;
    private LocalTime reservationTime;
    private Integer numberOfGuests;
    private ReservationStatus status;
    private String specialRequests;
    private Integer durationMinutes;
    private String confirmationCode;
    private LocalDateTime seatedAt;
    private LocalDateTime completedAt;
    private String cancellationReason;
    private LocalDateTime cancelledAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
