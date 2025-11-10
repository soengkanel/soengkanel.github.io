import api from './api';

const RESERVATION_BASE_URL = '/api/reservations';

export const reservationApi = {
  // Create a new reservation
  createReservation: async (data) => {
    const response = await api.post(RESERVATION_BASE_URL, data);
    return response.data;
  },

  // Get reservation by ID
  getReservationById: async (id) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/${id}`);
    return response.data;
  },

  // Get reservation by confirmation code
  getReservationByConfirmationCode: async (confirmationCode) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/confirmation/${confirmationCode}`);
    return response.data;
  },

  // Get all reservations for a branch
  getReservationsByBranch: async (branchId) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/branch/${branchId}`);
    return response.data;
  },

  // Get reservations for a branch on a specific date
  getReservationsByBranchAndDate: async (branchId, date) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/branch/${branchId}/date/${date}`);
    return response.data;
  },

  // Get reservations by status
  getReservationsByBranchAndStatus: async (branchId, status) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/branch/${branchId}/status/${status}`);
    return response.data;
  },

  // Get upcoming reservations
  getUpcomingReservations: async (branchId) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/branch/${branchId}/upcoming`);
    return response.data;
  },

  // Get reservations within a date range
  getReservationsByDateRange: async (branchId, startDate, endDate) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/branch/${branchId}/range`, {
      params: { startDate, endDate }
    });
    return response.data;
  },

  // Get customer's reservations
  getCustomerReservations: async (customerId) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/customer/${customerId}`);
    return response.data;
  },

  // Update reservation
  updateReservation: async (id, data) => {
    const response = await api.put(`${RESERVATION_BASE_URL}/${id}`, data);
    return response.data;
  },

  // Update reservation status
  updateReservationStatus: async (id, statusData) => {
    const response = await api.patch(`${RESERVATION_BASE_URL}/${id}/status`, statusData);
    return response.data;
  },

  // Confirm reservation
  confirmReservation: async (id) => {
    const response = await api.post(`${RESERVATION_BASE_URL}/${id}/confirm`);
    return response.data;
  },

  // Cancel reservation
  cancelReservation: async (id, reason) => {
    const response = await api.post(`${RESERVATION_BASE_URL}/${id}/cancel`, null, {
      params: { reason }
    });
    return response.data;
  },

  // Seat reservation
  seatReservation: async (id, tableId) => {
    const response = await api.post(`${RESERVATION_BASE_URL}/${id}/seat`, null, {
      params: { tableId }
    });
    return response.data;
  },

  // Complete reservation
  completeReservation: async (id) => {
    const response = await api.post(`${RESERVATION_BASE_URL}/${id}/complete`);
    return response.data;
  },

  // Mark as no-show
  markAsNoShow: async (id) => {
    const response = await api.post(`${RESERVATION_BASE_URL}/${id}/no-show`);
    return response.data;
  },

  // Delete reservation
  deleteReservation: async (id) => {
    const response = await api.delete(`${RESERVATION_BASE_URL}/${id}`);
    return response.data;
  },

  // Check table availability
  checkTableAvailability: async (tableId, date, startTime, durationMinutes) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/availability/table/${tableId}`, {
      params: { date, startTime, durationMinutes }
    });
    return response.data;
  },

  // Get available tables
  getAvailableTables: async (branchId, date, time, guests, duration) => {
    const response = await api.get(`${RESERVATION_BASE_URL}/availability/branch/${branchId}/tables`, {
      params: { date, time, guests, duration }
    });
    return response.data;
  },
};

export default reservationApi;
