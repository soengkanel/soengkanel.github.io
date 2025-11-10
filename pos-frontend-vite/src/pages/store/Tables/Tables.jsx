import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Plus, Search, Edit, Trash2, TableProperties, Users, MapPin, Grid3x3, List, Building2 } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { mockTables, getTablesByBranch } from "../../../data/mockFnBData";
import { getAllBranchesByStore } from "@/Redux Toolkit/features/branch/branchThunks";
import TableFormModal from "./TableFormModal";
import DeleteConfirmDialog from "../../../components/common/DeleteConfirmDialog";

export default function Tables() {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { branches } = useSelector((state) => state.branch);
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBranch, setSelectedBranch] = useState("all"); // NEW: Branch filter
  const [selectedLocation, setSelectedLocation] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [viewMode, setViewMode] = useState("table"); // 'grid' or 'table'

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedTable, setSelectedTable] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Fetch branches
  useEffect(() => {
    if (store?.id) {
      dispatch(getAllBranchesByStore({
        storeId: store.id,
        jwt: localStorage.getItem('jwt'),
      }));
    }
  }, [dispatch, store?.id]);

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchTables = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/tables/branch/${branchId}`);
        // const data = await response.json();

        // Use branch-specific helper function from mockFnBData
        const branchTables = selectedBranch === "all"
          ? mockTables
          : getTablesByBranch(parseInt(selectedBranch));

        setTables(branchTables);
      } catch (error) {
        console.error("Error fetching tables:", error);
      } finally {
        setLoading(false);
      }
    };

    if (store?.id) {
      fetchTables();
    }
  }, [store?.id, selectedBranch]);

  // Filter tables
  const filteredTables = tables.filter((table) => {
    const matchesSearch = table.tableNumber
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesLocation =
      selectedLocation === "all" || table.location === selectedLocation;
    const matchesStatus =
      selectedStatus === "all" || table.status === selectedStatus;
    return matchesSearch && matchesLocation && matchesStatus;
  });

  // Get unique locations
  const locations = ["all", ...new Set(tables.map((table) => table.location))];

  // CRUD Handlers
  const handleAddClick = () => {
    setSelectedTable(null);
    setIsFormModalOpen(true);
  };

  const handleEditClick = (table) => {
    setSelectedTable(table);
    setIsFormModalOpen(true);
  };

  const handleDeleteClick = (table) => {
    setSelectedTable(table);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedTable) return;

    setDeleteLoading(true);
    try {
      // TODO: Replace with actual API call
      // await dispatch(deleteTable(selectedTable.id)).unwrap();
      console.log('Deleting table:', selectedTable.id);

      // Remove from local state
      setTables(tables.filter(t => t.id !== selectedTable.id));

      setIsDeleteModalOpen(false);
      setSelectedTable(null);
    } catch (error) {
      console.error("Error deleting table:", error);
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleModalClose = () => {
    setIsFormModalOpen(false);
    setIsDeleteModalOpen(false);
    setSelectedTable(null);
  };

  const handleFormSubmit = (tableData) => {
    // TODO: This will be replaced with actual API response
    // For now, just refresh the data
    if (selectedTable) {
      // Update existing
      setTables(tables.map(t => t.id === selectedTable.id ? { ...t, ...tableData } : t));
    } else {
      // Add new (mock ID)
      setTables([...tables, { ...tableData, id: tables.length + 1 }]);
    }
  };

  // Stats
  const availableTables = tables.filter((t) => t.status === "AVAILABLE").length;
  const occupiedTables = tables.filter((t) => t.status === "OCCUPIED").length;
  const reservedTables = tables.filter((t) => t.status === "RESERVED").length;
  const totalCapacity = tables.reduce((sum, t) => sum + t.capacity, 0);

  const getStatusBadge = (status) => {
    const badges = {
      AVAILABLE: { label: "Available", class: "bg-green-100 text-green-800" },
      OCCUPIED: { label: "Occupied", class: "bg-red-100 text-red-800" },
      RESERVED: { label: "Reserved", class: "bg-yellow-100 text-yellow-800" },
      CLEANING: { label: "Cleaning", class: "bg-blue-100 text-blue-800" },
    };
    return badges[status] || { label: status, class: "bg-gray-100 text-gray-800" };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading tables...</p>
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
            <TableProperties className="w-8 h-8 text-primary" />
            Table Management
          </h1>
          <p className="text-gray-600 mt-1">
            Manage your restaurant table layouts and reservations
          </p>
        </div>
        <Button className="flex items-center gap-2" onClick={handleAddClick}>
          <Plus className="w-4 h-4" />
          Add Table
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Tables</p>
                <p className="text-2xl font-bold text-gray-900">{tables.length}</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-full">
                <TableProperties className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Available</p>
                <p className="text-2xl font-bold text-green-600">
                  {availableTables}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <TableProperties className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Occupied</p>
                <p className="text-2xl font-bold text-red-600">{occupiedTables}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <TableProperties className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Seats</p>
                <p className="text-2xl font-bold text-blue-600">{totalCapacity}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Branch Filter Info */}
      {selectedBranch !== "all" && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
          <p className="text-blue-900">
            <span className="font-semibold">Branch Filter Active:</span> Showing tables for{" "}
            <span className="font-semibold">
              {branches?.find((b) => b.id === parseInt(selectedBranch))?.name}
            </span>
          </p>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Search by table number..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Branch Filter */}
            <div className="md:w-52">
              <select
                value={selectedBranch}
                onChange={(e) => setSelectedBranch(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Branches</option>
                {(branches && branches.length > 0) && branches.map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Location Filter */}
            <div className="md:w-48">
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {locations.map((location) => (
                  <option key={location} value={location}>
                    {location === "all" ? "All Locations" : location}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div className="md:w-48">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Status</option>
                <option value="AVAILABLE">Available</option>
                <option value="OCCUPIED">Occupied</option>
                <option value="RESERVED">Reserved</option>
                <option value="CLEANING">Cleaning</option>
              </select>
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

      {/* Tables Display */}
      {filteredTables.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <TableProperties className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No tables found
            </h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || selectedLocation !== "all" || selectedStatus !== "all"
                ? "Try adjusting your filters"
                : "Get started by adding your first table"}
            </p>
            {!searchQuery && selectedLocation === "all" && selectedStatus === "all" && (
              <Button className="flex items-center gap-2 mx-auto" onClick={handleAddClick}>
                <Plus className="w-4 h-4" />
                Add Table
              </Button>
            )}
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        // Grid View
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredTables.map((table) => {
            const statusBadge = getStatusBadge(table.status);
            return (
              <Card
                key={table.id}
                className={`hover:shadow-lg transition-shadow cursor-pointer ${
                  table.status === "OCCUPIED" ? "border-red-300" : ""
                } ${table.status === "RESERVED" ? "border-yellow-300" : ""}`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl font-bold">
                      {table.tableNumber}
                    </CardTitle>
                    <Badge className={statusBadge.class}>
                      {statusBadge.label}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 flex items-center gap-2">
                        <Users className="w-4 h-4" />
                        Capacity
                      </span>
                      <span className="font-semibold">{table.capacity} seats</span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        Location
                      </span>
                      <span className="font-semibold">{table.location}</span>
                    </div>

                    {table.branchName && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 flex items-center gap-2">
                          <Building2 className="w-4 h-4" />
                          Branch
                        </span>
                        <span className="font-semibold text-blue-600">{table.branchName}</span>
                      </div>
                    )}

                    {table.notes && (
                      <div className="text-sm pt-2 border-t">
                        <p className="text-gray-600">Notes:</p>
                        <p className="text-gray-900">{table.notes}</p>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 pt-2">
                    {table.status === "AVAILABLE" && (
                      <Button variant="default" size="sm" className="flex-1">
                        Assign Order
                      </Button>
                    )}
                    {table.status === "OCCUPIED" && (
                      <Button variant="destructive" size="sm" className="flex-1">
                        Clear Table
                      </Button>
                    )}
                    {table.status === "RESERVED" && (
                      <Button variant="secondary" size="sm" className="flex-1">
                        View Reservation
                      </Button>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleEditClick(table)}
                    >
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-red-600"
                      onClick={() => handleDeleteClick(table)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
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
                      Table Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Branch
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Capacity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Notes
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTables.map((table) => {
                    const statusBadge = getStatusBadge(table.status);
                    return (
                      <tr
                        key={table.id}
                        className={`hover:bg-gray-50 ${
                          table.status === "OCCUPIED" ? "bg-red-50" : ""
                        } ${table.status === "RESERVED" ? "bg-yellow-50" : ""}`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <TableProperties className="w-5 h-5 text-primary" />
                            <span className="text-sm font-semibold text-gray-900">
                              {table.tableNumber}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex items-center gap-2">
                            <Building2 className="w-4 h-4 text-blue-500" />
                            <span className="font-medium text-blue-600">
                              {table.branchName || 'N/A'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center gap-1">
                            <Users className="w-4 h-4 text-gray-400" />
                            {table.capacity} seats
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center gap-1">
                            <MapPin className="w-4 h-4 text-gray-400" />
                            {table.location}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge className={statusBadge.class}>
                            {statusBadge.label}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {table.notes || "-"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            {table.status === "AVAILABLE" && (
                              <Button variant="default" size="sm">
                                Assign
                              </Button>
                            )}
                            {table.status === "OCCUPIED" && (
                              <Button variant="destructive" size="sm">
                                Clear
                              </Button>
                            )}
                            {table.status === "RESERVED" && (
                              <Button variant="secondary" size="sm">
                                View
                              </Button>
                            )}
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditClick(table)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-600"
                              onClick={() => handleDeleteClick(table)}
                            >
                              <Trash2 className="w-4 h-4" />
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

      {/* Modals */}
      <TableFormModal
        open={isFormModalOpen}
        onClose={handleModalClose}
        table={selectedTable}
        onSubmit={handleFormSubmit}
      />

      <DeleteConfirmDialog
        open={isDeleteModalOpen}
        onClose={handleModalClose}
        onConfirm={handleDeleteConfirm}
        title="Delete Table"
        description="Are you sure you want to delete this table? This action cannot be undone."
        itemName={selectedTable?.tableNumber}
        loading={deleteLoading}
      />
    </div>
  );
}
