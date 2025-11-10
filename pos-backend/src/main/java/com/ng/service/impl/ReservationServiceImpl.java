package com.ng.service.impl;

import com.ng.domain.ReservationStatus;
import com.ng.domain.TableStatus;
import com.ng.modal.*;
import com.ng.payload.dto.ReservationDTO;
import com.ng.payload.request.ReservationRequest;
import com.ng.payload.request.UpdateReservationStatusRequest;
import com.ng.repository.*;
import com.ng.service.EmailService;
import com.ng.service.ReservationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ReservationServiceImpl implements ReservationService {

    private final ReservationRepository reservationRepository;
    private final CustomerRepository customerRepository;
    private final BranchRepository branchRepository;
    private final TableLayoutRepository tableLayoutRepository;
    private final UserRepository userRepository;
    private final EmailService emailService;

    @Override
    @Transactional
    public ReservationDTO createReservation(ReservationRequest request, Long userId) {
        // Validate customer
        Customer customer = customerRepository.findById(request.getCustomerId())
                .orElseThrow(() -> new RuntimeException("Customer not found with id: " + request.getCustomerId()));

        // Validate branch
        Branch branch = branchRepository.findById(request.getBranchId())
                .orElseThrow(() -> new RuntimeException("Branch not found with id: " + request.getBranchId()));

        // Validate table if provided
        TableLayout table = null;
        if (request.getTableId() != null) {
            table = tableLayoutRepository.findById(request.getTableId())
                    .orElseThrow(() -> new RuntimeException("Table not found with id: " + request.getTableId()));

            // Check table availability
            LocalTime endTime = request.getReservationTime().plusMinutes(request.getDurationMinutes());
            if (reservationRepository.hasOverlappingReservation(
                    request.getTableId(),
                    request.getReservationDate(),
                    request.getReservationTime(),
                    endTime)) {
                throw new RuntimeException("Table is not available for the selected time slot");
            }
        }

        // Get user who created the reservation
        User createdBy = userId != null ? userRepository.findById(userId).orElse(null) : null;

        // Create reservation
        Reservation reservation = Reservation.builder()
                .customer(customer)
                .branch(branch)
                .table(table)
                .reservationDate(request.getReservationDate())
                .reservationTime(request.getReservationTime())
                .numberOfGuests(request.getNumberOfGuests())
                .specialRequests(request.getSpecialRequests())
                .durationMinutes(request.getDurationMinutes())
                .status(ReservationStatus.PENDING)
                .createdBy(createdBy)
                .reminderSent(false)
                .build();

        reservation = reservationRepository.save(reservation);

        // Send confirmation email
        sendConfirmationEmail(reservation);

        return convertToDTO(reservation);
    }

    @Override
    public ReservationDTO getReservationById(Long id) {
        Reservation reservation = reservationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + id));
        return convertToDTO(reservation);
    }

    @Override
    public ReservationDTO getReservationByConfirmationCode(String confirmationCode) {
        Reservation reservation = reservationRepository.findByConfirmationCode(confirmationCode)
                .orElseThrow(() -> new RuntimeException("Reservation not found with confirmation code: " + confirmationCode));
        return convertToDTO(reservation);
    }

    @Override
    public List<ReservationDTO> getReservationsByBranch(Long branchId) {
        List<Reservation> reservations = reservationRepository
                .findByBranchIdOrderByReservationDateDescReservationTimeDesc(branchId);
        return reservations.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<ReservationDTO> getReservationsByBranchAndDate(Long branchId, LocalDate date) {
        List<Reservation> reservations = reservationRepository
                .findByBranchIdAndReservationDateOrderByReservationTime(branchId, date);
        return reservations.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<ReservationDTO> getReservationsByBranchAndStatus(Long branchId, ReservationStatus status) {
        List<Reservation> reservations = reservationRepository
                .findByBranchIdAndStatusOrderByReservationDateDescReservationTimeDesc(branchId, status);
        return reservations.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<ReservationDTO> getUpcomingReservations(Long branchId) {
        List<Reservation> reservations = reservationRepository
                .findUpcomingReservations(branchId, LocalDate.now());
        return reservations.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<ReservationDTO> getReservationsByDateRange(Long branchId, LocalDate startDate, LocalDate endDate) {
        List<Reservation> reservations = reservationRepository
                .findByBranchAndDateRange(branchId, startDate, endDate);
        return reservations.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<ReservationDTO> getCustomerReservations(Long customerId) {
        List<Reservation> reservations = reservationRepository
                .findByCustomerIdOrderByReservationDateDescReservationTimeDesc(customerId);
        return reservations.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public ReservationDTO updateReservation(Long id, ReservationRequest request) {
        Reservation reservation = reservationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + id));

        // Only allow updates for pending or confirmed reservations
        if (!reservation.isActive()) {
            throw new RuntimeException("Cannot update reservation with status: " + reservation.getStatus());
        }

        // Update basic details
        reservation.setReservationDate(request.getReservationDate());
        reservation.setReservationTime(request.getReservationTime());
        reservation.setNumberOfGuests(request.getNumberOfGuests());
        reservation.setSpecialRequests(request.getSpecialRequests());
        reservation.setDurationMinutes(request.getDurationMinutes());

        // Update table if provided
        if (request.getTableId() != null && !request.getTableId().equals(
                reservation.getTable() != null ? reservation.getTable().getId() : null)) {
            TableLayout table = tableLayoutRepository.findById(request.getTableId())
                    .orElseThrow(() -> new RuntimeException("Table not found with id: " + request.getTableId()));

            // Check table availability
            LocalTime endTime = request.getReservationTime().plusMinutes(request.getDurationMinutes());
            if (reservationRepository.hasOverlappingReservation(
                    request.getTableId(),
                    request.getReservationDate(),
                    request.getReservationTime(),
                    endTime)) {
                throw new RuntimeException("Table is not available for the selected time slot");
            }

            reservation.setTable(table);
        }

        reservation = reservationRepository.save(reservation);
        return convertToDTO(reservation);
    }

    @Override
    @Transactional
    public ReservationDTO updateReservationStatus(Long id, UpdateReservationStatusRequest request) {
        Reservation reservation = reservationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + id));

        ReservationStatus newStatus = request.getStatus();

        // Handle status-specific logic
        switch (newStatus) {
            case CANCELLED:
                if (request.getCancellationReason() == null || request.getCancellationReason().trim().isEmpty()) {
                    throw new RuntimeException("Cancellation reason is required");
                }
                reservation.setCancellationReason(request.getCancellationReason());
                reservation.setCancelledAt(LocalDateTime.now());
                break;

            case SEATED:
                if (request.getTableId() == null) {
                    throw new RuntimeException("Table ID is required when seating customers");
                }
                TableLayout table = tableLayoutRepository.findById(request.getTableId())
                        .orElseThrow(() -> new RuntimeException("Table not found with id: " + request.getTableId()));
                reservation.setTable(table);
                reservation.setSeatedAt(LocalDateTime.now());

                // Update table status
                table.setStatus(TableStatus.OCCUPIED);
                table.setOccupiedAt(LocalDateTime.now());
                tableLayoutRepository.save(table);
                break;

            case COMPLETED:
                reservation.setCompletedAt(LocalDateTime.now());

                // Free up the table if assigned
                if (reservation.getTable() != null) {
                    TableLayout reservedTable = reservation.getTable();
                    reservedTable.setStatus(TableStatus.AVAILABLE);
                    reservedTable.setOccupiedAt(null);
                    tableLayoutRepository.save(reservedTable);
                }
                break;

            case NO_SHOW:
                // Free up the table if reserved
                if (reservation.getTable() != null) {
                    TableLayout reservedTable = reservation.getTable();
                    if (reservedTable.getStatus() == TableStatus.RESERVED) {
                        reservedTable.setStatus(TableStatus.AVAILABLE);
                        tableLayoutRepository.save(reservedTable);
                    }
                }
                break;

            case CONFIRMED:
                // Update table status to reserved if table is assigned
                if (reservation.getTable() != null) {
                    TableLayout reservedTable = reservation.getTable();
                    reservedTable.setStatus(TableStatus.RESERVED);
                    tableLayoutRepository.save(reservedTable);
                }
                break;
        }

        reservation.setStatus(newStatus);
        reservation = reservationRepository.save(reservation);

        return convertToDTO(reservation);
    }

    @Override
    @Transactional
    public ReservationDTO confirmReservation(Long id) {
        UpdateReservationStatusRequest request = UpdateReservationStatusRequest.builder()
                .status(ReservationStatus.CONFIRMED)
                .build();
        return updateReservationStatus(id, request);
    }

    @Override
    @Transactional
    public ReservationDTO cancelReservation(Long id, String reason) {
        UpdateReservationStatusRequest request = UpdateReservationStatusRequest.builder()
                .status(ReservationStatus.CANCELLED)
                .cancellationReason(reason)
                .build();
        return updateReservationStatus(id, request);
    }

    @Override
    @Transactional
    public ReservationDTO seatReservation(Long id, Long tableId) {
        UpdateReservationStatusRequest request = UpdateReservationStatusRequest.builder()
                .status(ReservationStatus.SEATED)
                .tableId(tableId)
                .build();
        return updateReservationStatus(id, request);
    }

    @Override
    @Transactional
    public ReservationDTO completeReservation(Long id) {
        UpdateReservationStatusRequest request = UpdateReservationStatusRequest.builder()
                .status(ReservationStatus.COMPLETED)
                .build();
        return updateReservationStatus(id, request);
    }

    @Override
    @Transactional
    public ReservationDTO markAsNoShow(Long id) {
        UpdateReservationStatusRequest request = UpdateReservationStatusRequest.builder()
                .status(ReservationStatus.NO_SHOW)
                .build();
        return updateReservationStatus(id, request);
    }

    @Override
    @Transactional
    public void deleteReservation(Long id) {
        Reservation reservation = reservationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Reservation not found with id: " + id));

        // Only allow deletion for pending reservations or cancelled ones
        if (reservation.getStatus() != ReservationStatus.PENDING &&
            reservation.getStatus() != ReservationStatus.CANCELLED) {
            throw new RuntimeException("Cannot delete reservation with status: " + reservation.getStatus());
        }

        reservationRepository.delete(reservation);
    }

    @Override
    public boolean isTableAvailable(Long tableId, LocalDate date, LocalTime startTime, Integer durationMinutes) {
        LocalTime endTime = startTime.plusMinutes(durationMinutes);
        return !reservationRepository.hasOverlappingReservation(tableId, date, startTime, endTime);
    }

    @Override
    public List<Long> getAvailableTables(Long branchId, LocalDate date, LocalTime time, Integer guests, Integer duration) {
        // Get all tables in the branch with sufficient capacity
        List<TableLayout> allTables = tableLayoutRepository.findByBranchId(branchId).stream()
                .filter(table -> table.getIsActive() && table.getCapacity() >= guests)
                .collect(Collectors.toList());

        // Filter out tables that are not available
        LocalTime endTime = time.plusMinutes(duration);
        return allTables.stream()
                .filter(table -> !reservationRepository.hasOverlappingReservation(
                        table.getId(), date, time, endTime))
                .map(TableLayout::getId)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public void sendReservationReminders() {
        LocalDate tomorrow = LocalDate.now().plusDays(1);
        List<Reservation> reservations = reservationRepository.findReservationsNeedingReminders(tomorrow);

        for (Reservation reservation : reservations) {
            try {
                sendReminderEmail(reservation);
                reservation.setReminderSent(true);
                reservationRepository.save(reservation);
            } catch (Exception e) {
                // Log error but continue with other reminders
                System.err.println("Failed to send reminder for reservation " + reservation.getId() + ": " + e.getMessage());
            }
        }
    }

    private void sendConfirmationEmail(Reservation reservation) {
        try {
            String subject = "Reservation Confirmation - " + reservation.getConfirmationCode();
            String body = String.format(
                    "Dear %s,\n\n" +
                    "Your reservation has been created successfully.\n\n" +
                    "Confirmation Code: %s\n" +
                    "Date: %s\n" +
                    "Time: %s\n" +
                    "Number of Guests: %d\n" +
                    "Branch: %s\n\n" +
                    "Thank you for choosing us!\n\n" +
                    "Best regards,\n" +
                    "%s",
                    reservation.getCustomer().getFullName(),
                    reservation.getConfirmationCode(),
                    reservation.getReservationDate(),
                    reservation.getReservationTime(),
                    reservation.getNumberOfGuests(),
                    reservation.getBranch().getName(),
                    reservation.getBranch().getName()
            );

            emailService.sendEmail(
                    reservation.getCustomer().getEmail(),
                    subject,
                    body
            );
        } catch (Exception e) {
            // Log error but don't fail the reservation
            System.err.println("Failed to send confirmation email: " + e.getMessage());
        }
    }

    private void sendReminderEmail(Reservation reservation) {
        try {
            String subject = "Reservation Reminder - " + reservation.getConfirmationCode();
            String body = String.format(
                    "Dear %s,\n\n" +
                    "This is a reminder for your upcoming reservation.\n\n" +
                    "Confirmation Code: %s\n" +
                    "Date: %s (Tomorrow)\n" +
                    "Time: %s\n" +
                    "Number of Guests: %d\n" +
                    "Branch: %s\n\n" +
                    "We look forward to seeing you!\n\n" +
                    "Best regards,\n" +
                    "%s",
                    reservation.getCustomer().getFullName(),
                    reservation.getConfirmationCode(),
                    reservation.getReservationDate(),
                    reservation.getReservationTime(),
                    reservation.getNumberOfGuests(),
                    reservation.getBranch().getName(),
                    reservation.getBranch().getName()
            );

            emailService.sendEmail(
                    reservation.getCustomer().getEmail(),
                    subject,
                    body
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to send reminder email: " + e.getMessage());
        }
    }

    private ReservationDTO convertToDTO(Reservation reservation) {
        return ReservationDTO.builder()
                .id(reservation.getId())
                .customerId(reservation.getCustomer().getId())
                .customerName(reservation.getCustomer().getFullName())
                .customerPhone(reservation.getCustomer().getPhone())
                .customerEmail(reservation.getCustomer().getEmail())
                .branchId(reservation.getBranch().getId())
                .branchName(reservation.getBranch().getName())
                .tableId(reservation.getTable() != null ? reservation.getTable().getId() : null)
                .tableNumber(reservation.getTable() != null ? reservation.getTable().getTableNumber() : null)
                .reservationDate(reservation.getReservationDate())
                .reservationTime(reservation.getReservationTime())
                .numberOfGuests(reservation.getNumberOfGuests())
                .status(reservation.getStatus())
                .specialRequests(reservation.getSpecialRequests())
                .durationMinutes(reservation.getDurationMinutes())
                .confirmationCode(reservation.getConfirmationCode())
                .seatedAt(reservation.getSeatedAt())
                .completedAt(reservation.getCompletedAt())
                .cancellationReason(reservation.getCancellationReason())
                .cancelledAt(reservation.getCancelledAt())
                .createdAt(reservation.getCreatedAt())
                .updatedAt(reservation.getUpdatedAt())
                .build();
    }
}
