import React from "react";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

const BasicInformation = ({ storeData }) => {
  // Handle both brand and name fields
  const storeName = storeData.brand || storeData.name || "N/A";
  // Support both 'businessType' and legacy 'storeType'/'type' fields
  const businessType = storeData.businessType || storeData.storeType || storeData.type || "N/A";
  const description = storeData.description || "No description provided";

  // Get friendly label for business type
  const getBusinessTypeLabel = (type) => {
    const labels = {
      FNB: "Food & Beverage",
      RETAIL: "Retail",
      HYBRID: "Hybrid (F&B + Retail)"
    };
    return labels[type] || type;
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
      <div className="space-y-4">
        <div>
          <Label className="text-sm text-muted-foreground">Store Name</Label>
          <p className="text-base font-medium">{storeName}</p>
        </div>
        <div>
          <Label className="text-sm text-muted-foreground">Business Type</Label>
          <Badge variant="secondary" className="mt-1">
            {getBusinessTypeLabel(businessType)}
          </Badge>
        </div>
        <div>
          <Label className="text-sm text-muted-foreground">Description</Label>
          <p className="text-base">{description}</p>
        </div>
      </div>
    </div>
  );
};

export default BasicInformation; 