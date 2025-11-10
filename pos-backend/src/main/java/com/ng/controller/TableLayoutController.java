package com.ng.controller;

import com.ng.domain.TableStatus;
import com.ng.modal.TableLayout;
import com.ng.service.TableLayoutService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tables")
@RequiredArgsConstructor
public class TableLayoutController {

    private final TableLayoutService tableLayoutService;

    @PostMapping
    public ResponseEntity<TableLayout> createTable(
            @Valid @RequestBody TableLayout table,
            @RequestParam Long branchId) {
        TableLayout created = tableLayoutService.createTable(table, branchId);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<TableLayout> updateTable(
            @PathVariable Long id,
            @Valid @RequestBody TableLayout table) {
        TableLayout updated = tableLayoutService.updateTable(id, table);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TableLayout> getTableById(@PathVariable Long id) {
        TableLayout table = tableLayoutService.getTableById(id);
        return ResponseEntity.ok(table);
    }

    @GetMapping
    public ResponseEntity<List<TableLayout>> getTablesByBranch(@RequestParam Long branchId) {
        List<TableLayout> tables = tableLayoutService.getTablesByBranch(branchId);
        return ResponseEntity.ok(tables);
    }

    @GetMapping("/available")
    public ResponseEntity<List<TableLayout>> getAvailableTables(@RequestParam Long branchId) {
        List<TableLayout> tables = tableLayoutService.getAvailableTables(branchId);
        return ResponseEntity.ok(tables);
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<TableLayout> updateTableStatus(
            @PathVariable Long id,
            @RequestParam TableStatus status) {
        TableLayout table = tableLayoutService.updateTableStatus(id, status);
        return ResponseEntity.ok(table);
    }

    @PatchMapping("/{tableId}/assign-order")
    public ResponseEntity<TableLayout> assignOrderToTable(
            @PathVariable Long tableId,
            @RequestParam Long orderId) {
        TableLayout table = tableLayoutService.assignOrderToTable(tableId, orderId);
        return ResponseEntity.ok(table);
    }

    @PatchMapping("/{id}/release")
    public ResponseEntity<TableLayout> releaseTable(@PathVariable Long id) {
        TableLayout table = tableLayoutService.releaseTable(id);
        return ResponseEntity.ok(table);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTable(@PathVariable Long id) {
        tableLayoutService.deleteTable(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/count")
    public ResponseEntity<Long> countTablesByStatus(
            @RequestParam Long branchId,
            @RequestParam TableStatus status) {
        long count = tableLayoutService.countTablesByStatus(branchId, status);
        return ResponseEntity.ok(count);
    }
}
