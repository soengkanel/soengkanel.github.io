package com.ng.repository;

import com.ng.domain.ReservationStatus;
import com.ng.modal.Reservation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface ReservationRepository extends JpaRepository<Reservation, Long> {

    /**
     * Find reservation by confirmation code
     */
    Optional<Reservation> findByConfirmationCode(String confirmationCode);

    /**
     * Find all reservations for a specific branch
     */
    List<Reservation> findByBranchIdOrderByReservationDateDescReservationTimeDesc(Long branchId);

    /**
     * Find all reservations for a specific branch on a given date
     */
    List<Reservation> findByBranchIdAndReservationDateOrderByReservationTime(Long branchId, LocalDate date);

    /**
     * Find all reservations for a specific branch and status
     */
    List<Reservation> findByBranchIdAndStatusOrderByReservationDateDescReservationTimeDesc(Long branchId, ReservationStatus status);

    /**
     * Find all reservations for a customer
     */
    List<Reservation> findByCustomerIdOrderByReservationDateDescReservationTimeDesc(Long customerId);

    /**
     * Find all active reservations for a specific table
     */
    @Query("SELECT r FROM Reservation r WHERE r.table.id = :tableId AND r.status IN ('CONFIRMED', 'SEATED')")
    List<Reservation> findActiveReservationsByTableId(@Param("tableId") Long tableId);

    /**
     * Find upcoming reservations (today and future)
     */
    @Query("SELECT r FROM Reservation r WHERE r.branch.id = :branchId AND r.reservationDate >= :fromDate AND r.status IN ('PENDING', 'CONFIRMED') ORDER BY r.reservationDate, r.reservationTime")
    List<Reservation> findUpcomingReservations(@Param("branchId") Long branchId, @Param("fromDate") LocalDate fromDate);

    /**
     * Find reservations within a date range
     */
    @Query("SELECT r FROM Reservation r WHERE r.branch.id = :branchId AND r.reservationDate BETWEEN :startDate AND :endDate ORDER BY r.reservationDate, r.reservationTime")
    List<Reservation> findByBranchAndDateRange(@Param("branchId") Long branchId, @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate);

    /**
     * Find reservations that need reminders (upcoming within next 24 hours, not yet reminded)
     */
    @Query("SELECT r FROM Reservation r WHERE r.status = 'CONFIRMED' AND r.reminderSent = false AND r.reservationDate = :tomorrow")
    List<Reservation> findReservationsNeedingReminders(@Param("tomorrow") LocalDate tomorrow);

    /**
     * Check for overlapping reservations for a table
     * Uses native query for time arithmetic
     */
    @Query(value = "SELECT COUNT(*) > 0 FROM reservations r " +
           "WHERE r.table_id = :tableId AND r.reservation_date = :date " +
           "AND r.status IN ('CONFIRMED', 'SEATED') " +
           "AND (r.reservation_time < :endTime " +
           "AND ADDTIME(r.reservation_time, SEC_TO_TIME(r.duration_minutes * 60)) > :startTime)",
           nativeQuery = true)
    boolean hasOverlappingReservation(@Param("tableId") Long tableId, @Param("date") LocalDate date,
                                     @Param("startTime") LocalTime startTime, @Param("endTime") LocalTime endTime);

    /**
     * Count reservations by status for a branch
     */
    long countByBranchIdAndStatus(Long branchId, ReservationStatus status);

    /**
     * Count total reservations for a branch in a date range
     */
    @Query("SELECT COUNT(r) FROM Reservation r WHERE r.branch.id = :branchId AND r.reservationDate BETWEEN :startDate AND :endDate")
    long countReservationsByBranchAndDateRange(@Param("branchId") Long branchId, @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate);
}
