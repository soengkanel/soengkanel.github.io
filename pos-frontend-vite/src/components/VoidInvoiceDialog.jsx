import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

const VoidInvoiceDialog = ({ open, onOpenChange, order }) => {
  const { toast } = useToast();
  const [voidReason, setVoidReason] = useState("");
  const [voidNotes, setVoidNotes] = useState("");
  const [managerPassword, setManagerPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const voidReasons = [
    { value: "CUSTOMER_COMPLAINT", label: "Customer Complaint" },
    { value: "ENTRY_ERROR", label: "Order Entry Error" },
    { value: "WRONG_ORDER", label: "Wrong Order" },
    { value: "KITCHEN_ERROR", label: "Kitchen Error" },
    { value: "CUSTOMER_CANCELLATION", label: "Customer Cancellation" },
    { value: "PAYMENT_ISSUE", label: "Payment Issue" },
    { value: "DUPLICATE_ORDER", label: "Duplicate Order" },
    { value: "MANAGER_DISCRETION", label: "Manager Discretion" },
    { value: "SYSTEM_ERROR", label: "System Error" },
    { value: "OTHER", label: "Other" },
  ];

  const handleVoidInvoice = async () => {
    if (!voidReason) {
      toast({
        title: "Validation Error",
        description: "Please select a void reason",
        variant: "destructive",
      });
      return;
    }

    if (!voidNotes || voidNotes.trim().length < 10) {
      toast({
        title: "Validation Error",
        description: "Please provide detailed notes (minimum 10 characters)",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/void-invoice", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add auth token if needed
        },
        body: JSON.stringify({
          orderId: order.id,
          voidReason: voidReason,
          voidNotes: voidNotes,
          // managerPassword: managerPassword, // Optional
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Failed to void invoice");
      }

      const voidedOrder = await response.json();

      toast({
        title: "Invoice Voided",
        description: `Order #${order.id} has been voided successfully`,
      });

      // Reset form
      setVoidReason("");
      setVoidNotes("");
      setManagerPassword("");
      onOpenChange(false);

      // Callback to refresh data
      if (onOpenChange) {
        onOpenChange(false);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!order) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-red-600 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Void Invoice - Order #{order.id}
          </DialogTitle>
          <DialogDescription>
            This action will permanently void this invoice. Please provide a reason and detailed explanation.
          </DialogDescription>
        </DialogHeader>

        <Alert variant="destructive">
          <AlertDescription>
            <strong>Warning:</strong> Voiding an invoice is irreversible and will be logged in the audit trail.
          </AlertDescription>
        </Alert>

        <div className="space-y-4">
          {/* Order Summary */}
          <div className="bg-muted p-4 rounded-lg">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">Order ID:</span>
                <span className="ml-2 font-medium">#{order.id}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Total Amount:</span>
                <span className="ml-2 font-medium">
                  ៛{order.totalAmount?.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Created:</span>
                <span className="ml-2 font-medium">
                  {new Date(order.createdAt).toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Status:</span>
                <span className="ml-2 font-medium">{order.status}</span>
              </div>
            </div>
          </div>

          {/* Void Reason */}
          <div className="space-y-2">
            <Label htmlFor="voidReason">
              Void Reason <span className="text-red-500">*</span>
            </Label>
            <Select value={voidReason} onValueChange={setVoidReason}>
              <SelectTrigger>
                <SelectValue placeholder="Select reason for void" />
              </SelectTrigger>
              <SelectContent>
                {voidReasons.map((reason) => (
                  <SelectItem key={reason.value} value={reason.value}>
                    {reason.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Void Notes */}
          <div className="space-y-2">
            <Label htmlFor="voidNotes">
              Detailed Explanation <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="voidNotes"
              value={voidNotes}
              onChange={(e) => setVoidNotes(e.target.value)}
              placeholder="Provide a detailed explanation for voiding this invoice (minimum 10 characters)"
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              {voidNotes.length}/1000 characters
            </p>
          </div>

          {/* Manager Password (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="managerPassword">
              Manager Password (Optional)
            </Label>
            <Input
              id="managerPassword"
              type="password"
              value={managerPassword}
              onChange={(e) => setManagerPassword(e.target.value)}
              placeholder="Enter manager password for approval"
            />
            <p className="text-xs text-muted-foreground">
              Required for high-value voids or based on store policy
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleVoidInvoice}
            disabled={isLoading}
          >
            {isLoading ? "Voiding..." : "Void Invoice"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default VoidInvoiceDialog;
