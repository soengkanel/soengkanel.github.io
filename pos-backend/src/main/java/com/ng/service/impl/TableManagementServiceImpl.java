package com.ng.service.impl;

import com.ng.domain.OrderStatus;
import com.ng.domain.TableStatus;
import com.ng.mapper.OrderMapper;
import com.ng.modal.Order;
import com.ng.modal.OrderItem;
import com.ng.modal.TableLayout;
import com.ng.payload.dto.OrderDTO;
import com.ng.payload.request.ChangeTableRequest;
import com.ng.payload.request.MergeTableRequest;
import com.ng.payload.request.SplitBillRequest;
import com.ng.repository.OrderItemRepository;
import com.ng.repository.OrderRepository;
import com.ng.repository.TableLayoutRepository;
import com.ng.service.TableManagementService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TableManagementServiceImpl implements TableManagementService {

    private final OrderRepository orderRepository;
    private final TableLayoutRepository tableLayoutRepository;
    private final OrderItemRepository orderItemRepository;

    @Override
    @Transactional
    public OrderDTO changeTable(ChangeTableRequest request) {
        // Fetch the order
        Order order = orderRepository.findById(request.getOrderId())
                .orElseThrow(() -> new RuntimeException("Order not found"));

        // Validate order is not completed
        if (order.getStatus() == OrderStatus.COMPLETED) {
            throw new RuntimeException("Cannot change table for completed order");
        }

        // Fetch old and new tables
        TableLayout oldTable = order.getTable();
        TableLayout newTable = tableLayoutRepository.findById(request.getNewTableId())
                .orElseThrow(() -> new RuntimeException("New table not found"));

        // Validate new table is available
        if (newTable.getStatus() != TableStatus.AVAILABLE) {
            throw new RuntimeException("New table is not available");
        }

        // Update old table status
        if (oldTable != null) {
            oldTable.setStatus(TableStatus.AVAILABLE);
            oldTable.setCurrentOrder(null);
            oldTable.setOccupiedAt(null);
            tableLayoutRepository.save(oldTable);
        }

        // Update new table status
        newTable.setStatus(TableStatus.OCCUPIED);
        newTable.setCurrentOrder(order);
        newTable.setOccupiedAt(LocalDateTime.now());
        tableLayoutRepository.save(newTable);

        // Update order with new table
        order.setTable(newTable);
        order = orderRepository.save(order);

        return OrderMapper.toDto(order);
    }

    @Override
    @Transactional
    public OrderDTO mergeTables(MergeTableRequest request) {
        // Fetch all source orders
        List<Order> sourceOrders = new ArrayList<>();
        for (Long orderId : request.getSourceOrderIds()) {
            Order order = orderRepository.findById(orderId)
                    .orElseThrow(() -> new RuntimeException("Order not found: " + orderId));

            // Validate order is not completed
            if (order.getStatus() == OrderStatus.COMPLETED) {
                throw new RuntimeException("Cannot merge completed order: " + orderId);
            }
            sourceOrders.add(order);
        }

        if (sourceOrders.isEmpty()) {
            throw new RuntimeException("No orders to merge");
        }

        // Fetch target table
        TableLayout targetTable = tableLayoutRepository.findById(request.getTargetTableId())
                .orElseThrow(() -> new RuntimeException("Target table not found"));

        // Create merged order or use first order as base
        Order mergedOrder = sourceOrders.get(0);
        mergedOrder.setTable(targetTable);

        // Collect all items from source orders
        List<OrderItem> allItems = new ArrayList<>();
        double totalSubtotal = 0.0;
        double totalDiscount = 0.0;
        double totalTax = 0.0;

        for (Order sourceOrder : sourceOrders) {
            // Add items to merged order
            for (OrderItem item : sourceOrder.getItems()) {
                item.setOrder(mergedOrder);
                allItems.add(item);
            }

            // Accumulate totals
            totalSubtotal += sourceOrder.getSubtotal() != null ? sourceOrder.getSubtotal() : 0.0;
            totalDiscount += sourceOrder.getDiscountAmount() != null ? sourceOrder.getDiscountAmount() : 0.0;
            totalTax += sourceOrder.getTaxAmount() != null ? sourceOrder.getTaxAmount() : 0.0;

            // Mark old tables as available (except the target)
            if (!sourceOrder.equals(mergedOrder) && sourceOrder.getTable() != null) {
                TableLayout oldTable = sourceOrder.getTable();
                oldTable.setStatus(TableStatus.AVAILABLE);
                oldTable.setCurrentOrder(null);
                oldTable.setOccupiedAt(null);
                tableLayoutRepository.save(oldTable);

                // Delete the source order (items already moved)
                sourceOrder.getItems().clear();
                orderRepository.delete(sourceOrder);
            }
        }

        // Update merged order
        mergedOrder.setItems(allItems);
        mergedOrder.setSubtotal(totalSubtotal);
        mergedOrder.setDiscountAmount(totalDiscount);
        mergedOrder.setTaxAmount(totalTax);
        mergedOrder.setTotalAmount(totalSubtotal - totalDiscount + totalTax);

        // Update target table
        targetTable.setStatus(TableStatus.OCCUPIED);
        targetTable.setCurrentOrder(mergedOrder);
        targetTable.setOccupiedAt(LocalDateTime.now());
        tableLayoutRepository.save(targetTable);

        mergedOrder = orderRepository.save(mergedOrder);

        return OrderMapper.toDto(mergedOrder);
    }

    @Override
    @Transactional
    public List<OrderDTO> splitBill(SplitBillRequest request) {
        // Fetch original order
        Order originalOrder = orderRepository.findById(request.getOriginalOrderId())
                .orElseThrow(() -> new RuntimeException("Original order not found"));

        // Validate order is not completed
        if (originalOrder.getStatus() == OrderStatus.COMPLETED) {
            throw new RuntimeException("Cannot split completed order");
        }

        List<OrderDTO> splitOrders = new ArrayList<>();
        int splitNumber = 1;

        // Mark original order as split
        originalOrder.setIsSplit(true);

        for (SplitBillRequest.SplitGroup group : request.getSplitGroups()) {
            // Create new split order
            Order splitOrder = Order.builder()
                    .branch(originalOrder.getBranch())
                    .cashier(originalOrder.getCashier())
                    .customer(group.getCustomerId() != null
                            ? findCustomerById(group.getCustomerId())
                            : originalOrder.getCustomer())
                    .table(originalOrder.getTable())
                    .orderType(originalOrder.getOrderType())
                    .parentOrderId(originalOrder.getId())
                    .isSplit(true)
                    .splitNumber(splitNumber++)
                    .status(OrderStatus.PENDING)
                    .paymentType(originalOrder.getPaymentType())
                    .build();

            // Move items to split order
            List<OrderItem> splitItems = new ArrayList<>();
            double splitSubtotal = 0.0;

            for (Long itemId : group.getOrderItemIds()) {
                OrderItem item = originalOrder.getItems().stream()
                        .filter(i -> i.getId().equals(itemId))
                        .findFirst()
                        .orElseThrow(() -> new RuntimeException("Order item not found: " + itemId));

                // Create copy of item for split order
                OrderItem newItem = OrderItem.builder()
                        .productId(item.getProductId())
                        .productType(item.getProductType())
                        .productName(item.getProductName())
                        .productSku(item.getProductSku())
                        .quantity(item.getQuantity())
                        .price(item.getPrice())
                        .discountType(item.getDiscountType())
                        .discountValue(item.getDiscountValue())
                        .discountAmount(item.getDiscountAmount())
                        .discountReason(item.getDiscountReason())
                        .specialInstructions(item.getSpecialInstructions())
                        .order(splitOrder)
                        .build();

                splitItems.add(newItem);
                splitSubtotal += newItem.getTotalPrice();
            }

            splitOrder.setItems(splitItems);
            splitOrder.setSubtotal(splitSubtotal);
            splitOrder.setTotalAmount(splitSubtotal); // Can apply tax/discount later

            splitOrder = orderRepository.save(splitOrder);
            splitOrders.add(OrderMapper.toDto(splitOrder));
        }

        // Mark original order as completed/archived
        originalOrder.setStatus(OrderStatus.COMPLETED);
        orderRepository.save(originalOrder);

        return splitOrders;
    }

    @Override
    public List<OrderDTO> getActiveOrdersByTable(Long tableId) {
        TableLayout table = tableLayoutRepository.findById(tableId)
                .orElseThrow(() -> new RuntimeException("Table not found"));

        return orderRepository.findByTableAndStatus(table, OrderStatus.PENDING)
                .stream()
                .map(OrderMapper::toDto)
                .collect(Collectors.toList());
    }

    // Helper method - implement based on your customer repository
    private com.ng.modal.Customer findCustomerById(Long customerId) {
        // TODO: Implement customer lookup
        return null;
    }
}
