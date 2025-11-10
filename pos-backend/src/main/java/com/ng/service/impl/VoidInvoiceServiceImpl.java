package com.ng.service.impl;

import com.ng.domain.OrderStatus;
import com.ng.domain.VoidReason;
import com.ng.mapper.OrderMapper;
import com.ng.modal.Order;
import com.ng.modal.User;
import com.ng.payload.dto.OrderDTO;
import com.ng.payload.request.VoidInvoiceRequest;
import com.ng.repository.OrderRepository;
import com.ng.repository.UserRepository;
import com.ng.service.VoidInvoiceService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class VoidInvoiceServiceImpl implements VoidInvoiceService {

    private final OrderRepository orderRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional
    public OrderDTO voidInvoice(VoidInvoiceRequest request, Long userId) {
        // Fetch the order
        Order order = orderRepository.findById(request.getOrderId())
                .orElseThrow(() -> new RuntimeException("Order not found"));

        // Validation: Cannot void already voided order
        if (order.getIsVoided() != null && order.getIsVoided()) {
            throw new RuntimeException("Order is already voided");
        }

        // Validation: Check order status (typically void COMPLETED orders only)
        if (order.getStatus() != OrderStatus.COMPLETED) {
            throw new RuntimeException("Can only void completed orders. Current status: " + order.getStatus());
        }

        // Fetch user performing void
        User voidUser = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // Optional: Manager approval validation
        User manager = null;
        if (request.getManagerId() != null) {
            manager = userRepository.findById(request.getManagerId())
                    .orElseThrow(() -> new RuntimeException("Manager not found"));

            // TODO: Verify manager password if provided
            // TODO: Check if user has MANAGER role
        }

        // Perform void
        order.setIsVoided(true);
        order.setVoidReason(request.getVoidReason());
        order.setVoidNotes(request.getVoidNotes());
        order.setVoidedBy(voidUser);
        order.setVoidedAt(LocalDateTime.now());
        order.setVoidApprovedBy(manager);
        order.setStatus(OrderStatus.CANCELLED); // Change status to CANCELLED

        order = orderRepository.save(order);

        // Log the void action
        log.info("Order #{} voided by user #{} ({}). Reason: {}, Notes: {}",
                order.getId(),
                voidUser.getId(),
                voidUser.getFullName(),
                request.getVoidReason(),
                request.getVoidNotes());

        // TODO: Send notification to management
        // TODO: Update inventory if needed
        // TODO: Process refund if payment was made

        return OrderMapper.toDto(order);
    }

    @Override
    public List<OrderDTO> getVoidedOrders(Long branchId, LocalDateTime startDate, LocalDateTime endDate) {
        List<Order> voidedOrders = orderRepository.findByBranchIdAndCreatedAtBetween(branchId, startDate, endDate)
                .stream()
                .filter(order -> order.getIsVoided() != null && order.getIsVoided())
                .collect(Collectors.toList());

        return voidedOrders.stream()
                .map(OrderMapper::toDto)
                .collect(Collectors.toList());
    }

    @Override
    public VoidStatisticsDTO getVoidStatistics(Long branchId, LocalDateTime startDate, LocalDateTime endDate) {
        List<Order> voidedOrders = orderRepository.findByBranchIdAndCreatedAtBetween(branchId, startDate, endDate)
                .stream()
                .filter(order -> order.getIsVoided() != null && order.getIsVoided())
                .collect(Collectors.toList());

        VoidStatisticsDTO stats = new VoidStatisticsDTO();
        stats.totalVoidedOrders = (long) voidedOrders.size();
        stats.totalVoidedAmount = voidedOrders.stream()
                .mapToDouble(order -> order.getTotalAmount() != null ? order.getTotalAmount() : 0.0)
                .sum();

        // Group by reason
        stats.voidsByReason = new HashMap<>();
        for (Order order : voidedOrders) {
            String reason = order.getVoidReason() != null ? order.getVoidReason().name() : "UNKNOWN";
            stats.voidsByReason.put(reason, stats.voidsByReason.getOrDefault(reason, 0L) + 1);
        }

        // Group by user
        stats.voidsByUser = new HashMap<>();
        for (Order order : voidedOrders) {
            if (order.getVoidedBy() != null) {
                String userName = order.getVoidedBy().getFullName();
                stats.voidsByUser.put(userName, stats.voidsByUser.getOrDefault(userName, 0L) + 1);
            }
        }

        return stats;
    }
}
