package com.ng.service.impl;


import com.ng.domain.UserRole;
import com.ng.exception.AccessDeniedException;
import com.ng.mapper.ProductMapper;
import com.ng.modal.Category;
import com.ng.modal.Product;
import com.ng.modal.Store;
import com.ng.modal.User;
import com.ng.payload.dto.ProductDTO;
import com.ng.repository.CategoryRepository;
import com.ng.repository.ProductRepository;
import com.ng.repository.StoreRepository;
import com.ng.service.ProductService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProductServiceImpl implements ProductService {

    private final ProductRepository productRepository;
    private final StoreRepository storeRepository;
    private final CategoryRepository categoryRepository;

    @Override
    public ProductDTO createProduct(ProductDTO dto, User user) throws AccessDeniedException {
        Store store = storeRepository.findById(dto.getStoreId())
                .orElseThrow(() -> new EntityNotFoundException("Store not found"));

        checkAuthority(store, user);

        Category category = categoryRepository.findById(dto.getCategoryId())
                .orElseThrow(() -> new EntityNotFoundException("Category not found"));

        Product product = ProductMapper.toEntity(dto, store, category);
        return ProductMapper.toDto(productRepository.save(product));
    }

    @Override
    public ProductDTO getProductById(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Product not found"));
        return ProductMapper.toDto(product);
    }



    @Override
    public ProductDTO updateProduct(Long id, ProductDTO dto, User user) throws AccessDeniedException {
        Product existing = productRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Product not found"));

        Category category=categoryRepository.findById(dto.getCategoryId()).orElseThrow(
                () -> new EntityNotFoundException("Category not found")
        );

        checkAuthority(existing.getStore(),user);

        existing.setName(dto.getName());
        existing.setSku(dto.getSku());
        existing.setDescription(dto.getDescription());
        existing.setMrp(dto.getMrp());
        existing.setSellingPrice(dto.getSellingPrice());
        existing.setBrand(dto.getBrand());
        existing.setImage(dto.getImage());
        existing.setCategory(category);


        if (dto.getStoreId() != null) {
            Store store = storeRepository.findById(dto.getStoreId())
                    .orElseThrow(() -> new EntityNotFoundException("Store not found"));
            existing.setStore(store);
        }

        return ProductMapper.toDto(productRepository.save(existing));
    }

    @Override
    public void deleteProduct(Long id, User user) throws AccessDeniedException {
        Product product=productRepository.findById(id).orElseThrow(
                () -> new EntityNotFoundException("Product not found")
        );
       checkAuthority(product.getStore(),user);
        productRepository.deleteById(id);
    }

    @Override
    public List<ProductDTO> getProductsByStoreId(Long storeId) {
        return productRepository.findByStoreId(storeId)
                .stream()
                .map(ProductMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public List<ProductDTO> searchByKeyword(Long storeId , String query ) {
        return productRepository.searchByKeyword(storeId, query)
                .stream()
                .map(ProductMapper::toDto)
                .collect(Collectors.toList());
    }

    public void checkAuthority(Store store, User user) throws AccessDeniedException {

        if(user.getRole()==UserRole.ROLE_STORE_MANAGER
                && user.getStore().getId().equals(store.getId())){
            return;
        }

        if (user.getRole() == UserRole.ROLE_STORE_ADMIN
                && store.getStoreAdmin().getId().equals(user.getId())) {
            return;
        }

        throw new AccessDeniedException("You are not authorized to manage this store.");

    }



}

