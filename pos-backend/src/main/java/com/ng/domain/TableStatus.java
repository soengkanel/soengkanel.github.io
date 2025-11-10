package com.ng.domain;

public enum TableStatus {
    AVAILABLE,    // Table is free
    OCCUPIED,     // Table has active order
    RESERVED,     // Table is reserved
    CLEANING      // Table is being cleaned
}
