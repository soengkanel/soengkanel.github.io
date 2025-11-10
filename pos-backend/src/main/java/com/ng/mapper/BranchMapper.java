package com.ng.mapper;


import com.ng.modal.Branch;
import com.ng.modal.Store;
import com.ng.payload.dto.BranchDTO;

public class BranchMapper {

    public static BranchDTO toDto(Branch branch) {
        return BranchDTO.builder()
                .id(branch.getId())
                .name(branch.getName())
                .address(branch.getAddress())
                .phone(branch.getPhone())
                .email(branch.getEmail())
                .closeTime(branch.getCloseTime())
                .openTime(branch.getOpenTime())
                .workingDays(branch.getWorkingDays())
                .storeId(branch.getStore() != null ? branch.getStore().getId() : null)
                .store(StoreMapper.toDto(branch.getStore()))
                .businessType(branch.getBusinessType()) // ✅ Include businessType
                .managerId(branch.getManager() != null ? branch.getManager().getId() : null)
                .createdAt(branch.getCreatedAt())
                .updatedAt(branch.getUpdatedAt())
                .manager(branch.getManager()!=null?
                        branch.getManager().getFullName():null)
                .build();
    }

    public static Branch toEntity(BranchDTO dto, Store store) {
        return Branch.builder()
                .id(dto.getId())
                .name(dto.getName())
                .address(dto.getAddress())
                .store(store)
                .email(dto.getEmail())
                .phone(dto.getPhone())
                .closeTime(dto.getCloseTime())
                .openTime(dto.getOpenTime())
                .workingDays(dto.getWorkingDays())
                // businessType will be auto-set from store in service layer
                .businessType(store != null ? store.getBusinessType() : null)
                .createdAt(dto.getCreatedAt())
                .updatedAt(dto.getUpdatedAt())
                .build();
    }
}
