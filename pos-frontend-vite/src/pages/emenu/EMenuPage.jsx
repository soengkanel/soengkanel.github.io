import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ShoppingCart, Plus, Minus, Check } from 'lucide-react';
import emenuApi from '../../utils/emenuApi';

const EMenuPage = () => {
  const [searchParams] = useSearchParams();
  const branchId = searchParams.get('branch');
  const tableId = searchParams.get('table');
  const token = searchParams.get('token');

  const [tableInfo, setTableInfo] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCart, setShowCart] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState(false);

  useEffect(() => {
    if (branchId && tableId && token) {
      loadData();
    }
  }, [branchId, tableId, token]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [table, menu] = await Promise.all([
        emenuApi.getTableInfo(branchId, tableId, token),
        emenuApi.getMenu(branchId)
      ]);
      setTableInfo(table);
      setMenuItems(menu);
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Invalid QR code or table not found');
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item) => {
    const existing = cart.find(c => c.menuItemId === item.id);
    if (existing) {
      setCart(cart.map(c =>
        c.menuItemId === item.id
          ? { ...c, quantity: c.quantity + 1 }
          : c
      ));
    } else {
      setCart([...cart, {
        menuItemId: item.id,
        name: item.name,
        price: item.price,
        quantity: 1
      }]);
    }
  };

  const updateQuantity = (itemId, change) => {
    setCart(cart.map(item => {
      if (item.menuItemId === itemId) {
        const newQty = item.quantity + change;
        return newQty > 0 ? { ...item, quantity: newQty } : null;
      }
      return item;
    }).filter(Boolean));
  };

  const getCartTotal = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const placeOrder = async () => {
    if (cart.length === 0) return;

    try {
      const orderData = {
        branchId: parseInt(branchId),
        tableId: parseInt(tableId),
        tableToken: token,
        items: cart.map(item => ({
          menuItemId: item.menuItemId,
          quantity: item.quantity
        }))
      };

      await emenuApi.placeOrder(orderData);
      setOrderSuccess(true);
      setCart([]);
      setTimeout(() => {
        setOrderSuccess(false);
        setShowCart(false);
      }, 3000);
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Failed to place order. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading menu...</p>
        </div>
      </div>
    );
  }

  if (!tableInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Invalid QR Code</h2>
          <p className="text-gray-600">Please scan a valid table QR code</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">{tableInfo.branchName}</h1>
          <p className="text-sm text-gray-600">Table {tableInfo.tableNumber}</p>
        </div>
      </div>

      {/* Menu Items */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid gap-4">
          {menuItems.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
                  {item.description && (
                    <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                  )}
                  <div className="mt-2 flex items-center gap-3">
                    <span className="text-lg font-bold text-blue-600">
                      ${item.price.toFixed(2)}
                    </span>
                    {item.isVegetarian && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        Vegetarian
                      </span>
                    )}
                    {item.isVegan && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        Vegan
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => addToCart(item)}
                  className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus size={20} />
                  Add
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cart Button */}
      {cart.length > 0 && (
        <button
          onClick={() => setShowCart(true)}
          className="fixed bottom-6 right-6 bg-blue-600 text-white px-6 py-4 rounded-full shadow-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <ShoppingCart size={24} />
          <span className="font-semibold">{cart.length} Items - ${getCartTotal().toFixed(2)}</span>
        </button>
      )}

      {/* Cart Modal */}
      {showCart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center sm:justify-center">
          <div className="bg-white w-full sm:max-w-lg sm:rounded-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">Your Order</h2>

              {orderSuccess ? (
                <div className="text-center py-8">
                  <Check size={64} className="text-green-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-green-600">Order Placed Successfully!</h3>
                  <p className="text-gray-600 mt-2">Your order has been sent to the kitchen</p>
                </div>
              ) : (
                <>
                  <div className="space-y-4 mb-6">
                    {cart.map((item) => (
                      <div key={item.menuItemId} className="flex justify-between items-center">
                        <div className="flex-1">
                          <h4 className="font-medium">{item.name}</h4>
                          <p className="text-sm text-gray-600">${item.price.toFixed(2)} each</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => updateQuantity(item.menuItemId, -1)}
                            className="bg-gray-200 p-1 rounded"
                          >
                            <Minus size={16} />
                          </button>
                          <span className="font-semibold w-8 text-center">{item.quantity}</span>
                          <button
                            onClick={() => updateQuantity(item.menuItemId, 1)}
                            className="bg-gray-200 p-1 rounded"
                          >
                            <Plus size={16} />
                          </button>
                          <span className="font-semibold ml-2 w-20 text-right">
                            ${(item.price * item.quantity).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="border-t pt-4 mb-6">
                    <div className="flex justify-between text-xl font-bold">
                      <span>Total</span>
                      <span>${getCartTotal().toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <button
                      onClick={() => setShowCart(false)}
                      className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 font-semibold"
                    >
                      Continue Browsing
                    </button>
                    <button
                      onClick={placeOrder}
                      className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
                    >
                      Place Order
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EMenuPage;
