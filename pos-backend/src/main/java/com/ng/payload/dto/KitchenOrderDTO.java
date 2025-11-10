package com.ng.payload.dto;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KitchenOrderDTO {
    private Long id;
    private Long orderId;
    private String orderNumber;
    private KitchenStation kitchenStation;
    private KitchenOrderStatus status;
    private String tableNumber;
    private Integer priority;
    private String specialInstructions;
    private Integer estimatedTime;
    private Integer actualTime;
    private LocalDateTime createdAt;
    private LocalDateTime preparationStartedAt;
    private LocalDateTime preparationCompletedAt;
    private List<KitchenOrderItemDTO> items;
    private Long branchId;
    private String branchName;
}
