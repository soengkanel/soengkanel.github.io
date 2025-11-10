package com.ng.payload.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemModifierDTO {
    private Long id;
    private String name;
    private Double additionalPrice;
    private String notes;
}
