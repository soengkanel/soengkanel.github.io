package com.ng.service;

import com.ng.payload.dto.MenuItemDTO;
import com.ng.payload.dto.OrderDTO;
import com.ng.payload.dto.TableInfoDTO;
import com.ng.payload.request.EMenuOrderRequest;

import java.util.List;

public interface EMenuService {

    /**
     * Get menu items for a branch (public access via QR code)
     */
    List<MenuItemDTO> getMenuForBranch(Long branchId);

    /**
     * Get menu items by category for a branch
     */
    List<MenuItemDTO> getMenuByCategory(Long branchId, Long categoryId);

    /**
     * Validate table token for QR code access
     */
    boolean validateTableToken(Long branchId, Long tableId, String token);

    /**
     * Place order from eMenu (customer-initiated)
     */
    OrderDTO placeEMenuOrder(EMenuOrderRequest request);

    /**
     * Get table details by token (for display on eMenu)
     */
    TableInfoDTO getTableInfo(Long branchId, Long tableId, String token);

    /**
     * Generate QR code for a table
     */
    byte[] generateTableQRCode(Long tableId) throws Exception;

    /**
     * Regenerate QR code token for a table
     */
    String regenerateTableToken(Long tableId);

    /**
     * Get all orders for a table (for customer to view their orders)
     */
    List<OrderDTO> getTableOrders(Long tableId);
}
