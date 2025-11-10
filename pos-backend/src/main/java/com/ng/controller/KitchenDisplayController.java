package com.ng.controller;

import com.ng.domain.KitchenStation;
import com.ng.payload.dto.KitchenOrderDTO;
import com.ng.payload.request.WaiterOrderRequest;
import com.ng.service.KitchenDisplayService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/kitchen")
@RequiredArgsConstructor
public class KitchenDisplayController {

    private final KitchenDisplayService kitchenDisplayService;

    /**
     * Get orders for specific kitchen station (Chef, Barista, etc.)
     */
    @GetMapping("/station/{station}/branch/{branchId}")
    public ResponseEntity<List<KitchenOrderDTO>> getStationOrders(
            @PathVariable KitchenStation station,
            @PathVariable Long branchId) {
        List<KitchenOrderDTO> orders = kitchenDisplayService.getOrdersByStation(station, branchId);
        return ResponseEntity.ok(orders);
    }

    /**
     * Get all active orders (for service/waiter view)
     */
    @GetMapping("/active/branch/{branchId}")
    public ResponseEntity<List<KitchenOrderDTO>> getAllActiveOrders(@PathVariable Long branchId) {
        List<KitchenOrderDTO> orders = kitchenDisplayService.getAllActiveOrders(branchId);
        return ResponseEntity.ok(orders);
    }

    /**
     * Get ready orders (for service staff to pick up)
     */
    @GetMapping("/ready/branch/{branchId}")
    public ResponseEntity<List<KitchenOrderDTO>> getReadyOrders(@PathVariable Long branchId) {
        List<KitchenOrderDTO> orders = kitchenDisplayService.getReadyOrders(branchId);
        return ResponseEntity.ok(orders);
    }

    /**
     * Start preparing an order (Chef/Barista action)
     */
    @PostMapping("/{kitchenOrderId}/start")
    public ResponseEntity<KitchenOrderDTO> startPreparation(@PathVariable Long kitchenOrderId) {
        KitchenOrderDTO order = kitchenDisplayService.startPreparation(kitchenOrderId);
        return ResponseEntity.ok(order);
    }

    /**
     * Mark order as ready (Chef/Barista action)
     */
    @PostMapping("/{kitchenOrderId}/ready")
    public ResponseEntity<KitchenOrderDTO> markAsReady(@PathVariable Long kitchenOrderId) {
        KitchenOrderDTO order = kitchenDisplayService.markAsReady(kitchenOrderId);
        return ResponseEntity.ok(order);
    }

    /**
     * Mark order as served (Waiter action)
     */
    @PostMapping("/{kitchenOrderId}/served")
    public ResponseEntity<KitchenOrderDTO> markAsServed(@PathVariable Long kitchenOrderId) {
        KitchenOrderDTO order = kitchenDisplayService.markAsServed(kitchenOrderId);
        return ResponseEntity.ok(order);
    }

    /**
     * Bump order (remove from display)
     */
    @DeleteMapping("/{kitchenOrderId}/bump")
    public ResponseEntity<Void> bumpOrder(@PathVariable Long kitchenOrderId) {
        kitchenDisplayService.bumpOrder(kitchenOrderId);
        return ResponseEntity.ok().build();
    }

    /**
     * Recall order (if accidentally bumped)
     */
    @PostMapping("/{kitchenOrderId}/recall")
    public ResponseEntity<KitchenOrderDTO> recallOrder(@PathVariable Long kitchenOrderId) {
        KitchenOrderDTO order = kitchenDisplayService.recallOrder(kitchenOrderId);
        return ResponseEntity.ok(order);
    }

    /**
     * Update order priority
     */
    @PatchMapping("/{kitchenOrderId}/priority")
    public ResponseEntity<KitchenOrderDTO> updatePriority(
            @PathVariable Long kitchenOrderId,
            @RequestParam Integer priority) {
        KitchenOrderDTO order = kitchenDisplayService.updatePriority(kitchenOrderId, priority);
        return ResponseEntity.ok(order);
    }

    /**
     * Create order via waiter/service staff
     */
    @PostMapping("/waiter-order")
    public ResponseEntity<Void> createWaiterOrder(
            @Valid @RequestBody WaiterOrderRequest request,
            Authentication authentication) {
        // Extract user ID from authentication
        Long userId = extractUserId(authentication);
        kitchenDisplayService.createWaiterOrder(request, userId);
        return ResponseEntity.ok().build();
    }

    /**
     * Route existing order to kitchen (trigger after payment or immediately)
     */
    @PostMapping("/route/{orderId}")
    public ResponseEntity<Void> routeToKitchen(@PathVariable Long orderId) {
        kitchenDisplayService.routeOrderToKitchen(orderId);
        return ResponseEntity.ok().build();
    }

    private Long extractUserId(Authentication authentication) {
        // Implementation depends on your authentication setup
        return 1L; // Placeholder
    }
}
