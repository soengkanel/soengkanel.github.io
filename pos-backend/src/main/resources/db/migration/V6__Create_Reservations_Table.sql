-- Migration: Create Reservations Table
-- Description: Adds table reservation functionality for F&B/Restaurant business types
-- Author: System
-- Date: 2025-10-14

-- Create reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    -- Customer and branch references
    customer_id BIGINT NOT NULL,
    branch_id BIGINT NOT NULL,
    table_id BIGINT NULL,

    -- Reservation details
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    number_of_guests INT NOT NULL CHECK (number_of_guests >= 1 AND number_of_guests <= 50),
    duration_minutes INT NOT NULL DEFAULT 120 CHECK (duration_minutes >= 30 AND duration_minutes <= 480),

    -- Status and tracking
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    confirmation_code VARCHAR(50) UNIQUE NOT NULL,

    -- Additional information
    special_requests TEXT(500),
    reminder_sent BOOLEAN DEFAULT FALSE,

    -- Timestamps for different states
    seated_at DATETIME NULL,
    completed_at DATETIME NULL,
    cancelled_at DATETIME NULL,
    cancellation_reason VARCHAR(500) NULL,

    -- User who created the reservation
    created_by BIGINT NULL,

    -- Audit fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign key constraints
    CONSTRAINT fk_reservation_customer FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE RESTRICT,
    CONSTRAINT fk_reservation_branch FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE RESTRICT,
    CONSTRAINT fk_reservation_table FOREIGN KEY (table_id) REFERENCES table_layouts(id) ON DELETE SET NULL,
    CONSTRAINT fk_reservation_created_by FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE SET NULL,

    -- Indexes for performance
    INDEX idx_reservation_date (reservation_date),
    INDEX idx_reservation_branch_date (branch_id, reservation_date),
    INDEX idx_reservation_branch_status (branch_id, status),
    INDEX idx_reservation_customer (customer_id),
    INDEX idx_reservation_confirmation (confirmation_code),
    INDEX idx_reservation_status (status),
    INDEX idx_reservation_table (table_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add comment to table
ALTER TABLE reservations COMMENT = 'Table reservations for restaurant/F&B businesses';
