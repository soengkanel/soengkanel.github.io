package com.ng.service;

import com.ng.domain.TableStatus;
import com.ng.modal.TableLayout;

import java.util.List;

public interface TableLayoutService {

    TableLayout createTable(TableLayout table, Long branchId);

    TableLayout updateTable(Long id, TableLayout table);

    TableLayout getTableById(Long id);

    List<TableLayout> getTablesByBranch(Long branchId);

    List<TableLayout> getAvailableTables(Long branchId);

    TableLayout updateTableStatus(Long tableId, TableStatus status);

    TableLayout assignOrderToTable(Long tableId, Long orderId);

    TableLayout releaseTable(Long tableId);

    void deleteTable(Long id);

    long countTablesByStatus(Long branchId, TableStatus status);
}
