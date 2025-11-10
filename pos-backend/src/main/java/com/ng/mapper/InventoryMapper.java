package com.ng.mapper;


import com.ng.domain.ProductType;
import com.ng.modal.Branch;
import com.ng.modal.Inventory;
import com.ng.payload.dto.InventoryDTO;

public class InventoryMapper {

    public static InventoryDTO toDto(Inventory inventory) {
        return InventoryDTO.builder()
                .id(inventory.getId())
                .branchId(inventory.getBranch().getId())
                .productId(inventory.getProductId())
                .productType(inventory.getProductType())
                .productName(inventory.getProductName())
                .productSku(inventory.getProductSku())
                .quantity(inventory.getQuantity())
                .build();
    }

    public static Inventory toEntity(InventoryDTO dto, Branch branch, Long productId, ProductType productType, String productName, String productSku) {
        return Inventory.builder()
                .id(dto.getId())
                .branch(branch)
                .productId(productId)
                .productType(productType)
                .productName(productName)
                .productSku(productSku)
                .quantity(dto.getQuantity())
                .build();
    }
}

