import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Building2, Plus, MapPin, Phone, Users } from "lucide-react";
import { useNavigate } from "react-router";

const BranchesSection = ({ storeData }) => {
  const navigate = useNavigate();
  const totalBranches = storeData?.totalBranches || 0;

  const getBusinessTypeLabel = (type) => {
    const labels = {
      FNB: "F&B",
      RETAIL: "Retail",
      HYBRID: "Hybrid"
    };
    return labels[type] || type;
  };

  const getBusinessTypeBadgeClass = (type) => {
    const classes = {
      FNB: "bg-orange-100 text-orange-800 border-orange-200",
      RETAIL: "bg-blue-100 text-blue-800 border-blue-200",
      HYBRID: "bg-purple-100 text-purple-800 border-purple-200"
    };
    return classes[type] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Branches</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Manage all branches under this store
            </p>
          </div>
          <Button
            className="bg-emerald-600 hover:bg-emerald-700"
            onClick={() => navigate("/store/branches")}
          >
            <Building2 className="h-4 w-4 mr-2" />
            View All Branches
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Branch Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 border rounded-lg">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Building2 className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalBranches}</p>
                <p className="text-sm text-muted-foreground">Total Branches</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 border rounded-lg">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium">Business Type</p>
                <Badge
                  variant="outline"
                  className={`mt-1 ${getBusinessTypeBadgeClass(storeData?.businessType)}`}
                >
                  {getBusinessTypeLabel(storeData?.businessType)}
                </Badge>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 border rounded-lg">
              <div className="p-2 bg-purple-100 rounded-lg">
                <MapPin className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium">All branches inherit</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Same business type as store
                </p>
              </div>
            </div>
          </div>

          {/* Information Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Building2 className="h-5 w-5 text-blue-600" />
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-blue-900 mb-1">
                  One Store, Many Branches
                </h4>
                <p className="text-sm text-blue-700">
                  This store has <span className="font-semibold">{totalBranches} branch{totalBranches !== 1 ? 'es' : ''}</span>.
                  All branches automatically inherit the <span className="font-semibold">{getBusinessTypeLabel(storeData?.businessType)}</span> business
                  type from the parent store. This ensures consistent capabilities across all locations.
                </p>
                <Button
                  variant="link"
                  className="text-blue-700 hover:text-blue-800 p-0 h-auto mt-2"
                  onClick={() => navigate("/store/branches")}
                >
                  Manage branches →
                </Button>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              onClick={() => navigate("/store/branches")}
              className="flex-1"
            >
              <Building2 className="h-4 w-4 mr-2" />
              View All Branches
            </Button>
            <Button
              className="flex-1 bg-emerald-600 hover:bg-emerald-700"
              onClick={() => navigate("/store/branches")}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add New Branch
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default BranchesSection;
