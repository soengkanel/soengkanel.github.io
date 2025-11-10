package com.ng.service.impl;

import com.ng.exception.ResourceNotFoundException;
import com.ng.modal.Category;
import com.ng.modal.RetailProduct;
import com.ng.modal.Store;
import com.ng.payload.dto.RetailProductDTO;
import com.ng.repository.CategoryRepository;
import com.ng.repository.RetailProductRepository;
import com.ng.repository.StoreRepository;
import com.ng.service.RetailProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RetailProductServiceImpl implements RetailProductService {

    private final RetailProductRepository retailProductRepository;
    private final StoreRepository storeRepository;
    private final CategoryRepository categoryRepository;

    @Override
    @Transactional
    public RetailProduct createRetailProduct(RetailProductDTO productDTO, Long storeId) {
        Store store = storeRepository.findById(storeId)
                .orElseThrow(() -> new ResourceNotFoundException("Store not found"));

        Category category = null;
        if (productDTO.getCategoryId() != null) {
            category = categoryRepository.findById(productDTO.getCategoryId())
                    .orElseThrow(() -> new ResourceNotFoundException("Category not found"));
        }

        RetailProduct product = RetailProduct.builder()
                .name(productDTO.getName())
                .sku(productDTO.getSku())
                .description(productDTO.getDescription())
                .mrp(productDTO.getMrp())
                .sellingPrice(productDTO.getSellingPrice())
                .brand(productDTO.getBrand())
                .barcode(productDTO.getBarcode())
                .manufacturer(productDTO.getManufacturer())
                .warranty(productDTO.getWarranty())
                .weight(productDTO.getWeight())
                .dimensions(productDTO.getDimensions())
                .reorderLevel(productDTO.getReorderLevel())
                .maxStockLevel(productDTO.getMaxStockLevel())
                .hsnCode(productDTO.getHsnCode())
                .taxRate(productDTO.getTaxRate())
                .modelNumber(productDTO.getModelNumber())
                .color(productDTO.getColor())
                .size(productDTO.getSize())
                .material(productDTO.getMaterial())
                .hasExpiry(productDTO.getHasExpiry())
                .shelfLifeDays(productDTO.getShelfLifeDays())
                .image(productDTO.getImage())
                .category(category)
                .store(store)
                .build();

        return retailProductRepository.save(product);
    }

    @Override
    @Transactional
    public RetailProduct updateRetailProduct(Long productId, RetailProductDTO productDTO) {
        RetailProduct product = retailProductRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Retail product not found"));

        if (productDTO.getCategoryId() != null) {
            Category category = categoryRepository.findById(productDTO.getCategoryId())
                    .orElseThrow(() -> new ResourceNotFoundException("Category not found"));
            product.setCategory(category);
        }

        // Update fields
        product.setName(productDTO.getName());
        product.setSku(productDTO.getSku());
        product.setDescription(productDTO.getDescription());
        product.setMrp(productDTO.getMrp());
        product.setSellingPrice(productDTO.getSellingPrice());
        product.setBrand(productDTO.getBrand());
        product.setBarcode(productDTO.getBarcode());
        product.setManufacturer(productDTO.getManufacturer());
        product.setWarranty(productDTO.getWarranty());
        product.setWeight(productDTO.getWeight());
        product.setDimensions(productDTO.getDimensions());
        product.setReorderLevel(productDTO.getReorderLevel());
        product.setMaxStockLevel(productDTO.getMaxStockLevel());
        product.setHsnCode(productDTO.getHsnCode());
        product.setTaxRate(productDTO.getTaxRate());
        product.setModelNumber(productDTO.getModelNumber());
        product.setColor(productDTO.getColor());
        product.setSize(productDTO.getSize());
        product.setMaterial(productDTO.getMaterial());
        product.setHasExpiry(productDTO.getHasExpiry());
        product.setShelfLifeDays(productDTO.getShelfLifeDays());
        product.setImage(productDTO.getImage());

        return retailProductRepository.save(product);
    }

    @Override
    public RetailProduct getRetailProductById(Long id) {
        return retailProductRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Retail product not found"));
    }

    @Override
    public List<RetailProduct> getRetailProductsByStore(Long storeId) {
        return retailProductRepository.findByStoreId(storeId);
    }

    @Override
    public List<RetailProduct> searchRetailProducts(Long storeId, String keyword) {
        return retailProductRepository.searchByKeyword(storeId, keyword);
    }

    @Override
    public RetailProduct getRetailProductByBarcode(String barcode) {
        return retailProductRepository.findByBarcode(barcode)
                .orElseThrow(() -> new ResourceNotFoundException("Product with barcode not found"));
    }

    @Override
    public List<RetailProduct> getLowStockProducts(Long storeId) {
        return retailProductRepository.findLowStockProducts(storeId);
    }

    @Override
    @Transactional
    public void deleteRetailProduct(Long id) {
        RetailProduct product = getRetailProductById(id);
        retailProductRepository.delete(product);
    }

    @Override
    public RetailProductDTO convertToDTO(RetailProduct product) {
        return RetailProductDTO.builder()
                .id(product.getId())
                .name(product.getName())
                .sku(product.getSku())
                .description(product.getDescription())
                .mrp(product.getMrp())
                .sellingPrice(product.getSellingPrice())
                .brand(product.getBrand())
                .barcode(product.getBarcode())
                .manufacturer(product.getManufacturer())
                .warranty(product.getWarranty())
                .weight(product.getWeight())
                .dimensions(product.getDimensions())
                .reorderLevel(product.getReorderLevel())
                .maxStockLevel(product.getMaxStockLevel())
                .hsnCode(product.getHsnCode())
                .taxRate(product.getTaxRate())
                .modelNumber(product.getModelNumber())
                .color(product.getColor())
                .size(product.getSize())
                .material(product.getMaterial())
                .hasExpiry(product.getHasExpiry())
                .shelfLifeDays(product.getShelfLifeDays())
                .image(product.getImage())
                .categoryId(product.getCategory() != null ? product.getCategory().getId() : null)
                .categoryName(product.getCategory() != null ? product.getCategory().getName() : null)
                .storeId(product.getStore().getId())
                .createdAt(product.getCreatedAt())
                .updatedAt(product.getUpdatedAt())
                .build();
    }
}
