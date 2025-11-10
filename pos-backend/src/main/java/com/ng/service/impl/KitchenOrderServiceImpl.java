package com.ng.service.impl;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import com.ng.domain.ProductType;
import com.ng.exception.ResourceNotFoundException;
import com.ng.modal.*;
import com.ng.repository.KitchenOrderRepository;
import com.ng.repository.MenuItemRepository;
import com.ng.repository.OrderRepository;
import com.ng.service.KitchenOrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class KitchenOrderServiceImpl implements KitchenOrderService {

    private final KitchenOrderRepository kitchenOrderRepository;
    private final OrderRepository orderRepository;
    private final MenuItemRepository menuItemRepository;

    @Override
    @Transactional
    public KitchenOrder createKitchenOrder(Long orderId, KitchenStation station) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new ResourceNotFoundException("Order not found"));

        // Filter order items for this kitchen station (only menu items)
        List<OrderItem> stationItems = order.getOrderItems().stream()
                .filter(item -> item.getProductType() == ProductType.MENU_ITEM)
                .filter(item -> {
                    // Get menu item to check kitchen station
                    MenuItem menuItem = menuItemRepository.findById(item.getProductId()).orElse(null);
                    return menuItem != null && menuItem.getKitchenStation() == station;
                })
                .collect(Collectors.toList());

        if (stationItems.isEmpty()) {
            throw new IllegalArgumentException("No items for kitchen station: " + station);
        }

        // Calculate estimated time
        int estimatedTime = stationItems.stream()
                .mapToInt(item -> {
                    MenuItem menuItem = menuItemRepository.findById(item.getProductId()).orElse(null);
                    return menuItem != null ? (menuItem.getPreparationTime() != null ? menuItem.getPreparationTime() : 0) : 0;
                })
                .max()
                .orElse(15); // Default 15 minutes

        KitchenOrder kitchenOrder = KitchenOrder.builder()
                .order(order)
                .kitchenStation(station)
                .status(KitchenOrderStatus.PENDING)
                .orderNumber("KO-" + orderId + "-" + station)
                .estimatedTime(estimatedTime)
                .items(new ArrayList<>())
                .build();

        kitchenOrder = kitchenOrderRepository.save(kitchenOrder);

        // Create kitchen order items
        for (OrderItem orderItem : stationItems) {
            KitchenOrderItem kitchenOrderItem = KitchenOrderItem.builder()
                    .kitchenOrder(kitchenOrder)
                    .orderItem(orderItem)
                    .menuItemName(orderItem.getProductName())
                    .quantity(orderItem.getQuantity())
                    .specialInstructions(orderItem.getSpecialInstructions())
                    .isCompleted(false)
                    .build();

            // Add modifiers as string
            if (orderItem.getModifiers() != null && !orderItem.getModifiers().isEmpty()) {
                String modifierStr = orderItem.getModifiers().stream()
                        .map(OrderItemModifier::getName)
                        .collect(Collectors.joining(", "));
                kitchenOrderItem.setModifiers(modifierStr);
            }

            kitchenOrder.getItems().add(kitchenOrderItem);
        }

        return kitchenOrderRepository.save(kitchenOrder);
    }

    @Override
    @Transactional
    public KitchenOrder updateKitchenOrderStatus(Long kitchenOrderId, KitchenOrderStatus status) {
        KitchenOrder kitchenOrder = getKitchenOrderById(kitchenOrderId);
        kitchenOrder.setStatus(status);

        if (status == KitchenOrderStatus.PREPARING && kitchenOrder.getPreparationStartedAt() == null) {
            kitchenOrder.setPreparationStartedAt(LocalDateTime.now());
        } else if (status == KitchenOrderStatus.READY && kitchenOrder.getPreparationCompletedAt() == null) {
            kitchenOrder.setPreparationCompletedAt(LocalDateTime.now());
            kitchenOrder.calculateActualTime();
        }

        return kitchenOrderRepository.save(kitchenOrder);
    }

    @Override
    public KitchenOrder getKitchenOrderById(Long id) {
        return kitchenOrderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Kitchen order not found"));
    }

    @Override
    public List<KitchenOrder> getActiveOrders() {
        return kitchenOrderRepository.findActiveOrders();
    }

    @Override
    public List<KitchenOrder> getOrdersByStation(KitchenStation station) {
        return kitchenOrderRepository.findActiveOrdersByStation(station);
    }

    @Override
    public List<KitchenOrder> getPendingOrders() {
        return kitchenOrderRepository.findByStatus(KitchenOrderStatus.PENDING);
    }

    @Override
    public List<KitchenOrder> getReadyOrders() {
        return kitchenOrderRepository.findByStatusOrderByPreparationCompletedAtAsc(KitchenOrderStatus.READY);
    }

    @Override
    @Transactional
    public KitchenOrder startPreparation(Long kitchenOrderId) {
        return updateKitchenOrderStatus(kitchenOrderId, KitchenOrderStatus.PREPARING);
    }

    @Override
    @Transactional
    public KitchenOrder completePreparation(Long kitchenOrderId) {
        return updateKitchenOrderStatus(kitchenOrderId, KitchenOrderStatus.READY);
    }

    @Override
    public List<KitchenOrder> getDelayedOrders() {
        return kitchenOrderRepository.findDelayedOrders();
    }

    @Override
    @Transactional
    public void cancelKitchenOrder(Long kitchenOrderId) {
        updateKitchenOrderStatus(kitchenOrderId, KitchenOrderStatus.CANCELLED);
    }
}
