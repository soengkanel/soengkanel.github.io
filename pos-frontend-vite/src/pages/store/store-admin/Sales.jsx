import React, { useEffect, useState, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, LineChart, Line } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Search, Filter, Calendar, Download, Plus, Edit, Trash2, CreditCard, DollarSign, User, Store } from "lucide-react";
import {
  getStoreOverview as getStoreOverviewThunk,
  getDailySales as getDailySalesThunk,
  getSalesByPaymentMethod as getSalesByPaymentMethodThunk
} from "@/Redux Toolkit/features/storeAnalytics/storeAnalyticsThunks";
import { useToast } from "@/components/ui/use-toast";
import {
  getStoreOverview as getMockStoreOverview,
  getDailySales as getMockDailySales,
  getSalesByPaymentMethod as getMockSalesByPaymentMethod
} from "@/data/mockSales";

export default function Sales() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { userProfile } = useSelector((state) => state.user);
  const { store } = useSelector((state) => state.store);
  const {
    storeOverview: reduxStoreOverview,
    dailySales: reduxDailySales,
    salesByPaymentMethod: reduxSalesByPaymentMethod,
    loading
  } = useSelector((state) => state.storeAnalytics);
  const [showNewSaleDialog, setShowNewSaleDialog] = useState(false);

  // Use mock data if Redux data is empty
  const storeOverview = useMemo(() => {
    if (reduxStoreOverview && Object.keys(reduxStoreOverview).length > 0) {
      return reduxStoreOverview;
    }
    return getMockStoreOverview();
  }, [reduxStoreOverview]);

  const dailySales = useMemo(() => {
    if (reduxDailySales && reduxDailySales.length > 0) {
      return reduxDailySales;
    }
    return getMockDailySales().slice(-7); // Last 7 days
  }, [reduxDailySales]);

  const salesByPaymentMethod = useMemo(() => {
    if (reduxSalesByPaymentMethod && reduxSalesByPaymentMethod.length > 0) {
      return reduxSalesByPaymentMethod;
    }
    return getMockSalesByPaymentMethod();
  }, [reduxSalesByPaymentMethod]);

  useEffect(() => {
    if (userProfile?.id) {
      fetchSalesData();
    }
  }, [userProfile]);

  const fetchSalesData = async () => {
    try {
      await Promise.all([
        dispatch(getStoreOverviewThunk(userProfile.id)).unwrap(),
        dispatch(getDailySalesThunk(userProfile.id)).unwrap(),
        dispatch(getSalesByPaymentMethodThunk(userProfile.id)).unwrap(),
      ]);
    } catch (err) {
      // Silently fail and use mock data
      console.log("Using mock sales data");
    }
  };

  // Format currency - Cambodia Riel
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('km-KH', {
      style: 'currency',
      currency: 'KHR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  // Format percentage change
  const formatChange = (current, previous) => {
    if (!previous || previous === 0) return "+0%";
    const change = ((current - previous) / previous) * 100;
    const sign = change >= 0 ? "+" : "";
    return `${sign}${change.toFixed(1)}%`;
  };

  // Prepare chart data
  const dailySalesData = dailySales?.map(item => ({
    date: new Date(item.date)?.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    sales: item.totalAmount
  })) || [];

  const paymentMethodData = salesByPaymentMethod?.map(item => ({
    name: item.paymentMethod,
    value: item.totalAmount
  })) || [];

  const salesConfig = {
    sales: {
      label: "Sales",
      color: "#10b981",
    },
  };

  const paymentConfig = {
    value: {
      label: "Amount",
      color: "#10b981",
    },
  };

  console.log("sales daily", dailySales)

  const handleNewSale = () => {
    // Check if store has branches
    if (!store?.branches || store.branches.length === 0) {
      toast({
        title: "No Branches Available",
        description: "Please create a branch first to make a sale.",
        variant: "destructive",
      });
      return;
    }

    // If only one branch, navigate directly to cashier
    if (store.branches.length === 1) {
      // Navigate to cashier or POS for that branch
      toast({
        title: "Coming Soon",
        description: "POS functionality will be available soon. Please use the cashier interface.",
      });
      // You can uncomment this when cashier route is ready
      // navigate(`/cashier?branch=${store.branches[0].id}`);
    } else {
      // Multiple branches, show dialog to select branch
      setShowNewSaleDialog(true);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Sales Management</h1>
        <Button
          className="bg-emerald-600 hover:bg-emerald-700"
          onClick={handleNewSale}
        >
          <Plus className="mr-2 h-4 w-4" /> New Sale
        </Button>
      </div>

      {/* New Sale Dialog for Branch Selection */}
      <Dialog open={showNewSaleDialog} onOpenChange={setShowNewSaleDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Select Branch</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <p className="text-sm text-gray-600">Choose a branch to create a new sale:</p>
            <div className="space-y-2">
              {store?.branches?.map((branch) => (
                <Button
                  key={branch.id}
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => {
                    setShowNewSaleDialog(false);
                    toast({
                      title: "Coming Soon",
                      description: `POS for ${branch.name} will be available soon.`,
                    });
                    // navigate(`/cashier?branch=${branch.id}`);
                  }}
                >
                  <Store className="mr-2 h-4 w-4" />
                  {branch.name}
                  {branch.location && (
                    <span className="ml-2 text-xs text-gray-500">- {branch.location}</span>
                  )}
                </Button>
              ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Sales</p>
                <h3 className="text-2xl font-bold mt-1">
                  {loading ? (
                    <div className="h-8 w-20 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    formatCurrency(storeOverview?.totalSales || 0)
                  )}
                </h3>
                <p className="text-xs text-emerald-500 mt-1">
                  {loading ? (
                    <div className="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    formatChange(storeOverview?.totalSales, storeOverview?.previousPeriodSales)
                  )} from last week
                </p>
              </div>
              <div className="p-3 bg-emerald-100 rounded-full">
                <DollarSign className="w-8 h-8 text-emerald-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Orders Today</p>
                <h3 className="text-2xl font-bold mt-1">
                  {loading ? (
                    <div className="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    storeOverview?.todayOrders || 0
                  )}
                </h3>
                <p className="text-xs text-emerald-500 mt-1">
                  {loading ? (
                    <div className="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    formatChange(storeOverview?.todayOrders, storeOverview?.yesterdayOrders)
                  )} from yesterday
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Store className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Active Cashiers</p>
                <h3 className="text-2xl font-bold mt-1">
                  {loading ? (
                    <div className="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    storeOverview?.activeCashiers || 0
                  )}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {loading ? (
                    <div className="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    "Same as yesterday"
                  )}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <User className="w-8 h-8 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Avg. Order Value</p>
                <h3 className="text-2xl font-bold mt-1">
                  {loading ? (
                    <div className="h-8 w-20 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    formatCurrency(storeOverview?.averageOrderValue || 0)
                  )}
                </h3>
                <p className="text-xs text-emerald-500 mt-1">
                  {loading ? (
                    <div className="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
                  ) : (
                    formatChange(storeOverview?.averageOrderValue, storeOverview?.previousPeriodAverageOrderValue)
                  )} from last week
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <CreditCard className="w-8 h-8 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Daily Sales (Last 7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="mt-2 text-gray-500">Loading chart data...</p>
                </div>
              </div>
            ) : dailySalesData.length > 0 ? (
              <ChartContainer config={salesConfig}>
                <ResponsiveContainer width="100%" height={320}>
                  <LineChart data={dailySalesData}>
                    <XAxis
                      dataKey="date"
                      stroke="#888888"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      stroke="#888888"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `៛${value}`}
                    />
                    <ChartTooltip
                      content={({ active, payload }) => (
                        <ChartTooltipContent
                          active={active}
                          payload={payload}
                          formatter={(value) => [formatCurrency(value), "Sales"]}
                        />
                      )}
                    />
                    <Line
                      type="monotone"
                      dataKey="sales"
                      stroke="currentColor"
                      strokeWidth={2}
                      className="stroke-emerald-500"
                      activeDot={{ r: 8, fill: "#10b981" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
            ) : (
              <div className="h-80 flex items-center justify-center">
                <p className="text-gray-500">No sales data available</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Payment Methods</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="mt-2 text-gray-500">Loading chart data...</p>
                </div>
              </div>
            ) : paymentMethodData.length > 0 ? (
              <ChartContainer config={paymentConfig}>
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={paymentMethodData}>
                    <XAxis
                      dataKey="name"
                      stroke="#888888"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      stroke="#888888"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `៛${value}`}
                    />
                    <ChartTooltip
                      content={({ active, payload }) => (
                        <ChartTooltipContent
                          active={active}
                          payload={payload}
                          formatter={(value) => [formatCurrency(value), "Amount"]}
                        />
                      )}
                    />
                    <Bar
                      dataKey="value"
                      fill="currentColor"
                      radius={[4, 4, 0, 0]}
                      className="fill-emerald-500"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            ) : (
              <div className="h-80 flex items-center justify-center">
                <p className="text-gray-500">No payment data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    
    </div>
  );
}