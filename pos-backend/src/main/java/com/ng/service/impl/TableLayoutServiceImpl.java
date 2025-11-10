package com.ng.service.impl;

import com.ng.domain.TableStatus;
import com.ng.exception.ResourceNotFoundException;
import com.ng.modal.Branch;
import com.ng.modal.Order;
import com.ng.modal.TableLayout;
import com.ng.repository.BranchRepository;
import com.ng.repository.OrderRepository;
import com.ng.repository.TableLayoutRepository;
import com.ng.service.TableLayoutService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class TableLayoutServiceImpl implements TableLayoutService {

    private final TableLayoutRepository tableLayoutRepository;
    private final BranchRepository branchRepository;
    private final OrderRepository orderRepository;

    @Override
    @Transactional
    public TableLayout createTable(TableLayout table, Long branchId) {
        Branch branch = branchRepository.findById(branchId)
                .orElseThrow(() -> new ResourceNotFoundException("Branch not found"));

        table.setBranch(branch);
        table.setStatus(TableStatus.AVAILABLE);
        table.setIsActive(true);

        return tableLayoutRepository.save(table);
    }

    @Override
    @Transactional
    public TableLayout updateTable(Long id, TableLayout tableData) {
        TableLayout table = getTableById(id);

        table.setTableNumber(tableData.getTableNumber());
        table.setCapacity(tableData.getCapacity());
        table.setLocation(tableData.getLocation());
        table.setNotes(tableData.getNotes());
        table.setIsActive(tableData.getIsActive());

        return tableLayoutRepository.save(table);
    }

    @Override
    public TableLayout getTableById(Long id) {
        return tableLayoutRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Table not found"));
    }

    @Override
    public List<TableLayout> getTablesByBranch(Long branchId) {
        return tableLayoutRepository.findByBranchIdAndIsActiveTrue(branchId);
    }

    @Override
    public List<TableLayout> getAvailableTables(Long branchId) {
        return tableLayoutRepository.findByBranchIdAndStatusAndIsActiveTrue(branchId, TableStatus.AVAILABLE);
    }

    @Override
    @Transactional
    public TableLayout updateTableStatus(Long tableId, TableStatus status) {
        TableLayout table = getTableById(tableId);
        table.setStatus(status);

        if (status == TableStatus.AVAILABLE) {
            table.setCurrentOrder(null);
            table.setOccupiedAt(null);
        }

        return tableLayoutRepository.save(table);
    }

    @Override
    @Transactional
    public TableLayout assignOrderToTable(Long tableId, Long orderId) {
        TableLayout table = getTableById(tableId);
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new ResourceNotFoundException("Order not found"));

        table.setCurrentOrder(order);
        table.setStatus(TableStatus.OCCUPIED);
        table.setOccupiedAt(LocalDateTime.now());

        return tableLayoutRepository.save(table);
    }

    @Override
    @Transactional
    public TableLayout releaseTable(Long tableId) {
        TableLayout table = getTableById(tableId);
        table.setCurrentOrder(null);
        table.setStatus(TableStatus.CLEANING);
        table.setOccupiedAt(null);

        return tableLayoutRepository.save(table);
    }

    @Override
    @Transactional
    public void deleteTable(Long id) {
        TableLayout table = getTableById(id);
        table.setIsActive(false);
        tableLayoutRepository.save(table);
    }

    @Override
    public long countTablesByStatus(Long branchId, TableStatus status) {
        return tableLayoutRepository.countByBranchIdAndStatus(branchId, status);
    }
}
