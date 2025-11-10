package com.ng.payload.dto;


import com.ng.domain.ProductType;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryDTO {
    private Long id;
    private Long branchId;
    private Long productId;
    private ProductType productType;
    private String productName;
    private String productSku;
    private Integer quantity;
}

