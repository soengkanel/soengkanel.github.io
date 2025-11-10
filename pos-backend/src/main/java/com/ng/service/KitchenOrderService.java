package com.ng.service;

import com.ng.domain.KitchenOrderStatus;
import com.ng.domain.KitchenStation;
import com.ng.modal.KitchenOrder;

import java.util.List;

public interface KitchenOrderService {

    KitchenOrder createKitchenOrder(Long orderId, KitchenStation station);

    KitchenOrder updateKitchenOrderStatus(Long kitchenOrderId, KitchenOrderStatus status);

    KitchenOrder getKitchenOrderById(Long id);

    List<KitchenOrder> getActiveOrders();

    List<KitchenOrder> getOrdersByStation(KitchenStation station);

    List<KitchenOrder> getPendingOrders();

    List<KitchenOrder> getReadyOrders();

    KitchenOrder startPreparation(Long kitchenOrderId);

    KitchenOrder completePreparation(Long kitchenOrderId);

    List<KitchenOrder> getDelayedOrders();

    void cancelKitchenOrder(Long kitchenOrderId);
}
