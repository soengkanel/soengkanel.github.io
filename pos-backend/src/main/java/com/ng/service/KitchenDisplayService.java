package com.ng.service;

import com.ng.domain.KitchenStation;
import com.ng.payload.dto.KitchenOrderDTO;
import com.ng.payload.request.WaiterOrderRequest;

import java.util.List;

public interface KitchenDisplayService {

    /**
     * Create kitchen orders from a main order and route to appropriate stations
     * This automatically splits items by kitchen station and sends real-time notifications
     */
    void routeOrderToKitchen(Long orderId);

    /**
     * Get active orders for a specific kitchen station
     */
    List<KitchenOrderDTO> getOrdersByStation(KitchenStation station, Long branchId);

    /**
     * Get all active orders for a branch (for service/waiter view)
     */
    List<KitchenOrderDTO> getAllActiveOrders(Long branchId);

    /**
     * Start preparing an order (Chef/Barista marks as started)
     */
    KitchenOrderDTO startPreparation(Long kitchenOrderId);

    /**
     * Mark order as ready (Chef/Barista marks as completed)
     */
    KitchenOrderDTO markAsReady(Long kitchenOrderId);

    /**
     * Mark order as served (Waiter/Service marks as delivered to customer)
     */
    KitchenOrderDTO markAsServed(Long kitchenOrderId);

    /**
     * Bump order (remove from display after served)
     */
    void bumpOrder(Long kitchenOrderId);

    /**
     * Create order via waiter/service staff
     */
    void createWaiterOrder(WaiterOrderRequest request, Long userId);

    /**
     * Get orders ready for pickup (for service staff)
     */
    List<KitchenOrderDTO> getReadyOrders(Long branchId);

    /**
     * Recall order (if accidentally bumped)
     */
    KitchenOrderDTO recallOrder(Long kitchenOrderId);

    /**
     * Update order priority
     */
    KitchenOrderDTO updatePriority(Long kitchenOrderId, Integer priority);
}
