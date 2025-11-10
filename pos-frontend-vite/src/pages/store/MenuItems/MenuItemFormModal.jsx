import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { X, ImageIcon, Upload, Building2, Info, DollarSign } from "lucide-react";
import { getAllBranchesByStore } from "../../../Redux Toolkit/features/branch/branchThunks";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../../../components/ui/dialog";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Badge } from "../../../components/ui/badge";
import { createMenuItem, updateMenuItem } from "../../../Redux Toolkit/features/menuItem/menuItemThunks";
import { getCategoriesByStore } from "../../../Redux Toolkit/features/category/categoryThunks";
import { uploadToCloudinary } from "../../../utils/uploadToCloudinary";
import { mockMenuCategories } from "../../../data/mockFnBData";

export default function MenuItemFormModal({ open, onClose, menuItem = null }) {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { categories: reduxCategories } = useSelector((state) => state.category);
  const { branches } = useSelector((state) => state.branch);
  const { token } = useSelector((state) => state.auth);

  // Use Redux categories if available, otherwise fall back to mock data
  const categories = (reduxCategories && reduxCategories.length > 0) ? reduxCategories : mockMenuCategories;

  const [formData, setFormData] = useState({
    name: "",
    sku: "",
    description: "",
    sellingPrice: "",
    categoryId: "",
    preparationTime: "",
    courseType: "MAIN",
    kitchenStation: "KITCHEN",
    spiceLevel: "NONE",
    isVegetarian: false,
    isAvailable: true,
    imageUrl: "",
    branchPricing: [], // [{ branchId, price, available }]
  });

  const [loading, setLoading] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (store?.id && token) {
      dispatch(getCategoriesByStore({ storeId: store.id, token }));
      dispatch(getAllBranchesByStore({ storeId: store.id, jwt: token }));
    }
  }, [dispatch, store?.id, token]);

  useEffect(() => {
    if (menuItem) {
      setFormData({
        name: menuItem.name || "",
        sku: menuItem.sku || "",
        description: menuItem.description || "",
        sellingPrice: menuItem.sellingPrice || menuItem.basePrice || "",
        categoryId: menuItem.categoryId || menuItem.category?.id || "",
        preparationTime: menuItem.preparationTime || "",
        courseType: menuItem.courseType || "MAIN",
        kitchenStation: menuItem.kitchenStation || "KITCHEN",
        spiceLevel: menuItem.spiceLevel || "NONE",
        isVegetarian: menuItem.isVegetarian || false,
        isAvailable: menuItem.isAvailable !== undefined ? menuItem.isAvailable : true,
        imageUrl: menuItem.imageUrl || "",
        branchPricing: menuItem.branchPricing || [],
      });
    } else {
      setFormData({
        name: "",
        sku: "",
        description: "",
        sellingPrice: "",
        categoryId: "",
        preparationTime: "",
        courseType: "MAIN",
        kitchenStation: "KITCHEN",
        spiceLevel: "NONE",
        isVegetarian: false,
        isAvailable: true,
        imageUrl: "",
        branchPricing: [],
      });
    }
    setErrors({});
  }, [menuItem, open]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setErrors((prev) => ({ ...prev, imageUrl: "Please select a valid image file" }));
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrors((prev) => ({ ...prev, imageUrl: "Image size must be less than 5MB" }));
      return;
    }

    setUploadingImage(true);
    setErrors((prev) => ({ ...prev, imageUrl: "" }));

    try {
      const imageUrl = await uploadToCloudinary(file);
      setFormData((prev) => ({ ...prev, imageUrl }));
    } catch (error) {
      console.error("Error uploading image:", error);
      setErrors((prev) => ({ ...prev, imageUrl: "Failed to upload image. Please try again." }));
    } finally {
      setUploadingImage(false);
    }
  };

  const handleRemoveImage = () => {
    setFormData((prev) => ({ ...prev, imageUrl: "" }));
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.sku.trim()) newErrors.sku = "SKU is required";
    if (!formData.sellingPrice || formData.sellingPrice <= 0) newErrors.sellingPrice = "Valid price is required";
    if (!formData.categoryId) newErrors.categoryId = "Category is required";
    if (!formData.preparationTime || formData.preparationTime <= 0) newErrors.preparationTime = "Valid prep time is required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);
    try {
      const payload = {
        ...formData,
        sellingPrice: parseFloat(formData.sellingPrice),
        preparationTime: parseInt(formData.preparationTime),
      };

      if (menuItem) {
        // Update existing menu item
        await dispatch(updateMenuItem({
          menuItemId: menuItem.id,
          menuItemData: payload,
        })).unwrap();
      } else {
        // Create new menu item
        await dispatch(createMenuItem({
          menuItemData: payload,
          storeId: store.id,
        })).unwrap();
      }

      onClose();
    } catch (error) {
      console.error("Error saving menu item:", error);
      setErrors({ submit: error || "Failed to save menu item" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{menuItem ? "Edit Menu Item" : "Add New Menu Item"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name and SKU */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Name <span className="text-red-500">*</span>
              </label>
              <Input
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g., Grilled Chicken"
                className={errors.name ? "border-red-500" : ""}
              />
              {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name}</p>}
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">
                SKU <span className="text-red-500">*</span>
              </label>
              <Input
                name="sku"
                value={formData.sku}
                onChange={handleChange}
                placeholder="e.g., MENU-MAIN-001"
                className={errors.sku ? "border-red-500" : ""}
              />
              {errors.sku && <p className="text-xs text-red-500 mt-1">{errors.sku}</p>}
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="text-sm font-medium text-gray-700">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the menu item..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Price, Prep Time, Category */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Price ($) <span className="text-red-500">*</span>
              </label>
              <Input
                type="number"
                name="sellingPrice"
                value={formData.sellingPrice}
                onChange={handleChange}
                placeholder="0.00"
                step="0.01"
                min="0"
                className={errors.sellingPrice ? "border-red-500" : ""}
              />
              {errors.sellingPrice && <p className="text-xs text-red-500 mt-1">{errors.sellingPrice}</p>}
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">
                Prep Time (min) <span className="text-red-500">*</span>
              </label>
              <Input
                type="number"
                name="preparationTime"
                value={formData.preparationTime}
                onChange={handleChange}
                placeholder="15"
                min="1"
                className={errors.preparationTime ? "border-red-500" : ""}
              />
              {errors.preparationTime && <p className="text-xs text-red-500 mt-1">{errors.preparationTime}</p>}
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                name="categoryId"
                value={formData.categoryId}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.categoryId ? "border-red-500" : "border-gray-300"
                }`}
              >
                <option value="">Select category</option>
                {categories && categories.length > 0 ? (
                  categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))
                ) : (
                  <option value="" disabled>No categories available</option>
                )}
              </select>
              {errors.categoryId && <p className="text-xs text-red-500 mt-1">{errors.categoryId}</p>}
            </div>
          </div>

          {/* Image Upload */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              Menu Item Photo
            </label>

            {!formData.imageUrl ? (
              <div className="space-y-3">
                {/* Upload Button */}
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    id="menuItemImageUpload"
                    style={{ display: "none" }}
                    onChange={handleImageUpload}
                    disabled={uploadingImage}
                  />
                  <label htmlFor="menuItemImageUpload">
                    <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-8 hover:border-primary transition-colors cursor-pointer bg-gray-50 hover:bg-gray-100">
                      <div className="flex flex-col items-center justify-center text-center">
                        <Upload className="w-12 h-12 text-gray-400 mb-3" />
                        <p className="text-sm font-medium text-gray-700 mb-1">
                          {uploadingImage ? "Uploading..." : "Click to upload photo"}
                        </p>
                        <p className="text-xs text-gray-500">
                          PNG, JPG, JPEG up to 5MB
                        </p>
                      </div>
                      {uploadingImage && (
                        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 rounded-lg">
                          <div className="text-center">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-2"></div>
                            <p className="text-sm text-gray-600">Uploading...</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </label>
                </div>

                {/* Or divider */}
                <div className="flex items-center gap-3">
                  <div className="flex-1 border-t border-gray-300"></div>
                  <span className="text-xs text-gray-500 uppercase">Or paste URL</span>
                  <div className="flex-1 border-t border-gray-300"></div>
                </div>

                {/* Image URL Input */}
                <Input
                  name="imageUrl"
                  value={formData.imageUrl}
                  onChange={handleChange}
                  placeholder="https://example.com/image.jpg"
                  disabled={uploadingImage}
                />
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="relative h-64 w-full bg-gray-100">
                  <img
                    src={formData.imageUrl}
                    alt="Menu item preview"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="hidden absolute inset-0 items-center justify-center bg-gray-100">
                    <div className="text-center text-gray-400">
                      <ImageIcon className="w-12 h-12 mx-auto mb-2" />
                      <p className="text-sm">Failed to load image</p>
                    </div>
                  </div>

                  {/* Remove button overlay */}
                  <Button
                    type="button"
                    variant="destructive"
                    size="icon"
                    className="absolute top-2 right-2"
                    onClick={handleRemoveImage}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                {/* Image URL display */}
                <div className="p-3 bg-gray-50 border-t">
                  <p className="text-xs text-gray-600 truncate">{formData.imageUrl}</p>
                </div>
              </div>
            )}

            {errors.imageUrl && (
              <p className="text-xs text-red-500 mt-1">{errors.imageUrl}</p>
            )}
          </div>

          {/* Course Type, Kitchen Station */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Course Type</label>
              <select
                name="courseType"
                value={formData.courseType}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="APPETIZER">Appetizer</option>
                <option value="MAIN">Main Course</option>
                <option value="DESSERT">Dessert</option>
                <option value="BEVERAGE">Beverage</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">Station Tag</label>
              <select
                name="kitchenStation"
                value={formData.kitchenStation}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="KITCHEN">🔪 Kitchen</option>
                <option value="BAR">🍹 Bar</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {formData.kitchenStation === 'BAR' ? 'Routes to barista/bar station' : 'Routes to kitchen/chef station'}
              </p>
            </div>
          </div>

          {/* Spice Level */}
          <div>
            <label className="text-sm font-medium text-gray-700">Spice Level</label>
            <select
              name="spiceLevel"
              value={formData.spiceLevel}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="NONE">None</option>
              <option value="MILD">Mild 🌶️</option>
              <option value="MEDIUM">Medium 🌶️🌶️</option>
              <option value="HOT">Hot 🌶️🌶️🌶️</option>
              <option value="EXTRA_HOT">Extra Hot 🌶️🌶️🌶️🌶️</option>
            </select>
          </div>

          {/* Checkboxes */}
          <div className="flex gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="isVegetarian"
                checked={formData.isVegetarian}
                onChange={handleChange}
                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
              />
              <span className="text-sm text-gray-700">Vegetarian 🥬</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="isAvailable"
                checked={formData.isAvailable}
                onChange={handleChange}
                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
              />
              <span className="text-sm text-gray-700">Available</span>
            </label>
          </div>

          {/* Branch-Specific Pricing & Availability */}
          {branches && branches.length > 0 && (
            <div className="space-y-3 border-t pt-4">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Building2 className="w-4 h-4 text-primary" />
                <span>Branch-Specific Pricing</span>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
                <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-blue-900">
                  Set different prices for each branch. The base price (${formData.sellingPrice || '0.00'}) will be used for branches not listed below.
                </p>
              </div>

              <div className="space-y-3 p-4 border rounded-lg bg-gray-50 max-h-80 overflow-y-auto">
                {branches.map((branch) => {
                  const branchData = formData.branchPricing?.find(bp => bp.branchId === branch.id) || null;

                  return (
                    <div key={branch.id} className="bg-white rounded-lg border p-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {/* Branch Name & Availability */}
                        <div className="space-y-2">
                          <label className="text-xs font-medium text-gray-700 flex items-center gap-2">
                            <Building2 className="w-3.5 h-3.5 text-gray-500" />
                            Branch
                          </label>
                          <div className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                            <span className="text-sm font-medium text-gray-900">{branch.name}</span>
                            <label className="flex items-center gap-2 cursor-pointer">
                              <span className="text-xs text-gray-600">Available</span>
                              <input
                                type="checkbox"
                                checked={branchData?.available !== false}
                                onChange={(e) => {
                                  setFormData(prev => {
                                    const currentPricing = prev.branchPricing || [];
                                    const existingIndex = currentPricing.findIndex(bp => bp.branchId === branch.id);

                                    if (!e.target.checked) {
                                      // Mark as unavailable
                                      const newPricing = [...currentPricing];
                                      if (existingIndex >= 0) {
                                        newPricing[existingIndex] = {
                                          ...newPricing[existingIndex],
                                          available: false
                                        };
                                      } else {
                                        newPricing.push({
                                          branchId: branch.id,
                                          available: false,
                                          price: null
                                        });
                                      }
                                      return { ...prev, branchPricing: newPricing };
                                    } else {
                                      // Mark as available or remove override
                                      if (branchData?.price && branchData.price !== formData.sellingPrice) {
                                        // Keep custom price but mark available
                                        const newPricing = [...currentPricing];
                                        newPricing[existingIndex] = {
                                          ...branchData,
                                          available: true
                                        };
                                        return { ...prev, branchPricing: newPricing };
                                      } else {
                                        // Remove branch override entirely (use base)
                                        return {
                                          ...prev,
                                          branchPricing: currentPricing.filter(bp => bp.branchId !== branch.id)
                                        };
                                      }
                                    }
                                  });
                                }}
                                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                              />
                            </label>
                          </div>
                        </div>

                        {/* Custom Price */}
                        <div className="space-y-2">
                          <label className="text-xs font-medium text-gray-700 flex items-center gap-2">
                            <DollarSign className="w-3.5 h-3.5 text-gray-500" />
                            Custom Price (Optional)
                          </label>
                          <div className="flex items-center gap-2">
                            <Input
                              type="number"
                              placeholder={`Base: ${formData.sellingPrice || '0.00'}`}
                              value={branchData?.price || ''}
                              onChange={(e) => {
                                const newPrice = e.target.value;
                                setFormData(prev => {
                                  const currentPricing = prev.branchPricing || [];
                                  const existingIndex = currentPricing.findIndex(bp => bp.branchId === branch.id);

                                  if (newPrice) {
                                    // Add or update custom price
                                    const newPricing = [...currentPricing];
                                    if (existingIndex >= 0) {
                                      newPricing[existingIndex] = {
                                        ...newPricing[existingIndex],
                                        price: parseFloat(newPrice)
                                      };
                                    } else {
                                      newPricing.push({
                                        branchId: branch.id,
                                        price: parseFloat(newPrice),
                                        available: true
                                      });
                                    }
                                    return { ...prev, branchPricing: newPricing };
                                  } else {
                                    // Remove price override
                                    if (branchData?.available === false) {
                                      // Keep unavailable status
                                      const newPricing = [...currentPricing];
                                      newPricing[existingIndex] = {
                                        branchId: branch.id,
                                        available: false,
                                        price: null
                                      };
                                      return { ...prev, branchPricing: newPricing };
                                    } else {
                                      // Remove override entirely
                                      return {
                                        ...prev,
                                        branchPricing: currentPricing.filter(bp => bp.branchId !== branch.id)
                                      };
                                    }
                                  }
                                });
                              }}
                              disabled={branchData?.available === false}
                              step="0.01"
                              min="0"
                              className="h-9 text-sm"
                            />
                            {branchData?.price && branchData.price !== formData.sellingPrice && branchData.available !== false && (
                              <Badge variant="outline" className="text-xs whitespace-nowrap">
                                {parseFloat(branchData.price) > parseFloat(formData.sellingPrice || 0) ? '+' : ''}
                                ${(parseFloat(branchData.price || 0) - parseFloat(formData.sellingPrice || 0)).toFixed(2)}
                              </Badge>
                            )}
                            {branchData?.available === false && (
                              <Badge variant="outline" className="bg-red-50 text-red-700 text-xs whitespace-nowrap">
                                Disabled
                              </Badge>
                            )}
                            {(!branchData || (!branchData.price && branchData.available !== false)) && (
                              <Badge variant="outline" className="bg-gray-50 text-gray-600 text-xs whitespace-nowrap">
                                Base
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {errors.submit && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{errors.submit}</p>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : menuItem ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
