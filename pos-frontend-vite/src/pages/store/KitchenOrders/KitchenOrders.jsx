import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { ChefHat, Clock, Check, X, AlertCircle, RefreshCw, Grid3x3, List } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { mockKitchenOrders } from "../../../data/mockFnBData";

export default function KitchenOrders() {
  const { store } = useSelector((state) => state.store);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStation, setSelectedStation] = useState("all");
  const [viewMode, setViewMode] = useState("table"); // 'grid' or 'table'

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchKitchenOrders = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/kitchen-orders/branch/${branchId}`);
        // const data = await response.json();

        // Use imported mock data
        setOrders(mockKitchenOrders);
      } catch (error) {
        console.error("Error fetching kitchen orders:", error);
      } finally {
        setLoading(false);
      }
    };

    if (store?.id) {
      fetchKitchenOrders();
    }
  }, [store?.id]);

  // Filter orders by station
  const filteredOrders = orders.filter((order) => {
    if (selectedStation === "all") return true;
    return order.items.some((item) => item.station === selectedStation);
  });

  // Get unique stations
  const stations = ["all", ...new Set(orders.flatMap((o) => o.items.map((i) => i.station)))];

  // Stats
  const pendingOrders = orders.filter((o) => o.status === "PENDING").length;
  const preparingOrders = orders.filter((o) => o.status === "PREPARING").length;
  const readyOrders = orders.filter((o) => o.status === "READY").length;

  const getStatusBadge = (status) => {
    const badges = {
      PENDING: { label: "Pending", class: "bg-yellow-100 text-yellow-800", icon: <Clock className="w-3 h-3" /> },
      PREPARING: { label: "Preparing", class: "bg-blue-100 text-blue-800", icon: <ChefHat className="w-3 h-3" /> },
      READY: { label: "Ready", class: "bg-green-100 text-green-800", icon: <Check className="w-3 h-3" /> },
      COMPLETED: { label: "Completed", class: "bg-gray-100 text-gray-800", icon: <Check className="w-3 h-3" /> },
    };
    return badges[status] || { label: status, class: "bg-gray-100 text-gray-800", icon: null };
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      URGENT: { label: "Urgent", class: "bg-red-100 text-red-800" },
      HIGH: { label: "High", class: "bg-orange-100 text-orange-800" },
      NORMAL: { label: "Normal", class: "bg-gray-100 text-gray-800" },
    };
    return badges[priority] || badges.NORMAL;
  };

  const getItemStatusBadge = (status) => {
    const badges = {
      PENDING: "bg-yellow-100 text-yellow-800",
      PREPARING: "bg-blue-100 text-blue-800",
      READY: "bg-green-100 text-green-800",
    };
    return badges[status] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading kitchen orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <ChefHat className="w-8 h-8 text-primary" />
            Kitchen Display System
          </h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage active kitchen orders
          </p>
        </div>
        <Button className="flex items-center gap-2" variant="outline">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Orders</p>
                <p className="text-2xl font-bold text-gray-900">{orders.length}</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-full">
                <ChefHat className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">{pendingOrders}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Preparing</p>
                <p className="text-2xl font-bold text-blue-600">{preparingOrders}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <ChefHat className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Ready</p>
                <p className="text-2xl font-bold text-green-600">{readyOrders}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <Check className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Station Filter and View Toggle */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-semibold text-gray-700">Filter by Station:</span>
              <div className="flex flex-wrap gap-2">
                {stations.map((station) => (
                  <Button
                    key={station}
                    variant={selectedStation === station ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedStation(station)}
                  >
                    {station === "all" ? "All Stations" : station}
                  </Button>
                ))}
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex gap-2">
              <Button
                variant={viewMode === "grid" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="flex items-center gap-2"
              >
                <Grid3x3 className="w-4 h-4" />
                Grid
              </Button>
              <Button
                variant={viewMode === "table" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("table")}
                className="flex items-center gap-2"
              >
                <List className="w-4 h-4" />
                Table
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Kitchen Orders Display */}
      {filteredOrders.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <ChefHat className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No active orders
            </h3>
            <p className="text-gray-600">
              Kitchen orders will appear here when customers place orders
            </p>
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        // Grid View
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredOrders.map((order) => {
            const statusBadge = getStatusBadge(order.status);
            const priorityBadge = getPriorityBadge(order.priority);
            return (
              <Card
                key={order.id}
                className={`hover:shadow-lg transition-shadow ${
                  order.priority === "URGENT" ? "border-red-300 border-2" : ""
                }`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-xl font-bold">
                        {order.orderNumber}
                      </CardTitle>
                      <p className="text-sm text-gray-600 mt-1">
                        Table: <span className="font-semibold">{order.tableNumber}</span>
                      </p>
                    </div>
                    <div className="text-right space-y-2">
                      <Badge className={statusBadge.class}>
                        {statusBadge.icon}
                        <span className="ml-1">{statusBadge.label}</span>
                      </Badge>
                      {order.priority !== "NORMAL" && (
                        <Badge className={priorityBadge.class}>
                          {priorityBadge.label}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Time Info */}
                  <div className="flex items-center justify-between text-sm bg-gray-50 p-3 rounded-lg">
                    <span className="text-gray-600 flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      Order Time
                    </span>
                    <span className="font-semibold">{order.orderTime}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Elapsed Time</span>
                    <span
                      className={`font-semibold ${
                        order.elapsedTime > 15 ? "text-red-600" : "text-gray-900"
                      }`}
                    >
                      {order.elapsedTime} min
                    </span>
                  </div>

                  {/* Order Items */}
                  <div className="space-y-2 pt-2 border-t">
                    <p className="text-sm font-semibold text-gray-700">Items:</p>
                    {order.items.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between bg-gray-50 p-2 rounded"
                      >
                        <div className="flex-1">
                          <p className="text-sm font-medium">{item.name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {item.station}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              Qty: {item.quantity}
                            </span>
                          </div>
                        </div>
                        <Badge className={getItemStatusBadge(item.status)}>
                          {item.status}
                        </Badge>
                      </div>
                    ))}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    {order.status === "PENDING" && (
                      <Button size="sm" className="flex-1">
                        <ChefHat className="w-4 h-4 mr-1" />
                        Start Preparing
                      </Button>
                    )}
                    {order.status === "PREPARING" && (
                      <Button size="sm" className="flex-1 bg-green-600 hover:bg-green-700">
                        <Check className="w-4 h-4 mr-1" />
                        Mark Ready
                      </Button>
                    )}
                    {order.status === "READY" && (
                      <Button size="sm" className="flex-1" variant="secondary">
                        <Check className="w-4 h-4 mr-1" />
                        Complete Order
                      </Button>
                    )}
                    <Button size="sm" variant="outline" className="text-red-600">
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  {order.elapsedTime > 15 && (
                    <div className="flex items-center gap-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                      <AlertCircle className="w-4 h-4" />
                      <span>Order taking longer than expected</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        // Table View
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Order Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Items
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredOrders.map((order) => {
                    const statusBadge = getStatusBadge(order.status);
                    const priorityBadge = getPriorityBadge(order.priority);
                    return (
                      <tr
                        key={order.id}
                        className={`hover:bg-gray-50 ${
                          order.priority === "URGENT" ? "bg-red-50" : ""
                        }`}
                      >
                        <td className="px-6 py-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <ChefHat className="w-5 h-5 text-primary" />
                              <span className="text-sm font-semibold text-gray-900">
                                {order.orderNumber}
                              </span>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">
                              Table: {order.tableNumber}
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="space-y-1">
                            {order.items.map((item) => (
                              <div key={item.id} className="flex items-center gap-2">
                                <span className="text-sm text-gray-900">
                                  {item.quantity}x {item.name}
                                </span>
                                <Badge variant="outline" className="text-xs">
                                  {item.station}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="flex items-center gap-1 text-sm text-gray-900">
                              <Clock className="w-4 h-4" />
                              {order.orderTime}
                            </div>
                            <p
                              className={`text-sm mt-1 ${
                                order.elapsedTime > 15 ? "text-red-600 font-semibold" : "text-gray-500"
                              }`}
                            >
                              {order.elapsedTime} min elapsed
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge className={statusBadge.class}>
                            {statusBadge.icon}
                            <span className="ml-1">{statusBadge.label}</span>
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {order.priority !== "NORMAL" && (
                            <Badge className={priorityBadge.class}>
                              {priorityBadge.label}
                            </Badge>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            {order.status === "PENDING" && (
                              <Button size="sm">
                                <ChefHat className="w-4 h-4 mr-1" />
                                Start
                              </Button>
                            )}
                            {order.status === "PREPARING" && (
                              <Button size="sm" className="bg-green-600 hover:bg-green-700">
                                <Check className="w-4 h-4 mr-1" />
                                Ready
                              </Button>
                            )}
                            {order.status === "READY" && (
                              <Button size="sm" variant="secondary">
                                <Check className="w-4 h-4 mr-1" />
                                Complete
                              </Button>
                            )}
                            <Button size="sm" variant="outline" className="text-red-600">
                              <X className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
