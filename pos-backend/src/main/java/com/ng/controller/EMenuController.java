package com.ng.controller;

import com.ng.payload.dto.MenuItemDTO;
import com.ng.payload.dto.OrderDTO;
import com.ng.payload.dto.TableInfoDTO;
import com.ng.payload.request.EMenuOrderRequest;
import com.ng.service.EMenuService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controller for customer-facing eMenu functionality (QR code access)
 * These endpoints are publicly accessible and don't require authentication
 */
@RestController
@RequestMapping("/api/emenu")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // Allow access from any origin for QR code scanning
public class EMenuController {

    private final EMenuService eMenuService;

    /**
     * Get menu items for a branch (public access)
     */
    @GetMapping("/menu/{branchId}")
    public ResponseEntity<List<MenuItemDTO>> getMenu(@PathVariable Long branchId) {
        List<MenuItemDTO> menu = eMenuService.getMenuForBranch(branchId);
        return ResponseEntity.ok(menu);
    }

    /**
     * Get menu items by category
     */
    @GetMapping("/menu/{branchId}/category/{categoryId}")
    public ResponseEntity<List<MenuItemDTO>> getMenuByCategory(
            @PathVariable Long branchId,
            @PathVariable Long categoryId) {
        List<MenuItemDTO> menu = eMenuService.getMenuByCategory(branchId, categoryId);
        return ResponseEntity.ok(menu);
    }

    /**
     * Get table information (validate QR code access)
     */
    @GetMapping("/table")
    public ResponseEntity<TableInfoDTO> getTableInfo(
            @RequestParam Long branchId,
            @RequestParam Long tableId,
            @RequestParam String token) {
        try {
            TableInfoDTO tableInfo = eMenuService.getTableInfo(branchId, tableId, token);
            return ResponseEntity.ok(tableInfo);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }

    /**
     * Place order from eMenu
     */
    @PostMapping("/order")
    public ResponseEntity<OrderDTO> placeOrder(@Valid @RequestBody EMenuOrderRequest request) {
        try {
            OrderDTO order = eMenuService.placeEMenuOrder(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(order);
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Get all orders for a table (for customers to see their orders)
     */
    @GetMapping("/orders/table/{tableId}")
    public ResponseEntity<List<OrderDTO>> getTableOrders(@PathVariable Long tableId) {
        List<OrderDTO> orders = eMenuService.getTableOrders(tableId);
        return ResponseEntity.ok(orders);
    }

    /**
     * Generate QR code for a table (staff use)
     * This endpoint should be secured in production
     */
    @GetMapping("/qr-code/table/{tableId}")
    public ResponseEntity<byte[]> generateTableQRCode(@PathVariable Long tableId) {
        try {
            byte[] qrCode = eMenuService.generateTableQRCode(tableId);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.IMAGE_PNG);
            headers.setContentLength(qrCode.length);
            return new ResponseEntity<>(qrCode, headers, HttpStatus.OK);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Regenerate QR code token for a table (staff use)
     * This endpoint should be secured in production
     */
    @PostMapping("/qr-code/table/{tableId}/regenerate")
    public ResponseEntity<String> regenerateTableToken(@PathVariable Long tableId) {
        try {
            String newToken = eMenuService.regenerateTableToken(tableId);
            return ResponseEntity.ok(newToken);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
}
