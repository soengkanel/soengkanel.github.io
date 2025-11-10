package com.ng.controller;

import com.ng.payload.dto.OrderDTO;
import com.ng.payload.request.ChangeTableRequest;
import com.ng.payload.request.MergeTableRequest;
import com.ng.payload.request.SplitBillRequest;
import com.ng.service.TableManagementService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST API for table management operations
 */
@RestController
@RequestMapping("/api/table-management")
@RequiredArgsConstructor
public class TableManagementController {

    private final TableManagementService tableManagementService;

    /**
     * Change table for an active order
     */
    @PostMapping("/change-table")
    public ResponseEntity<OrderDTO> changeTable(@Valid @RequestBody ChangeTableRequest request) {
        OrderDTO order = tableManagementService.changeTable(request);
        return ResponseEntity.ok(order);
    }

    /**
     * Merge multiple table orders into one
     */
    @PostMapping("/merge-tables")
    public ResponseEntity<OrderDTO> mergeTables(@Valid @RequestBody MergeTableRequest request) {
        OrderDTO mergedOrder = tableManagementService.mergeTables(request);
        return ResponseEntity.ok(mergedOrder);
    }

    /**
     * Split a bill into multiple separate orders
     */
    @PostMapping("/split-bill")
    public ResponseEntity<List<OrderDTO>> splitBill(@Valid @RequestBody SplitBillRequest request) {
        List<OrderDTO> splitOrders = tableManagementService.splitBill(request);
        return ResponseEntity.ok(splitOrders);
    }

    /**
     * Get active orders for a specific table
     */
    @GetMapping("/table/{tableId}/orders")
    public ResponseEntity<List<OrderDTO>> getActiveOrdersByTable(@PathVariable Long tableId) {
        List<OrderDTO> orders = tableManagementService.getActiveOrdersByTable(tableId);
        return ResponseEntity.ok(orders);
    }
}
