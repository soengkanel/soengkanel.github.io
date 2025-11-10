package com.ng.payload.dto;

import com.ng.domain.DiscountType;
import com.ng.domain.ProductType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemDTO {

        private Long id;
        private Long productId;
        private ProductType productType;
        private String productName;
        private String productSku;
        private Integer quantity;
        private ProductDTO product; // Legacy - for backward compatibility
        private Double price;
        private DiscountType discountType;
        private Double discountValue;
        private Double discountAmount;
        private String discountReason;
        private String specialInstructions;
        private List<OrderItemModifierDTO> modifiers;

}
