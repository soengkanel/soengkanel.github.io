package com.ng.payload.dto;


import com.ng.domain.DiscountType;
import com.ng.domain.OrderStatus;
import com.ng.domain.PaymentType;
import com.ng.domain.VoidReason;
import com.ng.modal.Customer;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderDTO {
    private Long id;
    private Double subtotal;
    private Double totalAmount;
    private DiscountType discountType;
    private Double discountValue;
    private Double discountAmount;
    private String discountReason;
    private Double taxAmount;
    private Long branchId;
    private Long cashierId;
    private Customer customer;
    private List<OrderItemDTO> items;
    private LocalDateTime createdAt;
    private PaymentType paymentType;
    private OrderStatus status;

    // Void invoice fields
    private Boolean isVoided;
    private VoidReason voidReason;
    private String voidNotes;
    private Long voidedById;
    private String voidedByName;
    private LocalDateTime voidedAt;
    private Long voidApprovedById;
    private String voidApprovedByName;
}
