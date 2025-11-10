import React, { useMemo, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Edit, Trash2, MapPin, Phone, Users, Loader2, Building2, Clock, Store } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { deleteBranch, getAllBranchesByStore } from "@/Redux Toolkit/features/branch/branchThunks";
import { findStoreEmployees } from "@/Redux Toolkit/features/employee/employeeThunks";
import { mockEmployees } from "@/data/mockEmployees";

const BranchTable = ({ branches, loading, onEdit }) => {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { employees: reduxEmployees } = useSelector((state) => state.employee);

  // Get store's business type for fallback
  // Store uses 'businessType' field
  const storeBusinessType = store?.businessType || "RETAIL";

  // Fetch employees when component mounts
  useEffect(() => {
    const jwt = localStorage.getItem("jwt");
    if (store?.id && jwt) {
      dispatch(findStoreEmployees({ storeId: store.id, jwt }));
    }
  }, [dispatch, store?.id]);

  // Use Redux employees if available, otherwise use mock data
  const employees = useMemo(() => {
    return reduxEmployees && reduxEmployees.length > 0
      ? reduxEmployees
      : mockEmployees;
  }, [reduxEmployees]);

  // Helper function to get manager name by ID
  const getManagerName = (managerId) => {
    if (!managerId) return "Not Assigned";
    const manager = employees.find(emp => emp.id === managerId);
    return manager ? manager.fullName : "Not Assigned";
  };

  const handleDeleteBranch = async (id) => {
    try {
      const jwt = localStorage.getItem("jwt");
      if (!id || !jwt) {
        toast({
          title: "Error",
          description: "Branch ID or authentication JWT missing",
          variant: "destructive",
        });
        return;
      }

      await dispatch(deleteBranch({ id, jwt })).unwrap();

      toast({
        title: "Success",
        description: "Branch deleted successfully",
      });

      // Refresh branches list
      dispatch(getAllBranchesByStore({ storeId: store.id, jwt }));
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete branch",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      ACTIVE: { label: "Active", className: "bg-green-100 text-green-800 border-green-200" },
      COMING_SOON: { label: "Coming Soon", className: "bg-blue-100 text-blue-800 border-blue-200" },
      UNDER_MAINTENANCE: { label: "Maintenance", className: "bg-yellow-100 text-yellow-800 border-yellow-200" },
      CLOSED: { label: "Closed", className: "bg-red-100 text-red-800 border-red-200" }
    };
    return statusConfig[status] || statusConfig.ACTIVE;
  };

  const getBusinessTypeBadge = (businessType) => {
    const typeConfig = {
      FNB: { label: "F&B", className: "bg-orange-100 text-orange-800 border-orange-200" },
      RETAIL: { label: "Retail", className: "bg-blue-100 text-blue-800 border-blue-200" },
      HYBRID: { label: "Hybrid", className: "bg-purple-100 text-purple-800 border-purple-200" }
    };
    // If businessType is missing, fallback to store's business type
    return typeConfig[businessType] || typeConfig[storeBusinessType] || typeConfig.RETAIL;
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Branch Details</TableHead>
          <TableHead>Store</TableHead>
          <TableHead>Location</TableHead>
          <TableHead>Business Type & Status</TableHead>
          <TableHead>Manager</TableHead>
          <TableHead>Contact</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          <TableRow>
            <TableCell colSpan={7} className="text-center py-8">
              <Loader2 className="h-6 w-6 animate-spin inline-block mr-2" />
              Loading branches...
            </TableCell>
          </TableRow>
        ) : branches.length === 0 ? (
          <TableRow>
            <TableCell colSpan={7} className="text-center py-8">
              <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">No branches found.</p>
            </TableCell>
          </TableRow>
        ) : (
          branches.map((branch) => (
            <TableRow key={branch.id}>
              <TableCell>
                <div>
                  <div className="font-semibold">{branch.name}</div>
                  {branch.code && (
                    <div className="text-xs text-muted-foreground mt-0.5">
                      Code: {branch.code}
                    </div>
                  )}
                  {(branch.openingTime || branch.closingTime) && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                      <Clock className="h-3 w-3" />
                      {branch.openingTime} - {branch.closingTime}
                    </div>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Store className="h-4 w-4 text-blue-500 flex-shrink-0" />
                  <div className="text-sm">
                    <div className="font-medium">{store?.brand || "N/A"}</div>
                    {store?.businessType && (
                      <div className="text-xs text-muted-foreground capitalize">
                        {store.businessType.toLowerCase()}
                      </div>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <div className="text-sm">
                    <div>{branch.location || branch.address}</div>
                    {branch.city && (
                      <div className="text-xs text-muted-foreground">
                        {branch.city}, {branch.state} {branch.zipCode}
                      </div>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div className="space-y-1">
                  <Badge variant="outline" className={getBusinessTypeBadge(branch.businessType).className}>
                    {getBusinessTypeBadge(branch.businessType).label}
                  </Badge>
                  <Badge variant="outline" className={getStatusBadge(branch.status).className}>
                    {getStatusBadge(branch.status).label}
                  </Badge>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    {branch.managerId ? getManagerName(branch.managerId) : (branch.manager || "Not Assigned")}
                  </span>
                </div>
                {branch.employees > 0 && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {branch.employees} employees
                  </div>
                )}
              </TableCell>
              <TableCell>
                <div className="space-y-1 text-sm">
                  {branch.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-xs">{branch.phone}</span>
                    </div>
                  )}
                  {branch.email && (
                    <div className="text-xs text-muted-foreground truncate max-w-[150px]">
                      {branch.email}
                    </div>
                  )}
                </div>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(branch)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-red-600 hover:text-red-800 hover:bg-red-50"
                    onClick={() => handleDeleteBranch(branch.id)}
                    disabled={loading}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
};

export default BranchTable;