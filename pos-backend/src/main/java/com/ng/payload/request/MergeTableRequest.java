package com.ng.payload.request;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Request to merge multiple table orders into one
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MergeTableRequest {

    @NotEmpty(message = "Source order IDs cannot be empty")
    private List<Long> sourceOrderIds;

    @NotNull(message = "Target table ID is required")
    private Long targetTableId;

    private String reason; // Optional reason for merge
}
