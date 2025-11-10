import api from './api';

const EMENU_BASE_URL = '/api/emenu';

export const emenuApi = {
  // Get menu for a branch
  getMenu: async (branchId) => {
    const response = await api.get(`${EMENU_BASE_URL}/menu/${branchId}`);
    return response.data;
  },

  // Get menu by category
  getMenuByCategory: async (branchId, categoryId) => {
    const response = await api.get(`${EMENU_BASE_URL}/menu/${branchId}/category/${categoryId}`);
    return response.data;
  },

  // Get table information
  getTableInfo: async (branchId, tableId, token) => {
    const response = await api.get(`${EMENU_BASE_URL}/table`, {
      params: { branchId, tableId, token }
    });
    return response.data;
  },

  // Place order
  placeOrder: async (orderData) => {
    const response = await api.post(`${EMENU_BASE_URL}/order`, orderData);
    return response.data;
  },

  // Get orders for a table
  getTableOrders: async (tableId) => {
    const response = await api.get(`${EMENU_BASE_URL}/orders/table/${tableId}`);
    return response.data;
  },

  // Generate QR code (staff use)
  generateQRCode: async (tableId) => {
    const response = await api.get(`${EMENU_BASE_URL}/qr-code/table/${tableId}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Regenerate table token (staff use)
  regenerateToken: async (tableId) => {
    const response = await api.post(`${EMENU_BASE_URL}/qr-code/table/${tableId}/regenerate`);
    return response.data;
  },
};

export default emenuApi;
