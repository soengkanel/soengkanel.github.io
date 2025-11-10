package com.ng.service;



import com.ng.payload.AdminAnalysis.DashboardSummaryDTO;
import com.ng.payload.AdminAnalysis.StoreRegistrationStatDTO;
import com.ng.payload.AdminAnalysis.StoreStatusDistributionDTO;


import java.util.List;

public interface AdminDashboardService {

    DashboardSummaryDTO getDashboardSummary();

    List<StoreRegistrationStatDTO> getLast7DayRegistrationStats();

    StoreStatusDistributionDTO getStoreStatusDistribution();
}
