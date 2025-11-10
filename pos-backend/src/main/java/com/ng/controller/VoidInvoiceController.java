package com.ng.controller;

import com.ng.payload.dto.OrderDTO;
import com.ng.payload.request.VoidInvoiceRequest;
import com.ng.service.VoidInvoiceService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * REST API for void invoice operations
 */
@RestController
@RequestMapping("/api/void-invoice")
@RequiredArgsConstructor
public class VoidInvoiceController {

    private final VoidInvoiceService voidInvoiceService;

    /**
     * Void an invoice/order
     */
    @PostMapping
    public ResponseEntity<OrderDTO> voidInvoice(
            @Valid @RequestBody VoidInvoiceRequest request,
            Authentication authentication) {

        // Extract user ID from authentication
        Long userId = extractUserId(authentication);

        OrderDTO voidedOrder = voidInvoiceService.voidInvoice(request, userId);
        return ResponseEntity.ok(voidedOrder);
    }

    /**
     * Get all voided orders for a branch within date range
     */
    @GetMapping("/branch/{branchId}")
    public ResponseEntity<List<OrderDTO>> getVoidedOrders(
            @PathVariable Long branchId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {

        List<OrderDTO> voidedOrders = voidInvoiceService.getVoidedOrders(branchId, startDate, endDate);
        return ResponseEntity.ok(voidedOrders);
    }

    /**
     * Get void statistics for a branch
     */
    @GetMapping("/statistics/branch/{branchId}")
    public ResponseEntity<VoidInvoiceService.VoidStatisticsDTO> getVoidStatistics(
            @PathVariable Long branchId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {

        VoidInvoiceService.VoidStatisticsDTO stats = voidInvoiceService.getVoidStatistics(branchId, startDate, endDate);
        return ResponseEntity.ok(stats);
    }

    /**
     * Helper method to extract user ID from authentication
     * TODO: Implement based on your authentication setup
     */
    private Long extractUserId(Authentication authentication) {
        // Placeholder - implement based on your auth system
        return 1L;
    }
}
