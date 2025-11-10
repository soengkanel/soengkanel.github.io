// AdminDashboardServiceImpl.java
package com.ng.service.impl;

import com.ng.domain.StoreStatus;
import com.ng.payload.AdminAnalysis.DashboardSummaryDTO;
import com.ng.payload.AdminAnalysis.StoreRegistrationStatDTO;
import com.ng.payload.AdminAnalysis.StoreStatusDistributionDTO;
import com.ng.repository.StoreRepository;
import com.ng.service.AdminDashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
@RequiredArgsConstructor
public class AdminDashboardServiceImpl implements AdminDashboardService {

    private final StoreRepository storeRepository;

    @Override
    public DashboardSummaryDTO getDashboardSummary() {
        Long total = storeRepository.count();
        Long active = storeRepository.countByStatus(StoreStatus.ACTIVE);
        Long pending = storeRepository.countByStatus(StoreStatus.PENDING);
        Long blocked = storeRepository.countByStatus(StoreStatus.BLOCKED);

        return DashboardSummaryDTO.builder()
                .totalStores(total)
                .activeStores(active)
                .pendingStores(pending)
                .blockedStores(blocked)
                .build();
    }

    @Override
    public List<StoreRegistrationStatDTO> getLast7DayRegistrationStats() {
        LocalDateTime today = LocalDateTime.now();
        LocalDateTime sevenDaysAgo = today.minusDays(6);
        List<Object[]> rawStats = storeRepository.getStoreRegistrationStats(sevenDaysAgo);

        Map<String, Long> dataMap = new LinkedHashMap<>();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");

        // Initialize 0 counts for 7 days
        for (int i = 0; i < 7; i++) {
            LocalDateTime date = sevenDaysAgo.plusDays(i);
            dataMap.put(date.format(formatter), 0L);
        }

        for (Object[] row : rawStats) {
            LocalDateTime date = (LocalDateTime) row[0];
            Long count = (Long) row[1];
            dataMap.put(date.format(formatter), count);
        }

        List<StoreRegistrationStatDTO> result = new ArrayList<>();
        dataMap.forEach((date, count) -> result.add(
                StoreRegistrationStatDTO.builder().date(date).count(count).build()
        ));

        return result;
    }

    @Override
    public StoreStatusDistributionDTO getStoreStatusDistribution() {
        Long active = storeRepository.countByStatus(StoreStatus.ACTIVE);
        Long blocked = storeRepository.countByStatus(StoreStatus.BLOCKED);
        Long pending = storeRepository.countByStatus(StoreStatus.PENDING);

        return StoreStatusDistributionDTO.builder()
                .active(active)
                .blocked(blocked)
                .pending(pending)
                .build();
    }
}
