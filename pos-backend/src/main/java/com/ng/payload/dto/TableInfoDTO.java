package com.ng.payload.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TableInfoDTO {
    private Long tableId;
    private String tableNumber;
    private String location;
    private Long branchId;
    private String branchName;
    private String branchPhone;
    private String branchAddress;
    private Boolean isActive;
}
