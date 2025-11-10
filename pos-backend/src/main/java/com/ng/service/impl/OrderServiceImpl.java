package com.ng.service.impl;


import com.ng.domain.OrderStatus;
import com.ng.domain.PaymentType;
import com.ng.domain.ProductType;
import com.ng.exception.UserException;
import com.ng.mapper.OrderMapper;
import com.ng.modal.*;
import com.ng.payload.dto.OrderDTO;
import com.ng.repository.*;

import com.ng.service.OrderService;
import com.ng.service.UserService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository; // Legacy - for backward compatibility
    private final RetailProductRepository retailProductRepository;
    private final MenuItemRepository menuItemRepository;
    private final BranchRepository branchRepository;
    private final UserService userService;

    @Override
    public OrderDTO createOrder(OrderDTO dto) throws UserException {
        User cashier = userService.getCurrentUser();

        Branch branch=cashier.getBranch();

        if(branch==null){
            throw new UserException("cashier's branch is null");
        }

        Order order = Order.builder()
                .branch(branch)
                .cashier(cashier)
                .customer(dto.getCustomer())
                .paymentType(dto.getPaymentType())
                .build();

        List<OrderItem> orderItems = dto.getItems().stream().map(itemDto -> {
            // Determine product type and fetch appropriate product
            ProductType productType = itemDto.getProductType() != null
                ? itemDto.getProductType()
                : ProductType.RETAIL; // Default to RETAIL for backward compatibility

            String productName;
            String productSku;
            Double sellingPrice;

            if (productType == ProductType.RETAIL) {
                RetailProduct product = retailProductRepository.findById(itemDto.getProductId())
                        .orElseThrow(() -> new EntityNotFoundException("Retail product not found"));
                productName = product.getName();
                productSku = product.getSku();
                sellingPrice = product.getSellingPrice();
            } else {
                MenuItem menuItem = menuItemRepository.findById(itemDto.getProductId())
                        .orElseThrow(() -> new EntityNotFoundException("Menu item not found"));
                productName = menuItem.getName();
                productSku = menuItem.getSku();
                sellingPrice = menuItem.getSellingPrice();
            }

            OrderItem orderItem = OrderItem.builder()
                    .productId(itemDto.getProductId())
                    .productType(productType)
                    .productName(productName)
                    .productSku(productSku)
                    .quantity(itemDto.getQuantity())
                    .price(sellingPrice)
                    .order(order)
                    .specialInstructions(itemDto.getSpecialInstructions())
                    .discountType(itemDto.getDiscountType())
                    .discountValue(itemDto.getDiscountValue())
                    .discountReason(itemDto.getDiscountReason())
                    .build();

            // Add modifiers if present (for menu items)
            if (itemDto.getModifiers() != null && !itemDto.getModifiers().isEmpty()) {
                itemDto.getModifiers().forEach(modifierDto -> {
                    OrderItemModifier modifier = OrderItemModifier.builder()
                            .name(modifierDto.getName())
                            .additionalPrice(modifierDto.getAdditionalPrice())
                            .notes(modifierDto.getNotes())
                            .build();
                    orderItem.addModifier(modifier);
                });
            }

            // Calculate line-item discount
            orderItem.calculateDiscountAmount();

            return orderItem;
        }).toList();

        // Calculate subtotal (including line-item discounts)
        double subtotal = orderItems.stream()
                .mapToDouble(OrderItem::getTotalPrice)
                .sum();
        order.setSubtotal(subtotal);
        order.setItems(orderItems);

        // Apply invoice-level discount
        order.setDiscountType(dto.getDiscountType());
        order.setDiscountValue(dto.getDiscountValue());
        order.setDiscountReason(dto.getDiscountReason());

        double invoiceDiscountAmount = 0.0;
        if (dto.getDiscountType() != null && dto.getDiscountValue() != null && dto.getDiscountValue() > 0) {
            if (dto.getDiscountType() == com.ng.domain.DiscountType.PERCENTAGE) {
                invoiceDiscountAmount = subtotal * (dto.getDiscountValue() / 100.0);
            } else if (dto.getDiscountType() == com.ng.domain.DiscountType.FIXED_AMOUNT) {
                invoiceDiscountAmount = Math.min(dto.getDiscountValue(), subtotal);
            }
            invoiceDiscountAmount = Math.round(invoiceDiscountAmount * 100.0) / 100.0;
        }
        order.setDiscountAmount(invoiceDiscountAmount);

        // Calculate tax (if provided)
        double taxAmount = dto.getTaxAmount() != null ? dto.getTaxAmount() : 0.0;
        order.setTaxAmount(taxAmount);

        // Calculate final total
        double total = subtotal - invoiceDiscountAmount + taxAmount;
        order.setTotalAmount(Math.max(0, total));

        return OrderMapper.toDto(orderRepository.save(order));
    }

    @Override
    public OrderDTO getOrderById(Long id) {
        return orderRepository.findById(id)
                .map(OrderMapper::toDto)
                .orElseThrow(() -> new EntityNotFoundException("Order not found"));
    }



    @Override
    public List<OrderDTO> getOrdersByBranch(Long branchId,
                                            Long customerId,
                                            Long cashierId,
                                            PaymentType paymentType,
                                            OrderStatus status) {
        return orderRepository.findByBranchId(branchId).stream()

                // ✅ Filter by Customer ID (if provided)
                .filter(order -> customerId == null ||
                        (order.getCustomer() != null &&
                                order.getCustomer().getId().equals(customerId)))

                // ✅ Filter by Cashier ID (if provided)
                .filter(order -> cashierId==null ||
                        (order.getCashier() != null &&
                                order.getCashier().getId().equals(cashierId)))

                // ✅ Filter by Payment Type (if provided)
                .filter(order -> paymentType == null ||
                        order.getPaymentType() == paymentType)

                // ✅ Filter by Status (if provided)
//                .filter(order -> status() == null ||
//                        order.getStatus() == status)

                // ✅ Map to DTO
                .map(OrderMapper::toDto)

                // ✅ Sort by createdAt (latest first)
                .sorted((o1, o2) -> o2.getCreatedAt().compareTo(o1.getCreatedAt()))

                .collect(Collectors.toList());
//        return orderRepository.findByBranchId(branchId).stream()
//                .map(OrderMapper::toDto)
//                .collect(Collectors.toList());
    }

    @Override
    public List<OrderDTO> getOrdersByCashier(Long cashierId) {
        return orderRepository.findByCashierId(cashierId).stream()
                .map(OrderMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public void deleteOrder(Long id) {
        if (!orderRepository.existsById(id)) {
            throw new EntityNotFoundException("Order not found");
        }
        orderRepository.deleteById(id);
    }

    @Override
    public List<OrderDTO> getTodayOrdersByBranch(Long branchId) {
        LocalDate today = LocalDate.now();
        LocalDateTime start = today.atStartOfDay();
        LocalDateTime end = today.plusDays(1).atStartOfDay();

        return orderRepository.findByBranchIdAndCreatedAtBetween(branchId, start, end)
                .stream()
                .map(OrderMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public List<OrderDTO> getOrdersByCustomerId(Long customerId) {
        List<Order> orders = orderRepository.findByCustomerId(customerId);

        return orders.stream()
                .map(OrderMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public List<OrderDTO> getTop5RecentOrdersByBranchId(Long branchId) {
        branchRepository.findById(branchId)
                .orElseThrow(() -> new EntityNotFoundException("Branch not found with ID: " + branchId));

        List<Order> orders = orderRepository.findTop5ByBranchIdOrderByCreatedAtDesc(branchId);
        return orders.stream()
                .map(OrderMapper::toDto)
                .collect(Collectors.toList());
    }

}
