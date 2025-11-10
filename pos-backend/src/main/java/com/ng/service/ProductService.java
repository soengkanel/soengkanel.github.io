package com.ng.service;


import com.ng.exception.AccessDeniedException;
import com.ng.modal.User;
import com.ng.payload.dto.ProductDTO;

import java.util.List;

public interface ProductService {
    ProductDTO createProduct(ProductDTO productDto, User user) throws AccessDeniedException;
    ProductDTO getProductById(Long id);

    ProductDTO updateProduct(Long id, ProductDTO productDto, User user) throws AccessDeniedException;
    void deleteProduct(Long id, User user) throws AccessDeniedException;

    List<ProductDTO> getProductsByStoreId(Long storeId);

    List<ProductDTO> searchByKeyword(Long storeId, String query);



}
