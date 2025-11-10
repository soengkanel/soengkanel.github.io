package com.ng.controller;

import com.ng.domain.ReservationStatus;
import com.ng.payload.dto.ReservationDTO;
import com.ng.payload.request.ReservationRequest;
import com.ng.payload.request.UpdateReservationStatusRequest;
import com.ng.service.ReservationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

@RestController
@RequestMapping("/api/reservations")
@RequiredArgsConstructor
public class ReservationController {

    private final ReservationService reservationService;

    /**
     * Create a new reservation
     */
    @PostMapping
    public ResponseEntity<ReservationDTO> createReservation(
            @Valid @RequestBody ReservationRequest request,
            Authentication authentication) {
        Long userId = authentication != null ? extractUserId(authentication) : null;
        ReservationDTO reservation = reservationService.createReservation(request, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(reservation);
    }

    /**
     * Get reservation by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<ReservationDTO> getReservationById(@PathVariable Long id) {
        ReservationDTO reservation = reservationService.getReservationById(id);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Get reservation by confirmation code
     */
    @GetMapping("/confirmation/{confirmationCode}")
    public ResponseEntity<ReservationDTO> getReservationByConfirmationCode(
            @PathVariable String confirmationCode) {
        ReservationDTO reservation = reservationService.getReservationByConfirmationCode(confirmationCode);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Get all reservations for a branch
     */
    @GetMapping("/branch/{branchId}")
    public ResponseEntity<List<ReservationDTO>> getReservationsByBranch(@PathVariable Long branchId) {
        List<ReservationDTO> reservations = reservationService.getReservationsByBranch(branchId);
        return ResponseEntity.ok(reservations);
    }

    /**
     * Get reservations for a branch on a specific date
     */
    @GetMapping("/branch/{branchId}/date/{date}")
    public ResponseEntity<List<ReservationDTO>> getReservationsByBranchAndDate(
            @PathVariable Long branchId,
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        List<ReservationDTO> reservations = reservationService.getReservationsByBranchAndDate(branchId, date);
        return ResponseEntity.ok(reservations);
    }

    /**
     * Get reservations by status
     */
    @GetMapping("/branch/{branchId}/status/{status}")
    public ResponseEntity<List<ReservationDTO>> getReservationsByBranchAndStatus(
            @PathVariable Long branchId,
            @PathVariable ReservationStatus status) {
        List<ReservationDTO> reservations = reservationService.getReservationsByBranchAndStatus(branchId, status);
        return ResponseEntity.ok(reservations);
    }

    /**
     * Get upcoming reservations for a branch
     */
    @GetMapping("/branch/{branchId}/upcoming")
    public ResponseEntity<List<ReservationDTO>> getUpcomingReservations(@PathVariable Long branchId) {
        List<ReservationDTO> reservations = reservationService.getUpcomingReservations(branchId);
        return ResponseEntity.ok(reservations);
    }

    /**
     * Get reservations within a date range
     */
    @GetMapping("/branch/{branchId}/range")
    public ResponseEntity<List<ReservationDTO>> getReservationsByDateRange(
            @PathVariable Long branchId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        List<ReservationDTO> reservations = reservationService.getReservationsByDateRange(branchId, startDate, endDate);
        return ResponseEntity.ok(reservations);
    }

    /**
     * Get customer's reservations
     */
    @GetMapping("/customer/{customerId}")
    public ResponseEntity<List<ReservationDTO>> getCustomerReservations(@PathVariable Long customerId) {
        List<ReservationDTO> reservations = reservationService.getCustomerReservations(customerId);
        return ResponseEntity.ok(reservations);
    }

    /**
     * Update reservation details
     */
    @PutMapping("/{id}")
    public ResponseEntity<ReservationDTO> updateReservation(
            @PathVariable Long id,
            @Valid @RequestBody ReservationRequest request) {
        ReservationDTO reservation = reservationService.updateReservation(id, request);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Update reservation status
     */
    @PatchMapping("/{id}/status")
    public ResponseEntity<ReservationDTO> updateReservationStatus(
            @PathVariable Long id,
            @Valid @RequestBody UpdateReservationStatusRequest request) {
        ReservationDTO reservation = reservationService.updateReservationStatus(id, request);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Confirm a reservation
     */
    @PostMapping("/{id}/confirm")
    public ResponseEntity<ReservationDTO> confirmReservation(@PathVariable Long id) {
        ReservationDTO reservation = reservationService.confirmReservation(id);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Cancel a reservation
     */
    @PostMapping("/{id}/cancel")
    public ResponseEntity<ReservationDTO> cancelReservation(
            @PathVariable Long id,
            @RequestParam String reason) {
        ReservationDTO reservation = reservationService.cancelReservation(id, reason);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Mark customer as seated
     */
    @PostMapping("/{id}/seat")
    public ResponseEntity<ReservationDTO> seatReservation(
            @PathVariable Long id,
            @RequestParam Long tableId) {
        ReservationDTO reservation = reservationService.seatReservation(id, tableId);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Complete a reservation
     */
    @PostMapping("/{id}/complete")
    public ResponseEntity<ReservationDTO> completeReservation(@PathVariable Long id) {
        ReservationDTO reservation = reservationService.completeReservation(id);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Mark as no-show
     */
    @PostMapping("/{id}/no-show")
    public ResponseEntity<ReservationDTO> markAsNoShow(@PathVariable Long id) {
        ReservationDTO reservation = reservationService.markAsNoShow(id);
        return ResponseEntity.ok(reservation);
    }

    /**
     * Delete a reservation
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<String> deleteReservation(@PathVariable Long id) {
        reservationService.deleteReservation(id);
        return ResponseEntity.ok("Reservation deleted successfully");
    }

    /**
     * Check table availability
     */
    @GetMapping("/availability/table/{tableId}")
    public ResponseEntity<Boolean> checkTableAvailability(
            @PathVariable Long tableId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.TIME) LocalTime startTime,
            @RequestParam Integer durationMinutes) {
        boolean available = reservationService.isTableAvailable(tableId, date, startTime, durationMinutes);
        return ResponseEntity.ok(available);
    }

    /**
     * Get available tables
     */
    @GetMapping("/availability/branch/{branchId}/tables")
    public ResponseEntity<List<Long>> getAvailableTables(
            @PathVariable Long branchId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.TIME) LocalTime time,
            @RequestParam Integer guests,
            @RequestParam Integer duration) {
        List<Long> availableTables = reservationService.getAvailableTables(branchId, date, time, guests, duration);
        return ResponseEntity.ok(availableTables);
    }

    /**
     * Helper method to extract user ID from authentication
     */
    private Long extractUserId(Authentication authentication) {
        // This should be implemented based on your authentication setup
        // For now, returning null
        return null;
    }
}
