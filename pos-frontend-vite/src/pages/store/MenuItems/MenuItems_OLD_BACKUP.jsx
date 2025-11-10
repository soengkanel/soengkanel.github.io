import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Plus, Search, Edit, Trash2, ChefHat, Clock, DollarSign, Grid3x3, List } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { fetchMenuItems, deleteMenuItem } from "../../../Redux Toolkit/features/menuItem/menuItemThunks";
import MenuItemFormModal from "./MenuItemFormModal";
import DeleteConfirmDialog from "../../../components/common/DeleteConfirmDialog";

export default function MenuItems() {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { menuItems, loading } = useSelector((state) => state.menuItem);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [viewMode, setViewMode] = useState("table"); // 'grid' or 'table'

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

  // Filter menu items
  const filteredItems = (menuItems || []).filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" || item.category?.name === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Get unique categories
  const categories = ["all", ...new Set((menuItems || []).map((item) => item.category?.name).filter(Boolean))];

  /* REMOVED Mock data block - now fetching from Redux
        const mockData = [
          {
            id: 1,
            name: "Spring Rolls",
            sku: "MENU-APP-001",
            description: "Crispy vegetable spring rolls served with sweet chili sauce",
            sellingPrice: 8.99,
            category: { id: 1, name: "Appetizers" },
            preparationTime: 10,
            isAvailable: true,
            courseType: "APPETIZER",
            kitchenStation: "FRY",
            spiceLevel: "NONE",
            isVegetarian: true,
          },
          {
            id: 2,
            name: "Garlic Bread",
            sku: "MENU-APP-002",
            description: "Toasted bread with garlic butter and herbs",
            sellingPrice: 5.99,
            category: { id: 1, name: "Appetizers" },
            preparationTime: 5,
            isAvailable: true,
            courseType: "APPETIZER",
            kitchenStation: "GRILL",
            spiceLevel: "NONE",
            isVegetarian: true,
          },
          {
            id: 3,
            name: "Grilled Chicken",
            sku: "MENU-MAIN-001",
            description: "Herb-marinated grilled chicken with vegetables",
            sellingPrice: 18.99,
            category: { id: 2, name: "Main Course" },
            preparationTime: 20,
            isAvailable: true,
            courseType: "MAIN",
            kitchenStation: "GRILL",
            spiceLevel: "MEDIUM",
            isVegetarian: false,
          },
          {
            id: 4,
            name: "Beef Burger",
            sku: "MENU-MAIN-002",
            description: "Juicy beef burger with cheese, lettuce, and fries",
            sellingPrice: 15.99,
            category: { id: 2, name: "Main Course" },
            preparationTime: 15,
            isAvailable: true,
            courseType: "MAIN",
            kitchenStation: "GRILL",
            spiceLevel: "MILD",
            isVegetarian: false,
          },
          {
            id: 5,
            name: "Chocolate Cake",
            sku: "MENU-DES-001",
            description: "Rich chocolate cake with chocolate ganache",
            sellingPrice: 7.99,
            category: { id: 3, name: "Desserts" },
            preparationTime: 5,
            isAvailable: true,
            courseType: "DESSERT",
            kitchenStation: "PASTRY",
            spiceLevel: "NONE",
            isVegetarian: true,
          },
          {
            id: 6,
            name: "Cappuccino",
            sku: "MENU-COF-001",
            description: "Italian cappuccino with steamed milk",
            sellingPrice: 4.99,
            category: { id: 5, name: "Coffee & Tea" },
            preparationTime: 5,
            isAvailable: true,
            courseType: "BEVERAGE",
            kitchenStation: "BEVERAGE",
            spiceLevel: "NONE",
            isVegetarian: true,
          },
        ];

        setMenuItems(mockData);
      } catch (error) {
        console.error("Error fetching menu items:", error);
      } finally {
        setLoading(false);
      }
    };

    if (store?.id) {
      fetchMenuItems();
    }
  }, [store?.id]);

  // Filter menu items
  const filteredItems = menuItems.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" || item.category?.name === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Get unique categories
  const categories = ["all", ...new Set(menuItems.map((item) => item.category?.name))];

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <ChefHat className="w-8 h-8 text-primary" />
            Menu Items
          </h1>
          <p className="text-gray-600 mt-1">
            Manage your food and beverage menu items
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Menu Item
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Items</p>
                <p className="text-2xl font-bold text-gray-900">{menuItems.length}</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-full">
                <ChefHat className="w-6 h-6 text-primary" />
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
                  {menuItems.filter((item) => item.isAvailable).length}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <ChefHat className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Categories</p>
                <p className="text-2xl font-bold text-blue-600">
                  {categories.length - 1}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <ChefHat className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Price</p>
                <p className="text-2xl font-bold text-orange-600">
                  $
                  {(
                    menuItems.reduce((sum, item) => sum + item.sellingPrice, 0) /
                    menuItems.length
                  ).toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <DollarSign className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

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
                  placeholder="Search by name or SKU..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="md:w-64">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category === "all" ? "All Categories" : category}
                  </option>
                ))}
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

      {/* Menu Items Display */}
      {filteredItems.length === 0 ? (
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
              <Button className="flex items-center gap-2 mx-auto">
                <Plus className="w-4 h-4" />
                Add Menu Item
              </Button>
            )}
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        // Grid View
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => (
            <Card key={item.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      {item.name}
                      {item.isVegetarian && <span className="text-green-600">🥬</span>}
                      {getSpiceLevelEmoji(item.spiceLevel)}
                    </CardTitle>
                    <p className="text-sm text-gray-500 mt-1">{item.sku}</p>
                  </div>
                  <Badge
                    className={`${
                      item.isAvailable
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {item.isAvailable ? "Available" : "Unavailable"}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600 line-clamp-2">
                  {item.description}
                </p>

                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span className="font-semibold text-lg text-green-600">
                        ${item.sellingPrice.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>{item.preparationTime} min</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <Badge className={getCourseTypeBadge(item.courseType)}>
                      {item.courseType}
                    </Badge>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <ChefHat className="w-4 h-4" />
                  <span>{item.kitchenStation}</span>
                </div>

                {item.category && (
                  <div className="pt-2 border-t">
                    <span className="text-xs text-gray-500">
                      Category: {item.category.name}
                    </span>
                  </div>
                )}

                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
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
                      Item
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      SKU
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Prep Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Station
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Course
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
                  {filteredItems.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div>
                            <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                              {item.name}
                              {item.isVegetarian && <span className="text-green-600">🥬</span>}
                              {getSpiceLevelEmoji(item.spiceLevel)}
                            </div>
                            <div className="text-sm text-gray-500">{item.description}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.sku}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.category?.name || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                        ${item.sellingPrice.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {item.preparationTime} min
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.kitchenStation}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge className={getCourseTypeBadge(item.courseType)}>
                          {item.courseType}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge
                          className={`${
                            item.isAvailable
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {item.isAvailable ? "Available" : "Unavailable"}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="outline" size="sm" className="text-red-600">
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
    </div>
  );
}
