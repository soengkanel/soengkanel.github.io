import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowRightLeft, Merge, Split, Table } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

const TableManagement = () => {
  const { toast } = useToast();
  const [showChangeTableDialog, setShowChangeTableDialog] = useState(false);
  const [showMergeDialog, setShowMergeDialog] = useState(false);
  const [showSplitDialog, setShowSplitDialog] = useState(false);

  // Sample data - replace with actual API calls
  const [tables] = useState([
    { id: 1, tableNumber: "T1", status: "OCCUPIED", capacity: 4, currentOrder: { id: 101, totalAmount: 150.00, items: [] } },
    { id: 2, tableNumber: "T2", status: "OCCUPIED", capacity: 2, currentOrder: { id: 102, totalAmount: 75.50, items: [] } },
    { id: 3, tableNumber: "T3", status: "AVAILABLE", capacity: 6, currentOrder: null },
    { id: 4, tableNumber: "T4", status: "OCCUPIED", capacity: 4, currentOrder: { id: 103, totalAmount: 200.00, items: [] } },
    { id: 5, tableNumber: "T5", status: "AVAILABLE", capacity: 2, currentOrder: null },
  ]);

  const [selectedOrder, setSelectedOrder] = useState(null);
  const [newTableId, setNewTableId] = useState(null);
  const [selectedTables, setSelectedTables] = useState([]);
  const [splitGroups, setSplitGroups] = useState([]);

  // Change Table Handler
  const handleChangeTable = async () => {
    if (!selectedOrder || !newTableId) {
      toast({
        title: "Error",
        description: "Please select an order and target table",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch("/api/table-management/change-table", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          orderId: selectedOrder.id,
          newTableId: newTableId,
        }),
      });

      if (!response.ok) throw new Error("Failed to change table");

      toast({
        title: "Success",
        description: `Order moved to table ${newTableId}`,
      });

      setShowChangeTableDialog(false);
      setSelectedOrder(null);
      setNewTableId(null);
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Merge Tables Handler
  const handleMergeTables = async () => {
    if (selectedTables.length < 2) {
      toast({
        title: "Error",
        description: "Please select at least 2 tables to merge",
        variant: "destructive",
      });
      return;
    }

    try {
      const orderIds = selectedTables.map(t => t.currentOrder.id);
      const targetTableId = selectedTables[0].id;

      const response = await fetch("/api/table-management/merge-tables", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sourceOrderIds: orderIds,
          targetTableId: targetTableId,
        }),
      });

      if (!response.ok) throw new Error("Failed to merge tables");

      toast({
        title: "Success",
        description: `${selectedTables.length} tables merged successfully`,
      });

      setShowMergeDialog(false);
      setSelectedTables([]);
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Split Bill Handler
  const handleSplitBill = async () => {
    if (!selectedOrder || splitGroups.length < 2) {
      toast({
        title: "Error",
        description: "Please create at least 2 split groups",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch("/api/table-management/split-bill", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          originalOrderId: selectedOrder.id,
          splitGroups: splitGroups,
        }),
      });

      if (!response.ok) throw new Error("Failed to split bill");

      const splitOrders = await response.json();

      toast({
        title: "Success",
        description: `Bill split into ${splitOrders.length} orders`,
      });

      setShowSplitDialog(false);
      setSelectedOrder(null);
      setSplitGroups([]);
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "AVAILABLE":
        return "bg-green-500";
      case "OCCUPIED":
        return "bg-red-500";
      case "RESERVED":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Table Management</h1>
        <div className="space-x-2">
          <Button
            onClick={() => setShowChangeTableDialog(true)}
            variant="outline"
          >
            <ArrowRightLeft className="w-4 h-4 mr-2" />
            Change Table
          </Button>
          <Button
            onClick={() => setShowMergeDialog(true)}
            variant="outline"
          >
            <Merge className="w-4 h-4 mr-2" />
            Merge Tables
          </Button>
          <Button
            onClick={() => setShowSplitDialog(true)}
            variant="outline"
          >
            <Split className="w-4 h-4 mr-2" />
            Split Bill
          </Button>
        </div>
      </div>

      {/* Table Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {tables.map((table) => (
          <Card key={table.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-center">
                <CardTitle className="flex items-center">
                  <Table className="w-5 h-5 mr-2" />
                  {table.tableNumber}
                </CardTitle>
                <Badge className={getStatusColor(table.status)}>
                  {table.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  Capacity: {table.capacity} guests
                </p>
                {table.currentOrder && (
                  <>
                    <p className="text-sm font-medium">
                      Order #{table.currentOrder.id}
                    </p>
                    <p className="text-lg font-bold text-green-600">
                      ៛{table.currentOrder.totalAmount.toFixed(2)}
                    </p>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Change Table Dialog */}
      <Dialog open={showChangeTableDialog} onOpenChange={setShowChangeTableDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Table</DialogTitle>
            <DialogDescription>
              Move an order to a different table
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Select Order</label>
              <Select onValueChange={(value) => {
                const table = tables.find(t => t.currentOrder?.id === parseInt(value));
                setSelectedOrder(table?.currentOrder);
              }}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose an order" />
                </SelectTrigger>
                <SelectContent>
                  {tables.filter(t => t.currentOrder).map((table) => (
                    <SelectItem key={table.currentOrder.id} value={table.currentOrder.id.toString()}>
                      {table.tableNumber} - Order #{table.currentOrder.id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium">New Table</label>
              <Select onValueChange={(value) => setNewTableId(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose target table" />
                </SelectTrigger>
                <SelectContent>
                  {tables.filter(t => t.status === "AVAILABLE").map((table) => (
                    <SelectItem key={table.id} value={table.id.toString()}>
                      {table.tableNumber} - {table.capacity} guests
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowChangeTableDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleChangeTable}>Change Table</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Merge Tables Dialog */}
      <Dialog open={showMergeDialog} onOpenChange={setShowMergeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Merge Tables</DialogTitle>
            <DialogDescription>
              Combine multiple table orders into one
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2">
            {tables.filter(t => t.currentOrder).map((table) => (
              <div key={table.id} className="flex items-center space-x-2">
                <Checkbox
                  id={`merge-${table.id}`}
                  checked={selectedTables.includes(table)}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setSelectedTables([...selectedTables, table]);
                    } else {
                      setSelectedTables(selectedTables.filter(t => t.id !== table.id));
                    }
                  }}
                />
                <label htmlFor={`merge-${table.id}`} className="text-sm font-medium">
                  {table.tableNumber} - Order #{table.currentOrder.id} (៛{table.currentOrder.totalAmount})
                </label>
              </div>
            ))}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMergeDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleMergeTables}>
              Merge {selectedTables.length} Tables
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Split Bill Dialog */}
      <Dialog open={showSplitDialog} onOpenChange={setShowSplitDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Split Bill</DialogTitle>
            <DialogDescription>
              Divide a table order into multiple bills
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Select Order to Split</label>
              <Select onValueChange={(value) => {
                const table = tables.find(t => t.currentOrder?.id === parseInt(value));
                setSelectedOrder(table?.currentOrder);
              }}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose an order" />
                </SelectTrigger>
                <SelectContent>
                  {tables.filter(t => t.currentOrder).map((table) => (
                    <SelectItem key={table.currentOrder.id} value={table.currentOrder.id.toString()}>
                      {table.tableNumber} - Order #{table.currentOrder.id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedOrder && (
              <div className="border rounded-lg p-4">
                <p className="text-sm text-muted-foreground mb-2">
                  Create split groups by selecting items from the order
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setSplitGroups([...splitGroups, { orderItemIds: [] }])}
                >
                  + Add Split Group
                </Button>
                <p className="text-sm mt-2">
                  Total groups: {splitGroups.length}
                </p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSplitDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSplitBill}>
              Split into {splitGroups.length} Bills
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TableManagement;
