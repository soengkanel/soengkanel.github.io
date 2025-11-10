import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Plus, Search, Edit, Trash2, ChefHat, Clock, DollarSign, Grid3x3, List, ArrowUpDown, ChevronLeft, ChevronRight, Filter } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { fetchMenuItems, deleteMenuItem } from "../../../Redux Toolkit/features/menuItem/menuItemThunks";
import MenuItemFormModal from "./MenuItemFormModal";
import DeleteConfirmDialog from "../../../components/common/DeleteConfirmDialog";
import { mockMenuItems, mockMenuCategories, getMenuItemsByBranch, getCategoriesByBranch, getBranchMenuStats } from "../../../data/mockFnBData";

export default function MenuItems() {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { branches } = useSelector((state) => state.branch);
  const { menuItems: reduxMenuItems, loading } = useSelector((state) => state.menuItem);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedBranch, setSelectedBranch] = useState(null); // null = all branches
  const [viewMode, setViewMode] = useState("table"); // 'grid' or 'table'

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(12);

  // Sorting states
  const [sortBy, setSortBy] = useState("name"); // name, price, prepTime
  const [sortOrder, setSortOrder] = useState("asc"); // asc, desc

  // Advanced filter states
  const [filterAvailability, setFilterAvailability] = useState("all"); // all, available, unavailable
  const [filterCourseType, setFilterCourseType] = useState("all");
  const [filterPriceRange, setFilterPriceRange] = useState({ min: "", max: "" });
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedMenuItem, setSelectedMenuItem] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Fetch menu items on component mount
  useEffect(() => {
    if (store?.id) {
      dispatch(fetchMenuItems(store.id));
    }
  }, [dispatch, store?.id]);

  // Get branch-specific menu items using helper function
  const branchSpecificMockItems = selectedBranch
    ? getMenuItemsByBranch(selectedBranch)
    : mockMenuItems;

  // Transform mock data to match expected format
  const transformedMockItems = branchSpecificMockItems.map(item => ({
    id: item.id,
    name: item.name,
    description: item.description,
    sku: `SKU-${item.id.toString().padStart(4, '0')}`,
    sellingPrice: item.price || item.basePrice, // Uses branch-specific price from helper
    basePrice: item.basePrice, // Keep base price
    category: { name: item.categoryName },
    isAvailable: item.isAvailable,
    preparationTime: item.preparationTime,
    isVegetarian: item.isVegetarian,
    spiceLevel: item.spicyLevel === 0 ? 'NONE' : item.spicyLevel === 1 ? 'MILD' : item.spicyLevel === 2 ? 'MEDIUM' : item.spicyLevel === 3 ? 'HOT' : 'EXTRA_HOT',
    courseType: item.categoryName === 'Appetizers' ? 'APPETIZER' :
                item.categoryName === 'Main Course' ? 'MAIN' :
                item.categoryName === 'Desserts' ? 'DESSERT' :
                item.categoryName === 'Beverages' ? 'BEVERAGE' : 'MAIN',
    kitchenStation: item.station || 'KITCHEN',
    imageUrl: item.imageUrl,
    branchId: selectedBranch, // Track which branch this is for
    branchPricing: item.branchPricing // Pass through branch pricing data
  }));

  // Use real data if available, otherwise use mock data
  const menuItems = (reduxMenuItems && reduxMenuItems.length > 0) ? reduxMenuItems : transformedMockItems;

  // CRUD Handlers
  const handleAddClick = () => {
    setSelectedMenuItem(null);
    setIsFormModalOpen(true);
  };

  const handleEditClick = (item) => {
    setSelectedMenuItem(item);
    setIsFormModalOpen(true);
  };

  const handleDeleteClick = (item) => {
    setSelectedMenuItem(item);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedMenuItem) return;

    setDeleteLoading(true);
    try {
      await dispatch(deleteMenuItem(selectedMenuItem.id)).unwrap();
      setIsDeleteModalOpen(false);
      setSelectedMenuItem(null);
    } catch (error) {
      console.error("Error deleting menu item:", error);
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleModalClose = () => {
    setIsFormModalOpen(false);
    setIsDeleteModalOpen(false);
    setSelectedMenuItem(null);
  };

  // Filter and sort menu items
  const filteredAndSortedItems = (() => {
    // Apply filters
    let items = (menuItems || []).filter((item) => {
      const matchesSearch =
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory =
        selectedCategory === "all" || item.category?.name === selectedCategory;

      const matchesAvailability =
        filterAvailability === "all" ||
        (filterAvailability === "available" && item.isAvailable) ||
        (filterAvailability === "unavailable" && !item.isAvailable);

      const matchesCourseType =
        filterCourseType === "all" || item.courseType === filterCourseType;

      const matchesPriceRange =
        (!filterPriceRange.min || item.sellingPrice >= parseFloat(filterPriceRange.min)) &&
        (!filterPriceRange.max || item.sellingPrice <= parseFloat(filterPriceRange.max));

      return matchesSearch && matchesCategory && matchesAvailability && matchesCourseType && matchesPriceRange;
    });

    // Apply sorting
    items.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "name":
          comparison = a.name.localeCompare(b.name);
          break;
        case "price":
          comparison = a.sellingPrice - b.sellingPrice;
          break;
        case "prepTime":
          comparison = a.preparationTime - b.preparationTime;
          break;
        case "category":
          comparison = (a.category?.name || "").localeCompare(b.category?.name || "");
          break;
        default:
          comparison = 0;
      }

      return sortOrder === "asc" ? comparison : -comparison;
    });

    return items;
  })();

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedItems.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedItems = filteredAndSortedItems.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedCategory, filterAvailability, filterCourseType, filterPriceRange, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedCategory("all");
    setSelectedBranch(null);
    setFilterAvailability("all");
    setFilterCourseType("all");
    setFilterPriceRange({ min: "", max: "" });
    setSortBy("name");
    setSortOrder("asc");
  };

  // Get unique categories
  const categories = ["all", ...new Set((menuItems || []).map((item) => item.category?.name).filter(Boolean))];

  const getCourseTypeBadge = (courseType) => {
    const badges = {
      APPETIZER: "bg-yellow-100 text-yellow-800",
      MAIN: "bg-red-100 text-red-800",
      DESSERT: "bg-pink-100 text-pink-800",
      BEVERAGE: "bg-blue-100 text-blue-800",
    };
    return badges[courseType] || "bg-gray-100 text-gray-800";
  };

  const getSpiceLevelEmoji = (level) => {
    const emojis = {
      NONE: "",
      MILD: "🌶️",
      MEDIUM: "🌶️🌶️",
      HOT: "🌶️🌶️🌶️",
      EXTRA_HOT: "🌶️🌶️🌶️🌶️",
    };
    return emojis[level] || "";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading menu items...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 w-full max-w-full overflow-hidden">
      {/* Compact Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <ChefHat className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Menu Items</h1>
            <p className="text-xs text-gray-500">
              {filteredAndSortedItems.length} of {(menuItems || []).length} items
            </p>
          </div>
        </div>
        <Button size="sm" className="flex items-center gap-2" onClick={handleAddClick}>
          <Plus className="w-4 h-4" />
          Add Item
        </Button>
      </div>

      {/* Compact Stats Bar */}
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">
            Total{selectedBranch && " (Branch)"}
          </p>
          <p className="text-lg font-bold text-gray-900">{(menuItems || []).length}</p>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Available</p>
          <p className="text-lg font-bold text-green-600">
            {(menuItems || []).filter((item) => item.isAvailable).length}
          </p>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Categories</p>
          <p className="text-lg font-bold text-blue-600">{categories.length - 1}</p>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Avg Price</p>
          <p className="text-lg font-bold text-orange-600">
            ${(menuItems || []).length > 0
              ? (
                  (menuItems || []).reduce((sum, item) => sum + item.sellingPrice, 0) /
                  (menuItems || []).length
                ).toFixed(2)
              : "0.00"}
          </p>
        </div>
      </div>

      {/* Branch Info Alert */}
      {selectedBranch && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
          <p className="text-blue-900">
            <span className="font-semibold">Branch Filter Active:</span> Showing menu items and pricing for{" "}
            <span className="font-semibold">
              {branches.find((b) => b.id === selectedBranch)?.name}
            </span>
          </p>
        </div>
      )}

      {/* Compact Filters */}
      <div className="bg-white border rounded-lg p-3">
        <div className="flex flex-col gap-2">
          {/* Main Filter Row */}
          <div className="flex gap-2">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 h-9 text-sm"
              />
            </div>

            {/* Category */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category === "all" ? "All" : category}
                </option>
              ))}
            </select>

            {/* Branch Filter */}
            <select
              value={selectedBranch || "all"}
              onChange={(e) => setSelectedBranch(e.target.value === "all" ? null : parseInt(e.target.value))}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Branches</option>
              {(branches || []).map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="name">Name</option>
              <option value="price">Price</option>
              <option value="prepTime">Prep Time</option>
              <option value="category">Category</option>
            </select>

            {/* Sort Order */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
              className="px-2 h-9"
            >
              <ArrowUpDown className="w-3 h-3" />
            </Button>

            {/* Filters Toggle */}
            <Button
              variant={showAdvancedFilters ? "default" : "outline"}
              size="sm"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="px-2 h-9"
            >
              <Filter className="w-3 h-3" />
            </Button>

            {/* View Toggle */}
            <div className="flex gap-1">
              <Button
                variant={viewMode === "grid" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="px-2 h-9"
              >
                <Grid3x3 className="w-3 h-3" />
              </Button>
              <Button
                variant={viewMode === "table" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("table")}
                className="px-2 h-9"
              >
                <List className="w-3 h-3" />
              </Button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="pt-2 border-t space-y-2">
              <div className="grid grid-cols-4 gap-2">
                <select
                  value={filterAvailability}
                  onChange={(e) => setFilterAvailability(e.target.value)}
                  className="px-2 py-1.5 text-xs border rounded-md"
                >
                  <option value="all">All Status</option>
                  <option value="available">Available</option>
                  <option value="unavailable">Unavailable</option>
                </select>

                <select
                  value={filterCourseType}
                  onChange={(e) => setFilterCourseType(e.target.value)}
                  className="px-2 py-1.5 text-xs border rounded-md"
                >
                  <option value="all">All Courses</option>
                  <option value="APPETIZER">Appetizer</option>
                  <option value="MAIN">Main</option>
                  <option value="DESSERT">Dessert</option>
                  <option value="BEVERAGE">Beverage</option>
                </select>

                <Input
                  type="number"
                  placeholder="Min $"
                  value={filterPriceRange.min}
                  onChange={(e) =>
                    setFilterPriceRange({ ...filterPriceRange, min: e.target.value })
                  }
                  className="h-8 text-xs"
                />

                <Input
                  type="number"
                  placeholder="Max $"
                  value={filterPriceRange.max}
                  onChange={(e) =>
                    setFilterPriceRange({ ...filterPriceRange, max: e.target.value })
                  }
                  className="h-8 text-xs"
                />
              </div>
              <Button variant="ghost" size="sm" onClick={clearFilters} className="h-7 text-xs">
                Clear Filters
              </Button>
            </div>
          )}

          {/* Results Summary */}
          <div className="flex items-center justify-between text-xs text-gray-500 pt-1">
            <span>
              {startIndex + 1}-{Math.min(endIndex, filteredAndSortedItems.length)} of{" "}
              {filteredAndSortedItems.length}
            </span>
            <div className="flex items-center gap-1.5">
              <span>Per page:</span>
              <select
                value={itemsPerPage}
                onChange={(e) => setItemsPerPage(Number(e.target.value))}
                className="px-2 py-0.5 text-xs border rounded"
              >
                <option value="12">12</option>
                <option value="24">24</option>
                <option value="48">48</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Menu Items Display */}
      {filteredAndSortedItems.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <ChefHat className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No menu items found
            </h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || selectedCategory !== "all"
                ? "Try adjusting your filters"
                : "Get started by adding your first menu item"}
            </p>
            {!searchQuery && selectedCategory === "all" && (
              <Button className="flex items-center gap-2 mx-auto" onClick={handleAddClick}>
                <Plus className="w-4 h-4" />
                Add Menu Item
              </Button>
            )}
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        // Compact Grid View
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {paginatedItems.map((item) => (
            <Card key={item.id} className="hover:shadow-md transition-shadow overflow-hidden border">
              {/* Compact Image */}
              {item.imageUrl && (
                <div className="relative h-32 w-full overflow-hidden bg-gray-100">
                  <img
                    src={item.imageUrl}
                    alt={item.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/200x150?text=No+Image';
                    }}
                  />
                  <div className="absolute top-1 right-1">
                    <div className={`w-2 h-2 rounded-full ${item.isAvailable ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  </div>
                </div>
              )}

              <CardContent className="p-3 space-y-2">
                {/* Title & Price */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-sm text-gray-900 truncate flex items-center gap-1">
                      {item.name}
                      {item.isVegetarian && <span className="text-xs">🥬</span>}
                    </h3>
                    <p className="text-xs text-gray-500">{item.sku}</p>
                  </div>
                  <span className="font-bold text-sm text-green-600 flex-shrink-0">
                    ${item.sellingPrice.toFixed(2)}
                  </span>
                </div>

                {/* Description */}
                <p className="text-xs text-gray-600 line-clamp-2">
                  {item.description}
                </p>

                {/* Meta Info */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {item.preparationTime}m
                  </span>
                  <Badge className={`${getCourseTypeBadge(item.courseType)} text-xs py-0`}>
                    {item.courseType}
                  </Badge>
                </div>

                {/* Actions */}
                <div className="flex gap-1.5 pt-1">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 h-7 text-xs"
                    onClick={() => handleEditClick(item)}
                  >
                    <Edit className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 px-2 text-red-600"
                    onClick={() => handleDeleteClick(item)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        // Compact Table View
        <Card className="w-full border">
          <CardContent className="p-0">
            <div className="overflow-x-auto w-full">
              <table className="w-full min-w-[1200px]">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Item
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      SKU
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Category
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Price
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Prep
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Station
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Course
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedItems.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          {item.imageUrl ? (
                            <img
                              src={item.imageUrl}
                              alt={item.name}
                              className="w-12 h-12 rounded object-cover flex-shrink-0"
                              onError={(e) => {
                                e.target.src = 'https://via.placeholder.com/48?text=No+Image';
                              }}
                            />
                          ) : (
                            <div className="w-12 h-12 rounded bg-gray-200 flex items-center justify-center flex-shrink-0">
                              <ChefHat className="w-6 h-6 text-gray-400" />
                            </div>
                          )}
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-gray-900 flex items-center gap-1 truncate">
                              {item.name}
                              {item.isVegetarian && <span className="text-xs">🥬</span>}
                              {getSpiceLevelEmoji(item.spiceLevel)}
                            </div>
                            <div className="text-xs text-gray-500 line-clamp-1">{item.description}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-600">
                        {item.sku}
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-600">
                        {item.category?.name || "-"}
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap text-sm font-semibold text-green-600">
                        ${item.sellingPrice.toFixed(2)}
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-600">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {item.preparationTime}m
                        </div>
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap">
                        <Badge className={`${item.kitchenStation === 'BAR' ? 'bg-purple-500' : 'bg-orange-500'} text-white text-xs py-0`}>
                          {item.kitchenStation}
                        </Badge>
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap">
                        <Badge className={`${getCourseTypeBadge(item.courseType)} text-xs py-0`}>
                          {item.courseType}
                        </Badge>
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap">
                        <Badge
                          className={`${
                            item.isAvailable
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          } text-xs py-0`}
                        >
                          {item.isAvailable ? "Available" : "Unavailable"}
                        </Badge>
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditClick(item)}
                            className="h-7 px-2"
                          >
                            <Edit className="w-3 h-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600 h-7 px-2"
                            onClick={() => handleDeleteClick(item)}
                          >
                            <Trash2 className="w-3 h-3" />
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

      {/* Compact Pagination */}
      {totalPages > 1 && (
        <Card className="border">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-600">
                Page {currentPage} of {totalPages}
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(1)}
                  disabled={currentPage === 1}
                  className="h-7 px-2 text-xs"
                >
                  First
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="h-7 px-2"
                >
                  <ChevronLeft className="w-3 h-3" />
                </Button>

                {/* Page Numbers */}
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }

                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => handlePageChange(pageNum)}
                        className="h-7 w-7 p-0 text-xs"
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="h-7 px-2"
                >
                  <ChevronRight className="w-3 h-3" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                  className="h-7 px-2 text-xs"
                >
                  Last
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modals */}
      <MenuItemFormModal
        open={isFormModalOpen}
        onClose={handleModalClose}
        menuItem={selectedMenuItem}
      />

      <DeleteConfirmDialog
        open={isDeleteModalOpen}
        onClose={handleModalClose}
        onConfirm={handleDeleteConfirm}
        title="Delete Menu Item"
        description="Are you sure you want to delete this menu item? This action cannot be undone."
        itemName={selectedMenuItem?.name}
        loading={deleteLoading}
      />
    </div>
  );
}
