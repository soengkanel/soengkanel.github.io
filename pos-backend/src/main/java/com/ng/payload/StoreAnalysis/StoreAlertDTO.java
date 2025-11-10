package com.ng.payload.StoreAnalysis;

import com.ng.payload.dto.BranchDTO;
import com.ng.payload.dto.ProductDTO;
import com.ng.payload.dto.RefundDTO;
import com.ng.payload.dto.UserDTO;
import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class StoreAlertDTO {
    private List<ProductDTO> lowStockAlerts;
    private List<BranchDTO> noSalesToday;
    private List<RefundDTO> refundSpikeAlerts;
    private List<UserDTO> inactiveCashiers;
}

