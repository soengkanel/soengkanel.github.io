package com.ng.service;

import com.ng.domain.ReservationStatus;
import com.ng.payload.dto.ReservationDTO;
import com.ng.payload.request.ReservationRequest;
import com.ng.payload.request.UpdateReservationStatusRequest;

import java.time.LocalDate;
import java.util.List;

public interface ReservationService {

    /**
     * Create a new reservation
     */
    ReservationDTO createReservation(ReservationRequest request, Long userId);

    /**
     * Get reservation by ID
     */
    ReservationDTO getReservationById(Long id);

    /**
     * Get reservation by confirmation code
     */
    ReservationDTO getReservationByConfirmationCode(String confirmationCode);

    /**
     * Get all reservations for a branch
     */
    List<ReservationDTO> getReservationsByBranch(Long branchId);

    /**
     * Get reservations for a branch on a specific date
     */
    List<ReservationDTO> getReservationsByBranchAndDate(Long branchId, LocalDate date);

    /**
     * Get reservations by status
     */
    List<ReservationDTO> getReservationsByBranchAndStatus(Long branchId, ReservationStatus status);

    /**
     * Get upcoming reservations for a branch
     */
    List<ReservationDTO> getUpcomingReservations(Long branchId);

    /**
     * Get reservations within a date range
     */
    List<ReservationDTO> getReservationsByDateRange(Long branchId, LocalDate startDate, LocalDate endDate);

    /**
     * Get customer's reservations
     */
    List<ReservationDTO> getCustomerReservations(Long customerId);

    /**
     * Update reservation details
     */
    ReservationDTO updateReservation(Long id, ReservationRequest request);

    /**
     * Update reservation status
     */
    ReservationDTO updateReservationStatus(Long id, UpdateReservationStatusRequest request);

    /**
     * Confirm a reservation
     */
    ReservationDTO confirmReservation(Long id);

    /**
     * Cancel a reservation
     */
    ReservationDTO cancelReservation(Long id, String reason);

    /**
     * Mark customer as seated
     */
    ReservationDTO seatReservation(Long id, Long tableId);

    /**
     * Complete a reservation
     */
    ReservationDTO completeReservation(Long id);

    /**
     * Mark as no-show
     */
    ReservationDTO markAsNoShow(Long id);

    /**
     * Delete a reservation
     */
    void deleteReservation(Long id);

    /**
     * Check table availability for given date/time
     */
    boolean isTableAvailable(Long tableId, LocalDate date, java.time.LocalTime startTime, Integer durationMinutes);

    /**
     * Get available tables for a given date/time/party size
     */
    List<Long> getAvailableTables(Long branchId, LocalDate date, java.time.LocalTime time, Integer guests, Integer duration);

    /**
     * Send reservation reminders for upcoming reservations
     */
    void sendReservationReminders();
}
