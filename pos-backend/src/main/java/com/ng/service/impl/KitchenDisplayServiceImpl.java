package com.ng.service.impl;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import com.ng.domain.OrderStatus;
import com.ng.domain.TableStatus;
import com.ng.modal.*;
import com.ng.payload.dto.KitchenOrderDTO;
import com.ng.payload.dto.KitchenOrderItemDTO;
import com.ng.payload.request.WaiterOrderRequest;
import com.ng.repository.*;
import com.ng.service.KitchenDisplayService;
import lombok.RequiredArgsConstructor;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class KitchenDisplayServiceImpl implements KitchenDisplayService {

    private final KitchenOrderRepository kitchenOrderRepository;
    private final OrderRepository orderRepository;
    private final MenuItemRepository menuItemRepository;
    private final BranchRepository branchRepository;
    private final TableLayoutRepository tableLayoutRepository;
    private final OrderItemRepository orderItemRepository;
    private final UserRepository userRepository;
    private final SimpMessagingTemplate messagingTemplate; // For WebSocket

    @Override
    @Transactional
    public void routeOrderToKitchen(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new RuntimeException("Order not found"));

        // Group order items by kitchen station
        Map<KitchenStation, List<OrderItem>> itemsByStation = new HashMap<>();

        for (OrderItem item : order.getOrderItems()) {
            if (item.getProduct() instanceof MenuItem) {
                MenuItem menuItem = (MenuItem) item.getProduct();
                KitchenStation station = menuItem.getKitchenStation();

                if (station != null) {
                    itemsByStation.computeIfAbsent(station, k -> new ArrayList<>()).add(item);
                }
            }
        }

        // Create kitchen order for each station
        for (Map.Entry<KitchenStation, List<OrderItem>> entry : itemsByStation.entrySet()) {
            KitchenStation station = entry.getKey();
            List<OrderItem> items = entry.getValue();

            KitchenOrder kitchenOrder = KitchenOrder.builder()
                    .order(order)
                    .kitchenStation(station)
                    .status(KitchenOrderStatus.PENDING)
                    .orderNumber(generateOrderNumber())
                    .tableNumber(order.getTable() != null ? order.getTable().getTableNumber() : "Takeout")
                    .priority(3)
                    .estimatedTime(calculateEstimatedTime(items))
                    .build();

            kitchenOrder = kitchenOrderRepository.save(kitchenOrder);

            // Create kitchen order items
            for (OrderItem orderItem : items) {
                KitchenOrderItem kitchenItem = new KitchenOrderItem();
                kitchenItem.setKitchenOrder(kitchenOrder);
                kitchenItem.setMenuItem((MenuItem) orderItem.getProduct());
                kitchenItem.setQuantity(orderItem.getQuantity());
                kitchenItem.setSpecialInstructions(orderItem.getNotes());
                kitchenOrder.getItems().add(kitchenItem);
            }

            kitchenOrder = kitchenOrderRepository.save(kitchenOrder);

            // Send real-time notification to specific kitchen station
            notifyKitchenStation(station, kitchenOrder);
        }
    }

    @Override
    public List<KitchenOrderDTO> getOrdersByStation(KitchenStation station, Long branchId) {
        List<KitchenOrder> orders = kitchenOrderRepository
                .findByKitchenStationAndOrderBranchIdAndStatusIn(
                        station,
                        branchId,
                        Arrays.asList(KitchenOrderStatus.PENDING, KitchenOrderStatus.PREPARING)
                );

        return orders.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<KitchenOrderDTO> getAllActiveOrders(Long branchId) {
        List<KitchenOrder> orders = kitchenOrderRepository
                .findByOrderBranchIdAndStatusNot(branchId, KitchenOrderStatus.COMPLETED);

        return orders.stream()
                .map(this::convertToDTO)
                .sorted(Comparator.comparing(KitchenOrderDTO::getPriority).reversed()
                        .thenComparing(KitchenOrderDTO::getCreatedAt))
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public KitchenOrderDTO startPreparation(Long kitchenOrderId) {
        KitchenOrder order = kitchenOrderRepository.findById(kitchenOrderId)
                .orElseThrow(() -> new RuntimeException("Kitchen order not found"));

        order.setStatus(KitchenOrderStatus.PREPARING);
        order.setPreparationStartedAt(LocalDateTime.now());
        order = kitchenOrderRepository.save(order);

        KitchenOrderDTO dto = convertToDTO(order);

        // Notify service staff that preparation has started
        notifyService("preparation-started", dto);

        return dto;
    }

    @Override
    @Transactional
    public KitchenOrderDTO markAsReady(Long kitchenOrderId) {
        KitchenOrder order = kitchenOrderRepository.findById(kitchenOrderId)
                .orElseThrow(() -> new RuntimeException("Kitchen order not found"));

        order.setStatus(KitchenOrderStatus.READY);
        order.setPreparationCompletedAt(LocalDateTime.now());
        order.calculateActualTime();
        order = kitchenOrderRepository.save(order);

        KitchenOrderDTO dto = convertToDTO(order);

        // Notify service staff that order is ready for pickup
        notifyService("order-ready", dto);

        return dto;
    }

    @Override
    @Transactional
    public KitchenOrderDTO markAsServed(Long kitchenOrderId) {
        KitchenOrder order = kitchenOrderRepository.findById(kitchenOrderId)
                .orElseThrow(() -> new RuntimeException("Kitchen order not found"));

        order.setStatus(KitchenOrderStatus.SERVED);
        order = kitchenOrderRepository.save(order);

        // Check if all kitchen orders for the main order are served
        checkAndCompleteOrder(order.getOrder().getId());

        return convertToDTO(order);
    }

    @Override
    @Transactional
    public void bumpOrder(Long kitchenOrderId) {
        KitchenOrder order = kitchenOrderRepository.findById(kitchenOrderId)
                .orElseThrow(() -> new RuntimeException("Kitchen order not found"));

        order.setStatus(KitchenOrderStatus.COMPLETED);
        kitchenOrderRepository.save(order);

        // Remove from displays
        notifyKitchenStation(order.getKitchenStation(), convertToDTO(order), "order-bumped");
    }

    @Override
    @Transactional
    public void createWaiterOrder(WaiterOrderRequest request, Long userId) {
        // Get required entities
        Branch branch = branchRepository.findById(request.getBranchId())
                .orElseThrow(() -> new RuntimeException("Branch not found"));

        TableLayout table = tableLayoutRepository.findById(request.getTableId())
                .orElseThrow(() -> new RuntimeException("Table not found"));

        User waiter = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // Create main order
        Order order = new Order();
        order.setBranch(branch);
        order.setTable(table);
        order.setCashier(waiter);
        order.setStatus(OrderStatus.PENDING);
        order.setOrderType("DINE_IN");
        order.setCreatedAt(LocalDateTime.now());

        double totalAmount = 0.0;
        List<OrderItem> orderItems = new ArrayList<>();

        // Create order items
        for (WaiterOrderRequest.WaiterOrderItemRequest itemReq : request.getItems()) {
            MenuItem menuItem = menuItemRepository.findById(itemReq.getMenuItemId())
                    .orElseThrow(() -> new RuntimeException("Menu item not found"));

            OrderItem orderItem = new OrderItem();
            orderItem.setProduct(menuItem);
            orderItem.setQuantity(itemReq.getQuantity());
            orderItem.setPrice(menuItem.getPrice());
            // Note: subtotal is calculated automatically via getSubtotal()
            orderItem.setNotes(itemReq.getSpecialInstructions());
            orderItem.setOrder(order);

            orderItems.add(orderItem);
            totalAmount += orderItem.getSubtotal();
        }

        order.setTotalAmount(totalAmount);
        order.setSubtotal(totalAmount);
        order = orderRepository.save(order);

        // Save order items
        for (OrderItem item : orderItems) {
            orderItemRepository.save(item);
        }

        // Update table status
        if (table.getStatus() == TableStatus.AVAILABLE) {
            table.setStatus(TableStatus.OCCUPIED);
            table.setOccupiedAt(LocalDateTime.now());
            tableLayoutRepository.save(table);
        }

        // Route to kitchen
        routeOrderToKitchen(order.getId());
    }

    @Override
    public List<KitchenOrderDTO> getReadyOrders(Long branchId) {
        List<KitchenOrder> orders = kitchenOrderRepository
                .findByOrderBranchIdAndStatus(branchId, KitchenOrderStatus.READY);

        return orders.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public KitchenOrderDTO recallOrder(Long kitchenOrderId) {
        KitchenOrder order = kitchenOrderRepository.findById(kitchenOrderId)
                .orElseThrow(() -> new RuntimeException("Kitchen order not found"));

        order.setStatus(KitchenOrderStatus.READY);
        order = kitchenOrderRepository.save(order);

        KitchenOrderDTO dto = convertToDTO(order);
        notifyService("order-recalled", dto);

        return dto;
    }

    @Override
    @Transactional
    public KitchenOrderDTO updatePriority(Long kitchenOrderId, Integer priority) {
        KitchenOrder order = kitchenOrderRepository.findById(kitchenOrderId)
                .orElseThrow(() -> new RuntimeException("Kitchen order not found"));

        order.setPriority(priority);
        order = kitchenOrderRepository.save(order);

        KitchenOrderDTO dto = convertToDTO(order);
        notifyKitchenStation(order.getKitchenStation(), dto, "priority-updated");

        return dto;
    }

    // Helper methods

    private void notifyKitchenStation(KitchenStation station, KitchenOrder order) {
        notifyKitchenStation(station, convertToDTO(order), "new-order");
    }

    private void notifyKitchenStation(KitchenStation station, KitchenOrderDTO dto, String event) {
        // Send to specific station topic
        messagingTemplate.convertAndSend("/topic/kitchen/" + station.name().toLowerCase(), Map.of(
                "event", event,
                "order", dto
        ));
    }

    private void notifyService(String event, KitchenOrderDTO dto) {
        // Send to service/waiter topic
        messagingTemplate.convertAndSend("/topic/service", Map.of(
                "event", event,
                "order", dto
        ));
    }

    private void checkAndCompleteOrder(Long orderId) {
        List<KitchenOrder> kitchenOrders = kitchenOrderRepository.findByOrderId(orderId);
        boolean allServed = kitchenOrders.stream()
                .allMatch(ko -> ko.getStatus() == KitchenOrderStatus.SERVED ||
                        ko.getStatus() == KitchenOrderStatus.COMPLETED);

        if (allServed) {
            Order order = orderRepository.findById(orderId).orElse(null);
            if (order != null) {
                order.setStatus(OrderStatus.COMPLETED);
                orderRepository.save(order);
            }
        }
    }

    private String generateOrderNumber() {
        return "ORD" + System.currentTimeMillis() % 10000;
    }

    private Integer calculateEstimatedTime(List<OrderItem> items) {
        return items.stream()
                .filter(item -> item.getProduct() instanceof MenuItem)
                .map(item -> ((MenuItem) item.getProduct()).getPreparationTime())
                .filter(Objects::nonNull)
                .max(Integer::compareTo)
                .orElse(15);
    }

    private KitchenOrderDTO convertToDTO(KitchenOrder order) {
        List<KitchenOrderItemDTO> itemDTOs = order.getItems().stream()
                .map(this::convertItemToDTO)
                .collect(Collectors.toList());

        return KitchenOrderDTO.builder()
                .id(order.getId())
                .orderId(order.getOrder().getId())
                .orderNumber(order.getOrderNumber())
                .kitchenStation(order.getKitchenStation())
                .status(order.getStatus())
                .tableNumber(order.getTableNumber())
                .priority(order.getPriority())
                .specialInstructions(order.getSpecialInstructions())
                .estimatedTime(order.getEstimatedTime())
                .actualTime(order.getActualTime())
                .createdAt(order.getCreatedAt())
                .preparationStartedAt(order.getPreparationStartedAt())
                .preparationCompletedAt(order.getPreparationCompletedAt())
                .items(itemDTOs)
                .branchId(order.getOrder().getBranch().getId())
                .branchName(order.getOrder().getBranch().getName())
                .build();
    }

    private KitchenOrderItemDTO convertItemToDTO(KitchenOrderItem item) {
        MenuItem menuItem = item.getMenuItem();
        return KitchenOrderItemDTO.builder()
                .id(item.getId())
                .itemName(menuItem.getName())
                .quantity(item.getQuantity())
                .specialInstructions(item.getSpecialInstructions())
                .courseType(menuItem.getCourseType() != null ? menuItem.getCourseType().name() : null)
                .spiceLevel(menuItem.getSpiceLevel() != null ? menuItem.getSpiceLevel().name() : null)
                .isVegetarian(menuItem.getIsVegetarian())
                .isVegan(menuItem.getIsVegan())
                .build();
    }
}
