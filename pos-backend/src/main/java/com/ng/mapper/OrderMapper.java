package com.ng.mapper;


import com.ng.modal.Order;
import com.ng.payload.dto.OrderDTO;

import java.util.stream.Collectors;

public class OrderMapper {

    public static OrderDTO toDto(Order order) {
        return OrderDTO.builder()
                .id(order.getId())
                .subtotal(order.getSubtotal())
                .totalAmount(order.getTotalAmount())
                .discountType(order.getDiscountType())
                .discountValue(order.getDiscountValue())
                .discountAmount(order.getDiscountAmount())
                .discountReason(order.getDiscountReason())
                .taxAmount(order.getTaxAmount())
                .branchId(order.getBranch().getId())
                .cashierId(order.getCashier().getId())
                .customer(order.getCustomer())
                .createdAt(order.getCreatedAt())
                .paymentType(order.getPaymentType())
                .status(order.getStatus())
                .isVoided(order.getIsVoided())
                .voidReason(order.getVoidReason())
                .voidNotes(order.getVoidNotes())
                .voidedById(order.getVoidedBy() != null ? order.getVoidedBy().getId() : null)
                .voidedByName(order.getVoidedBy() != null ? order.getVoidedBy().getFullName() : null)
                .voidedAt(order.getVoidedAt())
                .voidApprovedById(order.getVoidApprovedBy() != null ? order.getVoidApprovedBy().getId() : null)
                .voidApprovedByName(order.getVoidApprovedBy() != null ? order.getVoidApprovedBy().getFullName() : null)
                .items(order.getItems().stream()
                        .map(OrderItemMapper::toDto)
                        .collect(Collectors.toList()))
                .build();
    }
}

