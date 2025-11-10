package com.ng.payload.StoreAnalysis;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class BranchSalesDTO {
    private String branchName;
    private Double totalSales;
}

