package com.ng.service.impl;


import com.ng.domain.ProductType;
import com.ng.exception.UserException;
import com.ng.mapper.InventoryMapper;
import com.ng.modal.*;
import com.ng.payload.dto.InventoryDTO;
import com.ng.repository.*;
import com.ng.util.SecurityUtil;
import com.ng.service.InventoryService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.nio.file.AccessDeniedException;
import java.util.List;
import java.util.stream.Collectors;

@RequiredArgsConstructor
@Service
public class InventoryServiceImpl implements InventoryService {

    private final InventoryRepository inventoryRepository;
    private final BranchRepository branchRepository;
    private final RetailProductRepository retailProductRepository;
    private final MenuItemRepository menuItemRepository;
    private final SecurityUtil securityUtil;

    @Override
    public InventoryDTO createInventory(InventoryDTO dto) throws AccessDeniedException, UserException {
        Branch branch = branchRepository.findById(dto.getBranchId())
                .orElseThrow(() -> new EntityNotFoundException("Branch not found"));

        // Determine product type (default to RETAIL if not specified)
        ProductType productType = dto.getProductType() != null ? dto.getProductType() : ProductType.RETAIL;

        String productName;
        String productSku;

        // Fetch product details based on type
        if (productType == ProductType.RETAIL) {
            RetailProduct retailProduct = retailProductRepository.findById(dto.getProductId())
                    .orElseThrow(() -> new EntityNotFoundException("Retail product not found"));
            productName = retailProduct.getName();
            productSku = retailProduct.getSku();
        } else {
            MenuItem menuItem = menuItemRepository.findById(dto.getProductId())
                    .orElseThrow(() -> new EntityNotFoundException("Menu item not found"));
            productName = menuItem.getName();
            productSku = menuItem.getSku();
        }

//        securityUtil.checkAuthority(branch);

        Inventory inventory = InventoryMapper.toEntity(dto, branch, dto.getProductId(), productType, productName, productSku);
        return InventoryMapper.toDto(inventoryRepository.save(inventory));
    }

    @Override
    public InventoryDTO updateInventory(Long id, InventoryDTO dto) throws AccessDeniedException, UserException {
        Inventory inventory = inventoryRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Inventory not found"));

//        securityUtil.checkAuthority(inventory);

        inventory.setQuantity(dto.getQuantity());
        return InventoryMapper.toDto(inventoryRepository.save(inventory));
    }

    @Override
    public void deleteInventory(Long id) throws AccessDeniedException, UserException {
        Inventory inventory = inventoryRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Inventory not found"));

        securityUtil.checkAuthority(inventory);

        inventoryRepository.delete(inventory);
    }

    @Override
    public InventoryDTO getInventoryById(Long id) {
        Inventory inventory = inventoryRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Inventory not found"));

        return InventoryMapper.toDto(inventory);
    }

    @Override
    public List<InventoryDTO> getInventoryByBranch(Long branchId) {
        return inventoryRepository.findByBranchId(branchId)
                .stream()
                .map(InventoryMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public InventoryDTO getInventoryByProductId(Long productId) {
        return InventoryMapper.toDto(inventoryRepository.findByProductId(productId));
    }
}

