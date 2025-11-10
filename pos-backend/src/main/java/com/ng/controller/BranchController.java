package com.ng.controller;
import com.ng.exception.UserException;
import com.ng.modal.User;
import com.ng.payload.dto.BranchDTO;
import com.ng.service.BranchService;
import com.ng.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/branches")
@RequiredArgsConstructor
public class BranchController {

    private final BranchService branchService;
    private final UserService userService;


    // 🔹 Create Branch
    @PostMapping
    public ResponseEntity<BranchDTO> createBranch(
            @Valid @RequestBody BranchDTO dto,

            @RequestHeader("Authorization") String jwt) throws UserException {
        User user = userService.getUserFromJwtToken(jwt);
        return ResponseEntity.ok(branchService.createBranch(dto,user));
    }

    // 🔹 Get Branch by ID
    @GetMapping("/{id}")
    public ResponseEntity<BranchDTO> getBranch(@PathVariable Long id) {
        return ResponseEntity.ok(branchService.getBranchById(id));
    }

    // 🔹 Get All Branches (No Pagination)
    @GetMapping("/store/{storeId}")
    public ResponseEntity<List<BranchDTO>> getAllBranches(
            @RequestHeader("Authorization") String jwt,
            @PathVariable Long storeId
    ) throws UserException {
        User user=userService.getUserFromJwtToken(jwt);
        return ResponseEntity.ok(branchService.getAllBranchesByStoreId(storeId));
    }

    // 🔹 Update Branch
    @PutMapping("/{id}")
    public ResponseEntity<BranchDTO> updateBranch(
            @PathVariable Long id,
            @RequestBody BranchDTO dto,
            @RequestHeader("Authorization") String jwt) throws Exception {
        User user=userService.getUserFromJwtToken(jwt);
        return ResponseEntity.ok(branchService.updateBranch(id, dto, user));
    }

    // 🔹 Delete Branch
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBranch(@PathVariable Long id) {
        branchService.deleteBranch(id);
        return ResponseEntity.noContent().build();
    }


}
