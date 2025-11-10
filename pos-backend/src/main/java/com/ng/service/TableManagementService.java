package com.ng.service;

import com.ng.payload.dto.OrderDTO;
import com.ng.payload.request.ChangeTableRequest;
import com.ng.payload.request.MergeTableRequest;
import com.ng.payload.request.SplitBillRequest;

import java.util.List;

/**
 * Service for managing table operations in F&B/Restaurant
 */
public interface TableManagementService {

    /**
     * Change table for an active order
     * @param request Change table request
     * @return Updated order
     */
    OrderDTO changeTable(ChangeTableRequest request);

    /**
     * Merge multiple table orders into one
     * @param request Merge table request
     * @return Merged order
     */
    OrderDTO mergeTables(MergeTableRequest request);

    /**
     * Split a bill into multiple separate orders
     * @param request Split bill request
     * @return List of split orders
     */
    List<OrderDTO> splitBill(SplitBillRequest request);

    /**
     * Get active orders for a specific table
     * @param tableId Table ID
     * @return List of active orders
     */
    List<OrderDTO> getActiveOrdersByTable(Long tableId);
}
