package com.ng.service;


import com.ng.exception.UserException;
import com.ng.modal.User;
import com.ng.payload.dto.BranchDTO;

import java.util.List;

public interface BranchService {
    BranchDTO createBranch(BranchDTO branchDto, User user);
    BranchDTO getBranchById(Long id);
    List<BranchDTO> getAllBranchesByStoreId(Long storeId) throws UserException;
    BranchDTO updateBranch(Long id, BranchDTO branchDto, User user) throws Exception;

    void deleteBranch(Long id);
}

