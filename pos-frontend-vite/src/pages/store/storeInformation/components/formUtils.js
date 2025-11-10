// Transform store data for form initialization
export const getInitialValues = (storeData) => {
  if (!storeData) {
    return {
      brand: "",
      description: "",
      businessType: "",
      contact: {
        address: "",
        phone: "",
        email: "",
      },
    };
  }

  // Handle both nested contact object and flat structure
  // Support both 'businessType' and legacy 'storeType'/'type' fields
  return {
    brand: storeData.brand || storeData.name || "",
    description: storeData.description || "",
    businessType: storeData.businessType || storeData.storeType || storeData.type || "",
    contact: {
      address: storeData.contact?.address || storeData.address || "",
      phone: storeData.contact?.phone || storeData.phone || "",
      email: storeData.contact?.email || storeData.email || "",
    },
  };
}; 