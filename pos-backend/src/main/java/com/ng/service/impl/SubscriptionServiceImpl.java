package com.ng.service.impl;


import com.ng.domain.PaymentStatus;
import com.ng.domain.SubscriptionStatus;
import com.ng.modal.Store;
import com.ng.modal.Subscription;
import com.ng.modal.SubscriptionPlan;
//import com.ng.payload.SubscriptionDTO;
import com.ng.repository.StoreRepository;
import com.ng.repository.SubscriptionPlanRepository;
import com.ng.repository.SubscriptionRepository;
import com.ng.service.SubscriptionService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
public class SubscriptionServiceImpl implements SubscriptionService {

    private final SubscriptionRepository subscriptionRepository;
    private final StoreRepository storeRepository;

    private final SubscriptionPlanRepository planRepository;

    @Override
    public Subscription createSubscription(Long storeId,
                                           Long planId,
                                           String gateway,
                                           String transactionId) {
        Store store = storeRepository.findById(storeId)
                .orElseThrow(() -> new EntityNotFoundException("Store not found"));

        SubscriptionPlan plan = planRepository.findById(planId)
                .orElseThrow(() -> new EntityNotFoundException(
                        "Subscription Plan not found"
                ));

        Subscription sub = Subscription.builder()
                .store(store)
                .plan(plan)
                .startDate(LocalDate.now())
                .endDate(LocalDate.now().plusMonths(1)) // 🔁 use plan billing cycle in future
                .status(SubscriptionStatus.ACTIVE)
                .paymentStatus(PaymentStatus.PENDING)
                .paymentGateway(gateway)
                .transactionId(transactionId)
                .build();
        return subscriptionRepository.save(sub);
    }

    @Override
    public Subscription upgradeSubscription(Long storeId,
                                            Long planId, String gateway,
                                            String transactionId) {
        Store store = storeRepository.findById(storeId)
                .orElseThrow(() -> new EntityNotFoundException("Store not found"));

        SubscriptionPlan plan = planRepository.findById(planId)
                .orElseThrow(() -> new EntityNotFoundException(
                        "Subscription Plan not found"
                ));

        List<Subscription> activeSub=subscriptionRepository.findByStoreAndStatus(store,
                SubscriptionStatus.ACTIVE);

        for (Subscription sub : activeSub) {
            sub.setStatus(SubscriptionStatus.CANCELLED);
            subscriptionRepository.save(sub);
        }


        Subscription sub = Subscription.builder()
                .store(store)
                .plan(plan)
                .startDate(LocalDate.now())
                .endDate(LocalDate.now().plusMonths(1))
                .status(SubscriptionStatus.ACTIVE)
                .paymentStatus(PaymentStatus.SUCCESS)
                .paymentGateway(gateway)
                .transactionId(transactionId)
                .build();
        return subscriptionRepository.save(sub);
    }

    @Override
    public Subscription activateSubscription(Long subscriptionId) {
        Subscription sub = subscriptionRepository.findById(subscriptionId)
                .orElseThrow(() -> new RuntimeException("Subscription not found"));
        sub.setStatus(SubscriptionStatus.ACTIVE);
        sub.setPaymentStatus(PaymentStatus.SUCCESS);
        return subscriptionRepository.save(sub);
    }

    @Override
    public Subscription cancelSubscription(Long subscriptionId) {
        Subscription sub = subscriptionRepository.findById(subscriptionId)
                .orElseThrow(() -> new RuntimeException("Subscription not found"));
        sub.setStatus(SubscriptionStatus.CANCELLED);
        return subscriptionRepository.save(sub);
    }

    @Override
    public void expirePastSubscriptions() {
        List<Subscription> all = subscriptionRepository.findAll();
        all.stream()
                .filter(s -> s.getEndDate().isBefore(LocalDate.now()) && s.getStatus() != SubscriptionStatus.EXPIRED)
                .forEach(s -> {
                    s.setStatus(SubscriptionStatus.EXPIRED);
                    subscriptionRepository.save(s);
                });
    }

    @Override
    public Subscription updatePaymentStatus(Long subscriptionId, PaymentStatus status) {
        Subscription sub = subscriptionRepository.findById(subscriptionId)
                .orElseThrow(() -> new RuntimeException("Subscription not found"));
        sub.setPaymentStatus(status);
        return subscriptionRepository.save(sub);
    }

    @Override
    public List<Subscription> getSubscriptionsByStore(
            Long storeId,
            SubscriptionStatus status) {
        Store store = storeRepository.findById(storeId).orElseThrow(
                () -> new EntityNotFoundException("Store not found")
        );
        if (status != null) {
            return subscriptionRepository.findByStoreAndStatus(store, status);
        }
        return subscriptionRepository.findByStore(store);
    }

    @Override
    public List<Subscription> getAllSubscriptions(SubscriptionStatus status) {
        if (status != null) {
            return subscriptionRepository.findByStatus(status);
        }
        return subscriptionRepository.findAll();
    }

    @Override
    public List<Subscription> getExpiringSubscriptionsWithin(int days) {
        LocalDate today = LocalDate.now();
        LocalDate future = today.plusDays(days);
        return subscriptionRepository.findByEndDateBetween(today, future);
    }

    @Override
    public Long countByStatus(SubscriptionStatus status) {
        return subscriptionRepository.countByStatus(status);
    }
}
