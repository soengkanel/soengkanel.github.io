package com.ng.service.impl;


import com.ng.domain.BusinessType;
import com.ng.domain.StoreStatus;
import com.ng.domain.UserRole;
import com.ng.exception.ResourceNotFoundException;
import com.ng.exception.UserException;
import com.ng.mapper.StoreMapper;
import com.ng.mapper.UserMapper;
import com.ng.modal.Branch;
import com.ng.modal.Store;
import com.ng.modal.StoreContact;
import com.ng.modal.User;
import com.ng.payload.dto.StoreDTO;
import com.ng.payload.dto.UserDTO;
import com.ng.repository.BranchRepository;
import com.ng.repository.StoreRepository;
import com.ng.repository.UserRepository;
import com.ng.service.FnbInitializationService;
import com.ng.service.StoreService;

import com.ng.service.UserService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class StoreServiceImpl implements StoreService {

    private final StoreRepository storeRepository;
    private final UserService userService;
    private final BranchRepository branchRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final FnbInitializationService fnbInitializationService;


    @Override
    public StoreDTO createStore(StoreDTO storeDto, User user) {

        System.out.println(storeDto);

        Store store = StoreMapper.toEntity(storeDto, user);
        Store savedStore = storeRepository.save(store);

        // Initialize F&B sample data if business type is FNB or HYBRID
        if (savedStore.getBusinessType() == BusinessType.FNB ||
            savedStore.getBusinessType() == BusinessType.HYBRID) {

            // Get the main branch if it exists, or pass null to create one
            Branch mainBranch = branchRepository.findByStoreId(savedStore.getId())
                    .stream()
                    .findFirst()
                    .orElse(null);

            fnbInitializationService.initializeFnbSampleData(savedStore, mainBranch);
        }

        return StoreMapper.toDto(savedStore);
    }

    @Override
    public StoreDTO getStoreById(Long id) throws ResourceNotFoundException {
        Store store = storeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Store not found"));
        return StoreMapper.toDto(store);
    }

    @Override
    public List<StoreDTO> getAllStores(StoreStatus status) {
        List<Store> stores;
        if (status != null) {
            stores = storeRepository.findByStatus(status);
        } else {
            stores = storeRepository.findAll();
        }

        return stores.stream()
                .map(StoreMapper::toDto)
                .collect(Collectors.toList());


    }

    @Override
    public Store getStoreByAdminId() throws UserException {
        User currentUser=userService.getCurrentUser();
        return storeRepository.findByStoreAdminId(
                currentUser.getId()
        );
    }

    @Override
    public StoreDTO getStoreByEmployee() throws UserException {
        User currentUser=userService.getCurrentUser();


        if(currentUser.getStore()==null){
            throw new UserException("user does not have enough permissions to access this store");
        }
        return StoreMapper.toDto(currentUser.getStore());
    }

    @Override
    public StoreDTO updateStore(Long id, StoreDTO storeDto) throws ResourceNotFoundException, UserException {
        User currentUser=userService.getCurrentUser();
        Store existing = storeRepository.findByStoreAdminId(currentUser.getId());

        if(existing == null) {
            throw new ResourceNotFoundException("store not found");
        }

        existing.setBrand(storeDto.getBrand());
        existing.setDescription(storeDto.getDescription());

        // Convert string storeType to enum, if not null
        if (storeDto.getStoreType() != null) {
            existing.setStoreType(storeDto.getStoreType());
        }

        // Set contact info if provided
        if (storeDto.getContact() != null) {
            StoreContact contact = StoreContact.builder()
                    .address(storeDto.getContact().getAddress())
                    .phone(storeDto.getContact().getPhone())
                    .email(storeDto.getContact().getEmail())
                    .build();
            existing.setContact(contact);
        }

        return StoreMapper.toDto(storeRepository.save(existing));
    }

    @Override
    public void deleteStore() throws ResourceNotFoundException, UserException {
        Store store= getStoreByAdminId();

        if (store==null) {
            throw new ResourceNotFoundException("Store not found");
        }
        storeRepository.deleteById(store.getId());
    }

    @Override
    public UserDTO addEmployee(Long id, UserDTO userDto) throws UserException {
        Store store=getStoreByAdminId();

        User employee = UserMapper.toEntity(userDto);
        if(userDto.getRole()== UserRole.ROLE_STORE_MANAGER){
            employee.setStore(store);
        }else if(userDto.getRole()== UserRole.ROLE_BRANCH_MANAGER){
            Branch branch=branchRepository.findById(userDto.getBranchId()).orElseThrow(
                    ()-> new EntityNotFoundException("branch not found")
            );
            employee.setBranch(branch);
            employee.setStore(store);
        }

        employee.setPassword(passwordEncoder.encode(userDto.getPassword()));
        User addedEmployee=userRepository.save(employee);

        return UserMapper.toDTO(addedEmployee);
    }

    @Override
    public List<UserDTO> getEmployeesByStore(Long storeId) throws UserException {
        User currentUser=userService.getCurrentUser();

        Store store=storeRepository.findById(storeId).orElseThrow(
                ()->new EntityNotFoundException("store not found")
        );
        if(store.getStoreAdmin().getId().equals(currentUser.getId())
                || currentUser.getStore().getId().equals(store.getId())){
            List<User> employees=userRepository.findByStoreId(storeId);
            return UserMapper.toDTOList(employees);
        }

        throw new UserException("user does not have enough permissions to access this store");
    }


    @Override
    public StoreDTO moderateStore(Long storeId, StoreStatus action) throws ResourceNotFoundException {
        Store store = storeRepository.findById(storeId)
                .orElseThrow(() -> new ResourceNotFoundException("Store not found with id: " + storeId));

      store.setStatus(action);
        Store updatedStore = storeRepository.save(store);
        return StoreMapper.toDto(updatedStore);
    }


}
