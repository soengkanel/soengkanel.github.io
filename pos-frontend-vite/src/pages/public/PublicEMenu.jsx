import React, { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router";
import { ShoppingCart, Clock, ChefHat, Leaf, Flame, Search, Filter } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Input } from "../../components/ui/input";
import { mockMenuItems, mockMenuCategories, mockTables, getMenuItemsByBranch, getItemPriceForBranch } from "../../data/mockFnBData";

export default function PublicEMenu() {
  const { storeId } = useParams();
  const [searchParams] = useSearchParams();
  const tableId = searchParams.get("table");

  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [branchId, setBranchId] = useState(null);
  const [branchName, setBranchName] = useState("");

  // Fetch menu items (using mock data for now)
  useEffect(() => {
    const fetchMenu = async () => {
      setLoading(true);
      try {
        // Determine branch from table ID if provided
        let currentBranchId = null;
        let currentBranchName = "";

        if (tableId) {
          const table = mockTables.find(t => t.id === parseInt(tableId));
          if (table) {
            currentBranchId = table.branchId;
            currentBranchName = table.branchName;
            setBranchId(currentBranchId);
            setBranchName(currentBranchName);
          }
        }

        // Get branch-specific menu items with pricing
        const branchMenuItems = currentBranchId
          ? getMenuItemsByBranch(currentBranchId)
          : mockMenuItems;

        setMenuItems(branchMenuItems);
        setCategories(mockMenuCategories);
      } catch (error) {
        console.error("Error fetching menu:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMenu();
  }, [storeId, tableId]);

  // Filter menu items
  const filteredItems = menuItems.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "all" || item.categoryName === selectedCategory;
    const isAvailable = item.isAvailable;
    return matchesSearch && matchesCategory && isAvailable;
  });

  // Add to cart
  const addToCart = (item) => {
    const existingItem = cart.find((cartItem) => cartItem.id === item.id);
    if (existingItem) {
      setCart(
        cart.map((cartItem) =>
          cartItem.id === item.id
            ? { ...cartItem, quantity: cartItem.quantity + 1 }
            : cartItem
        )
      );
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
  };

  // Remove from cart
  const removeFromCart = (itemId) => {
    const existingItem = cart.find((cartItem) => cartItem.id === itemId);
    if (existingItem.quantity === 1) {
      setCart(cart.filter((cartItem) => cartItem.id !== itemId));
    } else {
      setCart(
        cart.map((cartItem) =>
          cartItem.id === itemId
            ? { ...cartItem, quantity: cartItem.quantity - 1 }
            : cartItem
        )
      );
    }
  };

  // Calculate total
  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const getSpiceLevelIcon = (level) => {
    if (level === 0) return null;
    return (
      <span className="flex items-center gap-1 text-red-500">
        {Array.from({ length: level }).map((_, i) => (
          <Flame key={i} className="w-3 h-3" />
        ))}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading menu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 pb-32">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900 flex items-center gap-2 truncate">
                <ChefHat className="w-6 h-6 sm:w-8 sm:h-8 text-orange-600 flex-shrink-0" />
                <span className="truncate">Restaurant Menu</span>
              </h1>
              {tableId && (
                <div className="text-xs sm:text-sm text-gray-600 mt-0.5">
                  <p>Table #{tableId}</p>
                  {branchName && (
                    <p className="text-xs text-blue-600 font-medium">{branchName}</p>
                  )}
                </div>
              )}
            </div>
            {cartItemCount > 0 && (
              <Button
                className="relative bg-orange-600 hover:bg-orange-700 ml-2 flex-shrink-0 px-3 sm:px-4"
                size="sm"
                onClick={() => document.getElementById('cart-section').scrollIntoView({ behavior: 'smooth' })}
              >
                <ShoppingCart className="w-4 h-4 sm:w-5 sm:h-5 sm:mr-2" />
                <span className="hidden sm:inline">Cart</span>
                <span className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 bg-red-600 text-white text-xs rounded-full w-5 h-5 sm:w-6 sm:h-6 flex items-center justify-center font-bold">
                  {cartItemCount}
                </span>
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-6">
        {/* Search and Filter */}
        <Card className="mb-4 sm:mb-6">
          <CardContent className="p-3 sm:p-4">
            <div className="space-y-3">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 sm:w-5 sm:h-5" />
                <Input
                  type="text"
                  placeholder="Search dishes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 sm:pl-10 text-sm sm:text-base h-10 sm:h-11"
                />
              </div>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 sm:px-4 py-2 sm:py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-600 text-sm sm:text-base"
              >
                <option value="all">All Categories</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.name}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Menu Items */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-6 mb-8">
          {filteredItems.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <ChefHat className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 text-base sm:text-lg">No items found</p>
            </div>
          ) : (
            filteredItems.map((item) => (
              <Card key={item.id} className="hover:shadow-lg transition-shadow overflow-hidden">
                {item.imageUrl && (
                  <div className="relative h-40 sm:h-48 overflow-hidden">
                    <img
                      src={item.imageUrl}
                      alt={item.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
                      }}
                    />
                    <div className="absolute top-2 right-2 flex gap-1 sm:gap-2">
                      {item.isVegetarian && (
                        <Badge className="bg-green-500 text-white text-xs">
                          <Leaf className="w-3 h-3 sm:mr-1" />
                          <span className="hidden sm:inline">Veg</span>
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start justify-between mb-2 gap-2">
                    <h3 className="font-bold text-base sm:text-lg text-gray-900 line-clamp-2 flex-1">
                      {item.name}
                    </h3>
                    {getSpiceLevelIcon(item.spicyLevel)}
                  </div>

                  <p className="text-xs sm:text-sm text-gray-600 mb-3 line-clamp-2">
                    {item.description}
                  </p>

                  <div className="flex items-center justify-between mb-3 text-xs sm:text-sm">
                    <div className="flex items-center gap-1 sm:gap-2 text-gray-500">
                      <Clock className="w-3 h-3 sm:w-4 sm:h-4" />
                      <span>{item.preparationTime} min</span>
                    </div>
                    <Badge className="bg-orange-100 text-orange-800 text-xs">
                      {item.categoryName}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xl sm:text-2xl font-bold text-orange-600">
                      ${item.price.toFixed(2)}
                    </span>
                    <Button
                      onClick={() => addToCart(item)}
                      className="bg-orange-600 hover:bg-orange-700 text-sm sm:text-base px-3 sm:px-4"
                      size="sm"
                    >
                      <ShoppingCart className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                      Add
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Cart Section - Mobile Optimized */}
        {cart.length > 0 && (
          <div id="cart-section" className="fixed bottom-0 left-0 right-0 bg-white shadow-2xl border-t-4 border-orange-600 z-40">
            <div className="max-w-7xl mx-auto">
              {/* Cart Header - Collapsible on mobile */}
              <div className="px-3 sm:px-6 py-3 sm:py-4 border-b">
                <h2 className="text-lg sm:text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5 sm:w-6 sm:h-6 text-orange-600" />
                  <span className="flex-1">Your Order</span>
                  {tableId && (
                    <div className="text-right">
                      <span className="text-sm sm:text-base text-gray-600 font-normal block">
                        Table #{tableId}
                      </span>
                      {branchName && (
                        <span className="text-xs text-blue-600 font-medium">
                          {branchName}
                        </span>
                      )}
                    </div>
                  )}
                </h2>
              </div>

              {/* Cart Items - Scrollable */}
              <div className="px-3 sm:px-6 py-3 space-y-2 sm:space-y-3 max-h-48 sm:max-h-60 overflow-y-auto">
                {cart.map((item) => (
                  <div key={item.id} className="flex items-center gap-2 sm:gap-3 bg-gray-50 p-2 sm:p-3 rounded-lg">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 truncate">
                        {item.name}
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-600">
                        ${item.price.toFixed(2)} each
                      </p>
                    </div>
                    <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => removeFromCart(item.id)}
                        className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                      >
                        -
                      </Button>
                      <span className="font-semibold w-6 sm:w-8 text-center text-sm sm:text-base">
                        {item.quantity}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => addToCart(item)}
                        className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                      >
                        +
                      </Button>
                      <span className="font-bold text-orange-600 w-14 sm:w-20 text-right text-sm sm:text-base">
                        ${(item.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Cart Footer - Total and Checkout */}
              <div className="px-3 sm:px-6 py-3 sm:py-4 border-t bg-gray-50">
                <div className="flex items-center justify-between mb-3 sm:mb-4">
                  <span className="text-lg sm:text-xl font-bold text-gray-900">Total:</span>
                  <span className="text-xl sm:text-2xl font-bold text-orange-600">
                    ${cartTotal.toFixed(2)}
                  </span>
                </div>

                <Button
                  className="w-full bg-orange-600 hover:bg-orange-700 text-base sm:text-lg py-5 sm:py-6 font-bold shadow-lg"
                  onClick={() => alert('Order functionality will be implemented soon!')}
                >
                  Place Order - ${cartTotal.toFixed(2)}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
