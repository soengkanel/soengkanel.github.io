package com.ng.service.impl;


import com.ng.domain.UserRole;
import com.ng.exception.UserException;
import com.ng.mapper.BranchMapper;
import com.ng.modal.Branch;
import com.ng.modal.Store;
import com.ng.modal.User;
import com.ng.payload.dto.BranchDTO;
import com.ng.repository.BranchRepository;
import com.ng.repository.StoreRepository;
import com.ng.repository.UserRepository;
import com.ng.service.BranchService;
import com.ng.service.UserService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class BranchServiceImpl implements BranchService {

    private final BranchRepository branchRepository;
    private final StoreRepository storeRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    private final UserService userService;

    @Override
    public BranchDTO createBranch(BranchDTO branchDto, User user) {
        Store store = storeRepository.findByStoreAdminId(user.getId());

        Branch branch = BranchMapper.toEntity(branchDto, store);

        // CRITICAL: Auto-set businessType from store
        // This ensures branch always has the same business type as parent store
        if (store != null) {
            branch.setBusinessType(store.getBusinessType());
        }

        return BranchMapper.toDto(branchRepository.save(branch));
    }

    @Override
    public BranchDTO getBranchById(Long id) {
        Branch branch = branchRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Branch not found"));
        return BranchMapper.toDto(branch);
    }

    @Override
    public List<BranchDTO> getAllBranchesByStoreId(Long storeId) throws UserException {
        User currentUser=userService.getCurrentUser();
        Store store=storeRepository.findById(storeId).orElseThrow(
                () -> new EntityNotFoundException("Store not found")
        );

        // Check if current user is allowed
        boolean isStoreManager = currentUser.getRole() == UserRole.ROLE_STORE_MANAGER &&
                currentUser.getStore() != null &&
                currentUser.getStore().getId().equals(storeId);

        boolean isStoreAdmin = currentUser.getRole() == UserRole.ROLE_STORE_ADMIN &&
                store.getStoreAdmin() != null &&
                store.getStoreAdmin().getId().equals(currentUser.getId());

        if (!isStoreManager && !isStoreAdmin) {
            throw new UserException("You are not authorized to access this store's branches");
        }

        return branchRepository.findByStoreId(store.getId()).stream()
                .map(BranchMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public BranchDTO updateBranch(Long id, BranchDTO branchDto, User user) throws Exception {

//        Store store = storeRepository.findByStoreAdminId(user.getId());

        Branch existing = branchRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Branch not found"));

//        if(!store.getId().equals(existing.getStore().getId())){
//            throw new Exception("can't have permission");
//        }

        existing.setName(branchDto.getName());
        existing.setAddress(branchDto.getAddress());
        existing.setEmail(branchDto.getEmail());
        existing.setPhone(branchDto.getPhone());
        existing.setCloseTime(branchDto.getCloseTime());
        existing.setOpenTime(branchDto.getOpenTime());
        existing.setWorkingDays(branchDto.getWorkingDays());

        return BranchMapper.toDto(branchRepository.save(existing));
    }

    @Override
    public void deleteBranch(Long id) {
        if (!branchRepository.existsById(id)) {
            throw new EntityNotFoundException("Branch not found");
        }
        branchRepository.deleteById(id);
    }
}
