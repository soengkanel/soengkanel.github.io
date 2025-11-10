import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AlertTriangle, Download, Search } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

const VoidInvoiceReport = () => {
  const { toast } = useToast();
  const [voidedOrders, setVoidedOrders] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const fetchVoidedOrders = async () => {
    if (!startDate || !endDate) {
      toast({
        title: "Validation Error",
        description: "Please select start and end dates",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const branchId = 1; // TODO: Get from context/state

      const response = await fetch(
        `/api/void-invoice/branch/${branchId}?startDate=${startDate}&endDate=${endDate}`
      );

      if (!response.ok) throw new Error("Failed to fetch voided orders");

      const data = await response.json();
      setVoidedOrders(data);

      // Fetch statistics
      const statsResponse = await fetch(
        `/api/void-invoice/statistics/branch/${branchId}?startDate=${startDate}&endDate=${endDate}`
      );

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    // CSV export logic
    const csv = [
      ["Order ID", "Total Amount", "Voided At", "Reason", "Notes", "Voided By"],
      ...voidedOrders.map((order) => [
        order.id,
        order.totalAmount,
        new Date(order.voidedAt).toLocaleString(),
        order.voidReason,
        order.voidNotes,
        order.voidedByName,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `voided-invoices-${startDate}-to-${endDate}.csv`;
    a.click();
  };

  const getReasonBadgeColor = (reason) => {
    const colors = {
      CUSTOMER_COMPLAINT: "bg-red-500",
      ENTRY_ERROR: "bg-yellow-500",
      WRONG_ORDER: "bg-orange-500",
      KITCHEN_ERROR: "bg-purple-500",
      CUSTOMER_CANCELLATION: "bg-blue-500",
      PAYMENT_ISSUE: "bg-pink-500",
      DUPLICATE_ORDER: "bg-indigo-500",
      MANAGER_DISCRETION: "bg-green-500",
      SYSTEM_ERROR: "bg-gray-500",
      OTHER: "bg-slate-500",
    };
    return colors[reason] || "bg-gray-500";
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold flex items-center">
          <AlertTriangle className="w-8 h-8 mr-2 text-red-600" />
          Voided Invoice Report
        </h1>
        <Button onClick={exportToCSV} disabled={voidedOrders.length === 0}>
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Date Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filter by Date Range</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="text-sm font-medium">Start Date</label>
              <Input
                type="datetime-local"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium">End Date</label>
              <Input
                type="datetime-local"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <Button onClick={fetchVoidedOrders} disabled={loading} className="mt-6">
              <Search className="w-4 h-4 mr-2" />
              {loading ? "Loading..." : "Search"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Voided</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.totalVoidedOrders}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                ៛{statistics.totalVoidedAmount?.toFixed(2)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Top Reason</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-medium">
                {Object.entries(statistics.voidsByReason || {}).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Impact</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-medium">
                {((statistics.totalVoidedOrders / (statistics.totalVoidedOrders + 100)) * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Voided Orders Table */}
      <Card>
        <CardHeader>
          <CardTitle>Voided Invoices</CardTitle>
        </CardHeader>
        <CardContent>
          {voidedOrders.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No voided invoices found for the selected date range
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order ID</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Voided At</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead>Voided By</TableHead>
                  <TableHead>Approved By</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {voidedOrders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell className="font-medium">#{order.id}</TableCell>
                    <TableCell className="text-red-600 font-semibold">
                      ៛{order.totalAmount?.toFixed(2)}
                    </TableCell>
                    <TableCell>
                      {new Date(order.voidedAt).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge className={getReasonBadgeColor(order.voidReason)}>
                        {order.voidReason?.replace(/_/g, " ")}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {order.voidNotes}
                    </TableCell>
                    <TableCell>{order.voidedByName}</TableCell>
                    <TableCell>
                      {order.voidApprovedByName || "-"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VoidInvoiceReport;
