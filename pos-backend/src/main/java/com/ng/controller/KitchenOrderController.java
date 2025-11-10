package com.ng.controller;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import com.ng.modal.KitchenOrder;
import com.ng.service.KitchenOrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/kitchen-orders")
@RequiredArgsConstructor
public class KitchenOrderController {

    private final KitchenOrderService kitchenOrderService;

    @PostMapping
    public ResponseEntity<KitchenOrder> createKitchenOrder(
            @RequestParam Long orderId,
            @RequestParam KitchenStation station) {
        KitchenOrder kitchenOrder = kitchenOrderService.createKitchenOrder(orderId, station);
        return ResponseEntity.status(HttpStatus.CREATED).body(kitchenOrder);
    }

    @GetMapping("/{id}")
    public ResponseEntity<KitchenOrder> getKitchenOrderById(@PathVariable Long id) {
        KitchenOrder kitchenOrder = kitchenOrderService.getKitchenOrderById(id);
        return ResponseEntity.ok(kitchenOrder);
    }

    @GetMapping("/active")
    public ResponseEntity<List<KitchenOrder>> getActiveOrders() {
        List<KitchenOrder> orders = kitchenOrderService.getActiveOrders();
        return ResponseEntity.ok(orders);
    }

    @GetMapping("/station/{station}")
    public ResponseEntity<List<KitchenOrder>> getOrdersByStation(@PathVariable KitchenStation station) {
        List<KitchenOrder> orders = kitchenOrderService.getOrdersByStation(station);
        return ResponseEntity.ok(orders);
    }

    @GetMapping("/pending")
    public ResponseEntity<List<KitchenOrder>> getPendingOrders() {
        List<KitchenOrder> orders = kitchenOrderService.getPendingOrders();
        return ResponseEntity.ok(orders);
    }

    @GetMapping("/ready")
    public ResponseEntity<List<KitchenOrder>> getReadyOrders() {
        List<KitchenOrder> orders = kitchenOrderService.getReadyOrders();
        return ResponseEntity.ok(orders);
    }

    @GetMapping("/delayed")
    public ResponseEntity<List<KitchenOrder>> getDelayedOrders() {
        List<KitchenOrder> orders = kitchenOrderService.getDelayedOrders();
        return ResponseEntity.ok(orders);
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<KitchenOrder> updateStatus(
            @PathVariable Long id,
            @RequestParam KitchenOrderStatus status) {
        KitchenOrder kitchenOrder = kitchenOrderService.updateKitchenOrderStatus(id, status);
        return ResponseEntity.ok(kitchenOrder);
    }

    @PatchMapping("/{id}/start")
    public ResponseEntity<KitchenOrder> startPreparation(@PathVariable Long id) {
        KitchenOrder kitchenOrder = kitchenOrderService.startPreparation(id);
        return ResponseEntity.ok(kitchenOrder);
    }

    @PatchMapping("/{id}/complete")
    public ResponseEntity<KitchenOrder> completePreparation(@PathVariable Long id) {
        KitchenOrder kitchenOrder = kitchenOrderService.completePreparation(id);
        return ResponseEntity.ok(kitchenOrder);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> cancelKitchenOrder(@PathVariable Long id) {
        kitchenOrderService.cancelKitchenOrder(id);
        return ResponseEntity.noContent().build();
    }
}
