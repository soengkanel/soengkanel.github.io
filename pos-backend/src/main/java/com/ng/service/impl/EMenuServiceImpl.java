package com.ng.service.impl;

import com.ng.domain.OrderStatus;
import com.ng.domain.TableStatus;
import com.ng.modal.*;
import com.ng.payload.dto.MenuItemDTO;
import com.ng.payload.dto.OrderDTO;
import com.ng.payload.dto.TableInfoDTO;
import com.ng.payload.request.EMenuOrderRequest;
import com.ng.repository.*;
import com.ng.service.EMenuService;
import com.ng.util.QRCodeGenerator;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class EMenuServiceImpl implements EMenuService {

    private final MenuItemRepository menuItemRepository;
    private final TableLayoutRepository tableLayoutRepository;
    private final BranchRepository branchRepository;
    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final CustomerRepository customerRepository;
    private final QRCodeGenerator qrCodeGenerator;

    @Value("${app.emenu.base-url:http://localhost:5173}")
    private String baseUrl;

    @Override
    public List<MenuItemDTO> getMenuForBranch(Long branchId) {
        List<MenuItem> menuItems = menuItemRepository.findByBranchIdAndIsAvailableTrue(branchId);
        return menuItems.stream()
                .map(this::convertToMenuItemDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<MenuItemDTO> getMenuByCategory(Long branchId, Long categoryId) {
        List<MenuItem> menuItems = menuItemRepository
                .findByBranchIdAndCategoryIdAndIsAvailableTrue(branchId, categoryId);
        return menuItems.stream()
                .map(this::convertToMenuItemDTO)
                .collect(Collectors.toList());
    }

    @Override
    public boolean validateTableToken(Long branchId, Long tableId, String token) {
        TableLayout table = tableLayoutRepository.findById(tableId).orElse(null);
        if (table == null || !table.getBranch().getId().equals(branchId)) {
            return false;
        }
        return token != null && token.equals(table.getQrCode());
    }

    @Override
    @Transactional
    public OrderDTO placeEMenuOrder(EMenuOrderRequest request) {
        // Validate table token
        if (!validateTableToken(request.getBranchId(), request.getTableId(), request.getTableToken())) {
            throw new RuntimeException("Invalid table token");
        }

        // Get table and branch
        TableLayout table = tableLayoutRepository.findById(request.getTableId())
                .orElseThrow(() -> new RuntimeException("Table not found"));

        Branch branch = branchRepository.findById(request.getBranchId())
                .orElseThrow(() -> new RuntimeException("Branch not found"));

        // Create or get customer
        Customer customer = null;
        if (request.getCustomerPhone() != null && !request.getCustomerPhone().isEmpty()) {
            customer = customerRepository.findByPhone(request.getCustomerPhone())
                    .orElseGet(() -> {
                        Customer newCustomer = new Customer();
                        newCustomer.setFullName(request.getCustomerName() != null ?
                                request.getCustomerName() : "Guest");
                        newCustomer.setPhone(request.getCustomerPhone());
                        return customerRepository.save(newCustomer);
                    });
        }

        // Create order
        Order order = new Order();
        order.setBranch(branch);
        order.setTable(table);
        order.setCustomer(customer);
        order.setStatus(OrderStatus.PENDING);
        order.setOrderType("DINE_IN");
        order.setCreatedAt(LocalDateTime.now());

        // Calculate total and create order items
        double totalAmount = 0.0;
        List<OrderItem> orderItems = new ArrayList<>();

        for (EMenuOrderRequest.EMenuOrderItemRequest itemRequest : request.getItems()) {
            MenuItem menuItem = menuItemRepository.findById(itemRequest.getMenuItemId())
                    .orElseThrow(() -> new RuntimeException("Menu item not found: " + itemRequest.getMenuItemId()));

            if (!menuItem.getIsAvailable()) {
                throw new RuntimeException("Menu item not available: " + menuItem.getName());
            }

            OrderItem orderItem = new OrderItem();
            orderItem.setProduct(menuItem);
            orderItem.setQuantity(itemRequest.getQuantity());
            orderItem.setPrice(menuItem.getPrice());
            // Note: subtotal is calculated automatically via getSubtotal()

            if (itemRequest.getSpecialInstructions() != null) {
                orderItem.setNotes(itemRequest.getSpecialInstructions());
            }

            orderItems.add(orderItem);
            totalAmount += orderItem.getSubtotal();
        }

        order.setTotalAmount(totalAmount);
        order.setSubtotal(totalAmount);

        // Save order
        order = orderRepository.save(order);

        // Save order items
        for (OrderItem item : orderItems) {
            item.setOrder(order);
            orderItemRepository.save(item);
        }

        // Update table status
        if (table.getStatus() == TableStatus.AVAILABLE) {
            table.setStatus(TableStatus.OCCUPIED);
            table.setOccupiedAt(LocalDateTime.now());
            table.setCurrentOrder(order);
            tableLayoutRepository.save(table);
        }

        return convertToOrderDTO(order, orderItems);
    }

    @Override
    public TableInfoDTO getTableInfo(Long branchId, Long tableId, String token) {
        if (!validateTableToken(branchId, tableId, token)) {
            throw new RuntimeException("Invalid table token");
        }

        TableLayout table = tableLayoutRepository.findById(tableId)
                .orElseThrow(() -> new RuntimeException("Table not found"));

        Branch branch = table.getBranch();

        return TableInfoDTO.builder()
                .tableId(table.getId())
                .tableNumber(table.getTableNumber())
                .location(table.getLocation())
                .branchId(branch.getId())
                .branchName(branch.getName())
                .branchPhone(branch.getPhone())
                .branchAddress(branch.getAddress())
                .isActive(table.getIsActive())
                .build();
    }

    @Override
    public byte[] generateTableQRCode(Long tableId) throws Exception {
        TableLayout table = tableLayoutRepository.findById(tableId)
                .orElseThrow(() -> new RuntimeException("Table not found"));

        // Generate token if not exists
        if (table.getQrCode() == null || table.getQrCode().isEmpty()) {
            String token = qrCodeGenerator.generateTableToken(
                    table.getBranch().getId(),
                    table.getId()
            );
            table.setQrCode(token);
            tableLayoutRepository.save(table);
        }

        String menuUrl = qrCodeGenerator.generateMenuUrl(
                baseUrl,
                table.getBranch().getId(),
                table.getId(),
                table.getQrCode()
        );

        return qrCodeGenerator.generateQRCodeBytes(menuUrl);
    }

    @Override
    @Transactional
    public String regenerateTableToken(Long tableId) {
        TableLayout table = tableLayoutRepository.findById(tableId)
                .orElseThrow(() -> new RuntimeException("Table not found"));

        String newToken = qrCodeGenerator.generateTableToken(
                table.getBranch().getId(),
                table.getId()
        );

        table.setQrCode(newToken);
        tableLayoutRepository.save(table);

        return newToken;
    }

    @Override
    public List<OrderDTO> getTableOrders(Long tableId) {
        List<Order> orders = orderRepository.findByTableIdAndStatusNot(tableId, OrderStatus.CANCELLED);
        return orders.stream()
                .map(order -> convertToOrderDTO(order, order.getOrderItems()))
                .collect(Collectors.toList());
    }

    private MenuItemDTO convertToMenuItemDTO(MenuItem menuItem) {
        MenuItemDTO dto = new MenuItemDTO();
        dto.setId(menuItem.getId());
        dto.setName(menuItem.getName());
        dto.setDescription(menuItem.getDescription());
        dto.setPrice(menuItem.getPrice());
        dto.setCategoryId(menuItem.getCategory() != null ? menuItem.getCategory().getId() : null);
        dto.setCategoryName(menuItem.getCategory() != null ? menuItem.getCategory().getName() : null);
        dto.setImageUrl(menuItem.getImageUrl());
        dto.setIsAvailable(menuItem.getIsAvailable());
        dto.setSpiceLevel(menuItem.getSpiceLevel());
        dto.setCourseType(menuItem.getCourseType());
        dto.setIsVegetarian(menuItem.getIsVegetarian());
        dto.setIsVegan(menuItem.getIsVegan());
        dto.setAllergens(menuItem.getAllergens());
        dto.setPreparationTime(menuItem.getPreparationTime());
        return dto;
    }

    private OrderDTO convertToOrderDTO(Order order, List<OrderItem> items) {
        OrderDTO dto = new OrderDTO();
        dto.setId(order.getId());
        dto.setTotalAmount(order.getTotalAmount());
        dto.setBranchId(order.getBranch().getId());
        dto.setCustomer(order.getCustomer());
        dto.setStatus(order.getStatus());
        dto.setCreatedAt(order.getCreatedAt());
        // Note: You'll need to implement OrderItemDTO conversion
        return dto;
    }
}
