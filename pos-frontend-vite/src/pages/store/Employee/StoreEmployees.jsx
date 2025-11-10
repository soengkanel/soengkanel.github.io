import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Plus, Search, SlidersHorizontal, ArrowUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { EmployeeForm, EmployeeTable } from ".";
import { useDispatch, useSelector } from "react-redux";
import { useEffect } from "react";
import {
  createStoreEmployee,
  findStoreEmployees,
  updateEmployee,
  deleteEmployee,
} from "@/Redux Toolkit/features/employee/employeeThunks";
import { storeAdminRole } from "../../../utils/userRole";
import { mockEmployees } from "@/data/mockEmployees";

export default function StoreEmployees() {
  const dispatch = useDispatch();
  const { employees } = useSelector((state) => state.employee);
  const { store } = useSelector(state => state.store);

  useEffect(() => {
    if (store?.id) {
      dispatch(
        findStoreEmployees({
          storeId: store?.id,
          token: localStorage.getItem("jwt"),
        })
      );
    }
  }, [dispatch, store?.id, localStorage.getItem("jwt")]);

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [currentEmployee, setCurrentEmployee] = useState(null);

  // Filtering, Sorting, and Pagination states
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  const handleAddEmployee = (newEmployeeData) => {
    if (store?.id && localStorage.getItem("jwt")) {
      dispatch(
        createStoreEmployee({
          employee: {
            ...newEmployeeData,
            storeId: store?.id,
            username: newEmployeeData.email.split("@")[0],
          },
          storeId: store?.id,
          token: localStorage.getItem("jwt"),
        })
      );
      setIsAddDialogOpen(false);
    }
  };

  const handleEditEmployee = (updatedEmployeeData) => {
    if (currentEmployee?.id && localStorage.getItem("jwt")) {
      dispatch(
        updateEmployee({
          employeeId: currentEmployee.id,
          employeeDetails: updatedEmployeeData,
          token: localStorage.getItem("jwt"),
        })
      );
      setIsEditDialogOpen(false);
    }
  };

  const handleDeleteEmployee = (id) => {
    if (localStorage.getItem("jwt")) {
      dispatch(deleteEmployee({ employeeId: id, token: localStorage.getItem("jwt") }));
    }
  };

  const openEditDialog = (employee) => {
    setCurrentEmployee(employee);
    setIsEditDialogOpen(true);
  };

  // Get all employees (API or mock)
  const allEmployees = useMemo(() => {
    if (employees && employees.length > 0) {
      return employees;
    }
    // Use mock employees directly (they already have the correct structure)
    return mockEmployees;
  }, [employees]);

  // Filtered and sorted employees
  const filteredAndSortedEmployees = useMemo(() => {
    let result = [...allEmployees];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(emp =>
        emp.fullName?.toLowerCase().includes(query) ||
        emp.email?.toLowerCase().includes(query) ||
        emp.phone?.toLowerCase().includes(query) ||
        emp.department?.toLowerCase().includes(query)
      );
    }

    // Apply role filter
    if (roleFilter !== "ALL") {
      result = result.filter(emp => emp.role === roleFilter);
    }

    // Apply status filter
    if (statusFilter !== "ALL") {
      result = result.filter(emp => emp.status === statusFilter);
    }

    // Apply sorting
    result.sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case "name":
          aValue = a.fullName?.toLowerCase() || "";
          bValue = b.fullName?.toLowerCase() || "";
          break;
        case "role":
          aValue = a.role || "";
          bValue = b.role || "";
          break;
        case "email":
          aValue = a.email?.toLowerCase() || "";
          bValue = b.email?.toLowerCase() || "";
          break;
        case "department":
          aValue = a.department?.toLowerCase() || "";
          bValue = b.department?.toLowerCase() || "";
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  }, [allEmployees, searchQuery, roleFilter, statusFilter, sortBy, sortOrder]);

  // Paginated employees
  const paginatedEmployees = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredAndSortedEmployees.slice(startIndex, endIndex);
  }, [filteredAndSortedEmployees, currentPage, itemsPerPage]);

  // Calculate total pages
  const totalPages = Math.ceil(filteredAndSortedEmployees.length / itemsPerPage);

  // Get unique roles for filter
  const uniqueRoles = useMemo(() => {
    const roles = new Set(allEmployees.map(emp => emp.role));
    return Array.from(roles).sort();
  }, [allEmployees]);

  // Toggle sort order
  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Employee Management
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {filteredAndSortedEmployees.length} of {allEmployees.length} employee{allEmployees.length !== 1 ? 's' : ''}
            {employees?.length === 0 && " (showing demo data)"}
          </p>
        </div>
        <Button className="bg-emerald-600 hover:bg-emerald-700" onClick={() => setIsAddDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add Employee
        </Button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search by name, email, phone, or department..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1); // Reset to first page on search
            }}
            className="pl-9"
          />
        </div>

        {/* Role Filter */}
        <Select value={roleFilter} onValueChange={(value) => {
          setRoleFilter(value);
          setCurrentPage(1);
        }}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by Role" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Roles</SelectItem>
            {uniqueRoles.map(role => (
              <SelectItem key={role} value={role}>
                {role.replace("ROLE_", "").replace(/_/g, " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Status Filter */}
        <Select value={statusFilter} onValueChange={(value) => {
          setStatusFilter(value);
          setCurrentPage(1);
        }}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Status</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="INACTIVE">Inactive</SelectItem>
          </SelectContent>
        </Select>

        {/* Sort */}
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="role">Role</SelectItem>
            <SelectItem value="email">Email</SelectItem>
            <SelectItem value="department">Department</SelectItem>
          </SelectContent>
        </Select>

        <Button
          variant="outline"
          size="icon"
          onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
          className="flex-shrink-0"
        >
          <ArrowUpDown className={`h-4 w-4 ${sortOrder === "desc" ? "rotate-180" : ""}`} />
        </Button>
      </div>

      {/* Employee Table */}
      <EmployeeTable
        employees={paginatedEmployees}
        onEdit={openEditDialog}
        onDelete={handleDeleteEmployee}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Rows per page:</span>
            <Select value={itemsPerPage.toString()} onValueChange={(value) => {
              setItemsPerPage(parseInt(value));
              setCurrentPage(1);
            }}>
              <SelectTrigger className="w-[70px] h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Add Employee Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add New Employee</DialogTitle>
          </DialogHeader>
          <EmployeeForm
            onSubmit={handleAddEmployee}
            initialData={{
              fullName: "",
              email: "",
              password: "",
              phone: "",
              role: "",
              branchId: "",
            }}
            roles={storeAdminRole}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Employee Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Employee</DialogTitle>
          </DialogHeader>
          <EmployeeForm
            onSubmit={handleEditEmployee}
            roles={storeAdminRole}
            initialData={
              currentEmployee
                ? {
                    ...currentEmployee,
                    branchId: currentEmployee.branchId || "",
                  }
                : null
            }
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
