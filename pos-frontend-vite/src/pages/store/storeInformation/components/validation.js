import * as Yup from "yup";

// Validation schema for store information
export const StoreValidationSchema = Yup.object().shape({
  brand: Yup.string()
    .min(2, "Store name must be at least 2 characters")
    .max(100, "Store name must be less than 100 characters")
    .required("Store name is required"),
  description: Yup.string()
    .max(500, "Description must be less than 500 characters"),
  businessType: Yup.string()
    .required("Business type is required"),
  contact: Yup.object().shape({
    address: Yup.string()
      .min(10, "Address must be at least 10 characters")
      .max(200, "Address must be less than 200 characters")
      .required("Address is required"),
    phone: Yup.string()
      .matches(/^[\+]?[1-9][\d]{0,15}$/, "Please enter a valid phone number")
      .required("Phone number is required"),
    email: Yup.string()
      .email("Please enter a valid email address")
      .required("Email is required"),
  }),
});

// Business type options for the select dropdown
export const BUSINESS_TYPE_OPTIONS = [
  { value: "FNB", label: "Food & Beverage (Restaurant, Cafe, Bar)" },
  { value: "RETAIL", label: "Retail (Shop, Store, Boutique)" },
  { value: "HYBRID", label: "Hybrid (F&B + Retail)" },
];

// Legacy export for backward compatibility (will be removed)
export const STORE_TYPE_OPTIONS = BUSINESS_TYPE_OPTIONS; 