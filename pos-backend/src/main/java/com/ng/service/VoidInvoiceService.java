package com.ng.service;

import com.ng.payload.dto.OrderDTO;
import com.ng.payload.request.VoidInvoiceRequest;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Service for voiding invoices/orders
 */
public interface VoidInvoiceService {

    /**
     * Void an invoice/order
     * @param request Void request with reason and notes
     * @param userId User performing the void
     * @return Voided order
     */
    OrderDTO voidInvoice(VoidInvoiceRequest request, Long userId);

    /**
     * Get all voided orders for a branch
     * @param branchId Branch ID
     * @param startDate Start date filter
     * @param endDate End date filter
     * @return List of voided orders
     */
    List<OrderDTO> getVoidedOrders(Long branchId, LocalDateTime startDate, LocalDateTime endDate);

    /**
     * Get void statistics for a branch
     * @param branchId Branch ID
     * @param startDate Start date
     * @param endDate End date
     * @return Void statistics
     */
    VoidStatisticsDTO getVoidStatistics(Long branchId, LocalDateTime startDate, LocalDateTime endDate);

    /**
     * DTO for void statistics
     */
    class VoidStatisticsDTO {
        public Long totalVoidedOrders;
        public Double totalVoidedAmount;
        public java.util.Map<String, Long> voidsByReason;
        public java.util.Map<String, Long> voidsByUser;
    }
}
