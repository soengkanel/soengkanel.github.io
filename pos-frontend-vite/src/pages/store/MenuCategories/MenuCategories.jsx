import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Plus, Search, Edit, Trash2, Coffee, UtensilsCrossed, Grid3x3, List, Building2 } from "lucide-react";
import { getAllBranchesByStore } from "@/Redux Toolkit/features/branch/branchThunks";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { mockMenuCategories, mockMenuItems } from "../../../data/mockFnBData";
import { mockBranches } from "../../../data/mockBranches";
import CategoryForm from "../Category/CategoryForm";

export default function MenuCategories() {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { branches } = useSelector((state) => state.branch);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState("table"); // 'grid' or 'table'
  const [selectedBranch, setSelectedBranch] = useState("all"); // 'all' or branch ID
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  // Fetch branches when component mounts
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
    const fetchCategories = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/category/${store.id}`);
        // const data = await response.json();

        // Use imported mock data and calculate item counts
        const categoriesWithCounts = mockMenuCategories.map(category => {
          const itemCount = mockMenuItems.filter(
            item => item.categoryId === category.id
          ).length;

          return {
            id: category.id,
            name: category.name,
            description: category.description,
            itemCount: itemCount,
            isActive: category.isActive,
            displayOrder: category.displayOrder,
            imageUrl: category.imageUrl,
            branchIds: category.branchIds || [] // Include branch availability
          };
        });

        setCategories(categoriesWithCounts);
      } catch (error) {
        console.error("Error fetching categories:", error);
      } finally {
        setLoading(false);
      }
    };

    if (store?.id) {
      fetchCategories();
    }
  }, [store?.id]);

  // Filter categories by search and branch
  const filteredCategories = categories.filter((category) => {
    const matchesSearch = category.name.toLowerCase().includes(searchQuery.toLowerCase());

    // Branch filter logic
    const matchesBranch = selectedBranch === "all" ||
      (!category.branchIds || category.branchIds.length === 0) || // Available at all branches
      category.branchIds.includes(parseInt(selectedBranch)); // Available at selected branch

    return matchesSearch && matchesBranch;
  });

  const totalItems = categories.reduce((sum, cat) => sum + cat.itemCount, 0);

  // Handler functions
  const handleAddCategory = () => {
    setEditingCategory(null);
    setIsDialogOpen(true);
  };

  const handleEditCategory = (category) => {
    setEditingCategory(category);
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setEditingCategory(null);
  };

  const handleFormSubmit = () => {
    handleCloseDialog();
    // Refresh categories if needed
  };

  // Helper function to get branch names for a category
  const getBranchNames = (category) => {
    // If branchIds is empty or null, it's available at all branches
    if (!category.branchIds || category.branchIds.length === 0) {
      return "All Branches";
    }

    // Get branch names for specific branch IDs
    const branchNames = category.branchIds
      .map(branchId => {
        const branch = mockBranches.find(b => b.id === branchId);
        return branch ? branch.name : null;
      })
      .filter(Boolean);

    return branchNames.length > 0 ? branchNames.join(", ") : "No branches";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading categories...</p>
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
            <Coffee className="w-8 h-8 text-primary" />
            Menu Categories
          </h1>
          <p className="text-gray-600 mt-1">
            Organize your menu items into categories
          </p>
        </div>
        <Button className="flex items-center gap-2" onClick={handleAddCategory}>
          <Plus className="w-4 h-4" />
          Add Category
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Categories</p>
                <p className="text-2xl font-bold text-gray-900">
                  {categories.length}
                </p>
              </div>
              <div className="p-3 bg-primary/10 rounded-full">
                <Coffee className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Menu Items</p>
                <p className="text-2xl font-bold text-green-600">{totalItems}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <UtensilsCrossed className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Empty Categories</p>
                <p className="text-2xl font-bold text-orange-600">
                  {categories.filter((cat) => cat.itemCount === 0).length}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <Coffee className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and View Toggle */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search categories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Branch Filter */}
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Branches</option>
              {(branches && branches.length > 0) && branches.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>

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

      {/* Categories Display */}
      {filteredCategories.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Coffee className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No categories found
            </h3>
            <p className="text-gray-600 mb-4">
              {searchQuery
                ? "Try a different search term"
                : "Get started by adding your first category"}
            </p>
            {!searchQuery && (
              <Button className="flex items-center gap-2 mx-auto" onClick={handleAddCategory}>
                <Plus className="w-4 h-4" />
                Add Category
              </Button>
            )}
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        // Grid View
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredCategories.map((category) => (
            <Card
              key={category.id}
              className="hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
            >
              {/* Category Image */}
              {category.imageUrl && (
                <div className="relative h-40 w-full overflow-hidden bg-gray-200">
                  <img
                    src={category.imageUrl}
                    alt={category.name}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
                    }}
                  />
                  <div className="absolute top-2 right-2">
                    <Badge
                      className={`${
                        category.itemCount > 0
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {category.itemCount > 0 ? "Active" : "Empty"}
                    </Badge>
                  </div>
                </div>
              )}

              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Coffee className="w-5 h-5 text-primary" />
                    {category.name}
                  </CardTitle>
                </div>
                {category.description && (
                  <p className="text-sm text-gray-600 mt-2">
                    {category.description}
                  </p>
                )}
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Menu Items</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {category.itemCount}
                    </p>
                  </div>
                  <div
                    className={`p-3 rounded-full ${
                      category.itemCount > 0
                        ? "bg-green-100"
                        : "bg-gray-100"
                    }`}
                  >
                    <UtensilsCrossed
                      className={`w-6 h-6 ${
                        category.itemCount > 0
                          ? "text-green-600"
                          : "text-gray-400"
                      }`}
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleEditCategory(category)}
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600"
                    disabled={category.itemCount > 0}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>

                {category.itemCount > 0 && (
                  <p className="text-xs text-gray-500 text-center">
                    Cannot delete category with items
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
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
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Branches
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Item Count
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredCategories.map((category) => (
                    <tr key={category.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          {category.imageUrl ? (
                            <img
                              src={category.imageUrl}
                              alt={category.name}
                              className="w-12 h-12 rounded-lg object-cover"
                              onError={(e) => {
                                e.target.src = 'https://via.placeholder.com/48?text=No+Image';
                              }}
                            />
                          ) : (
                            <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center">
                              <Coffee className="w-6 h-6 text-gray-400" />
                            </div>
                          )}
                          <div>
                            <span className="text-sm font-medium text-gray-900 block">
                              {category.name}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-600">
                          {category.description || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-blue-500" />
                          <span className="text-sm text-gray-900">
                            {getBranchNames(category)}
                          </span>
                        </div>
                        {category.branchIds && category.branchIds.length > 0 && (
                          <Badge variant="outline" className="mt-1 text-xs">
                            {category.branchIds.length} branch{category.branchIds.length !== 1 ? 'es' : ''}
                          </Badge>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <UtensilsCrossed className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-900">
                            {category.itemCount} items
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge
                          className={
                            category.itemCount > 0
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          }
                        >
                          {category.itemCount > 0 ? "Active" : "Empty"}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditCategory(category)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600"
                            disabled={category.itemCount > 0}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add/Edit Category Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingCategory ? "Edit Category" : "Add New Category"}
            </DialogTitle>
            <DialogDescription>
              {editingCategory
                ? "Update the category details below"
                : "Fill in the details to create a new menu category"}
            </DialogDescription>
          </DialogHeader>
          <CategoryForm
            initialValues={editingCategory}
            onSubmit={handleFormSubmit}
            onCancel={handleCloseDialog}
            isEditing={!!editingCategory}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
