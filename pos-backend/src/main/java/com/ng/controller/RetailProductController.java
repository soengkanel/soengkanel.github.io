package com.ng.controller;

import com.ng.modal.RetailProduct;
import com.ng.payload.dto.RetailProductDTO;
import com.ng.payload.request.RetailProductRequest;
import com.ng.service.RetailProductService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/retail-products")
@RequiredArgsConstructor
public class RetailProductController {

    private final RetailProductService retailProductService;

    /**
     * Create a new retail product
     */
    @PostMapping
    public ResponseEntity<RetailProductDTO> createRetailProduct(
            @Valid @RequestBody RetailProductRequest request,
            @RequestParam Long storeId) {

        RetailProductDTO dto = mapRequestToDTO(request);
        RetailProduct product = retailProductService.createRetailProduct(dto, storeId);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(retailProductService.convertToDTO(product));
    }

    /**
     * Update an existing retail product
     */
    @PutMapping("/{id}")
    public ResponseEntity<RetailProductDTO> updateRetailProduct(
            @PathVariable Long id,
            @Valid @RequestBody RetailProductRequest request) {

        RetailProductDTO dto = mapRequestToDTO(request);
        RetailProduct product = retailProductService.updateRetailProduct(id, dto);
        return ResponseEntity.ok(retailProductService.convertToDTO(product));
    }

    /**
     * Get retail product by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<RetailProductDTO> getRetailProductById(@PathVariable Long id) {
        RetailProduct product = retailProductService.getRetailProductById(id);
        return ResponseEntity.ok(retailProductService.convertToDTO(product));
    }

    /**
     * Get all retail products for a store
     */
    @GetMapping
    public ResponseEntity<List<RetailProductDTO>> getRetailProductsByStore(@RequestParam Long storeId) {
        List<RetailProduct> products = retailProductService.getRetailProductsByStore(storeId);
        List<RetailProductDTO> dtos = products.stream()
                .map(retailProductService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Search retail products by keyword
     */
    @GetMapping("/search")
    public ResponseEntity<List<RetailProductDTO>> searchRetailProducts(
            @RequestParam Long storeId,
            @RequestParam String keyword) {

        List<RetailProduct> products = retailProductService.searchRetailProducts(storeId, keyword);
        List<RetailProductDTO> dtos = products.stream()
                .map(retailProductService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Get retail product by barcode
     */
    @GetMapping("/barcode/{barcode}")
    public ResponseEntity<RetailProductDTO> getRetailProductByBarcode(@PathVariable String barcode) {
        RetailProduct product = retailProductService.getRetailProductByBarcode(barcode);
        return ResponseEntity.ok(retailProductService.convertToDTO(product));
    }

    /**
     * Get low stock retail products
     */
    @GetMapping("/low-stock")
    public ResponseEntity<List<RetailProductDTO>> getLowStockProducts(@RequestParam Long storeId) {
        List<RetailProduct> products = retailProductService.getLowStockProducts(storeId);
        List<RetailProductDTO> dtos = products.stream()
                .map(retailProductService::convertToDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }

    /**
     * Delete retail product
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRetailProduct(@PathVariable Long id) {
        retailProductService.deleteRetailProduct(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Helper method to map request to DTO
     */
    private RetailProductDTO mapRequestToDTO(RetailProductRequest request) {
        return RetailProductDTO.builder()
                .name(request.getName())
                .sku(request.getSku())
                .description(request.getDescription())
                .mrp(request.getMrp())
                .sellingPrice(request.getSellingPrice())
                .brand(request.getBrand())
                .barcode(request.getBarcode())
                .manufacturer(request.getManufacturer())
                .warranty(request.getWarranty())
                .weight(request.getWeight())
                .dimensions(request.getDimensions())
                .reorderLevel(request.getReorderLevel())
                .maxStockLevel(request.getMaxStockLevel())
                .hsnCode(request.getHsnCode())
                .taxRate(request.getTaxRate())
                .modelNumber(request.getModelNumber())
                .color(request.getColor())
                .size(request.getSize())
                .material(request.getMaterial())
                .hasExpiry(request.getHasExpiry())
                .shelfLifeDays(request.getShelfLifeDays())
                .image(request.getImage())
                .categoryId(request.getCategoryId())
                .build();
    }
}
