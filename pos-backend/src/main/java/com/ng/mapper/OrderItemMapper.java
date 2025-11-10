package com.ng.mapper;

import com.ng.modal.OrderItem;
import com.ng.payload.dto.OrderItemDTO;
import com.ng.payload.dto.OrderItemModifierDTO;

import java.util.stream.Collectors;

public class OrderItemMapper {

    public static OrderItemDTO toDto(OrderItem item) {
        if (item == null) return null;

        return OrderItemDTO.builder()
                .id(item.getId())
                .productId(item.getProductId())
                .productType(item.getProductType())
                .productName(item.getProductName())
                .productSku(item.getProductSku())
                .quantity(item.getQuantity())
                .price(item.getPrice())
                .discountType(item.getDiscountType())
                .discountValue(item.getDiscountValue())
                .discountAmount(item.getDiscountAmount())
                .discountReason(item.getDiscountReason())
                .specialInstructions(item.getSpecialInstructions())
                .modifiers(item.getModifiers() != null
                        ? item.getModifiers().stream()
                                .map(modifier -> OrderItemModifierDTO.builder()
                                        .id(modifier.getId())
                                        .name(modifier.getName())
                                        .additionalPrice(modifier.getAdditionalPrice())
                                        .notes(modifier.getNotes())
                                        .build())
                                .collect(Collectors.toList())
                        : null)
                .build();
    }
}
