package com.ng.mapper;

import com.ng.domain.BusinessType;
import com.ng.modal.Store;
import com.ng.modal.User;
import com.ng.payload.dto.StoreDTO;

public class StoreMapper {





        public static StoreDTO toDto(Store store) {
            if (store == null) {
                return null;
            }

            return StoreDTO.builder()
                    .id(store.getId())
                    .brand(store.getBrand())
                    .storeAdminId(store.getStoreAdmin() != null ? store.getStoreAdmin().getId() : null)
                    .storeAdmin(UserMapper.toDTO(store.getStoreAdmin()))
                    .storeType(store.getStoreType())
                    .businessType(store.getBusinessType())
                    .description(store.getDescription())
                    .contact(store.getContact())
                    .createdAt(store.getCreatedAt())
                    .updatedAt(store.getUpdatedAt())
                    .status(store.getStatus())
                    // ✅ Include total branch count (not the full list to avoid circular reference)
                    .totalBranches(store.getBranches() != null ? store.getBranches().size() : 0)
                    .build();
        }

        public static Store toEntity(StoreDTO dto, User storeAdmin) {
            return Store.builder()
                    .id(dto.getId())
                    .brand(dto.getBrand())
                    .storeAdmin(storeAdmin)
                    .createdAt(dto.getCreatedAt())
                    .updatedAt(dto.getUpdatedAt())
                    .storeType(dto.getStoreType())
                    .businessType(dto.getBusinessType() != null ? dto.getBusinessType() : BusinessType.RETAIL)
                    .description(dto.getDescription())
                    .build();
        }
    }


