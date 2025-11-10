package com.ng.payload.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KitchenOrderItemDTO {
    private Long id;
    private String itemName;
    private Integer quantity;
    private String specialInstructions;
    private String courseType;
    private String spiceLevel;
    private Boolean isVegetarian;
    private Boolean isVegan;
}
