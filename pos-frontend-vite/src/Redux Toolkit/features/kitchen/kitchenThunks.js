import { createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../../utils/api';

export const fetchActiveKitchenOrders = createAsyncThunk(
  'kitchen/fetchActive',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/kitchen-orders/active');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch active orders');
    }
  }
);

export const fetchKitchenOrdersByStation = createAsyncThunk(
  'kitchen/fetchByStation',
  async (station, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kitchen-orders/station/${station}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch station orders');
    }
  }
);

export const fetchPendingOrders = createAsyncThunk(
  'kitchen/fetchPending',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/kitchen-orders/pending');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch pending orders');
    }
  }
);

export const fetchReadyOrders = createAsyncThunk(
  'kitchen/fetchReady',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/kitchen-orders/ready');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch ready orders');
    }
  }
);

export const createKitchenOrder = createAsyncThunk(
  'kitchen/create',
  async ({ orderId, station }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kitchen-orders?orderId=${orderId}&station=${station}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create kitchen order');
    }
  }
);

export const startPreparation = createAsyncThunk(
  'kitchen/startPreparation',
  async (kitchenOrderId, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/kitchen-orders/${kitchenOrderId}/start`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to start preparation');
    }
  }
);

export const completePreparation = createAsyncThunk(
  'kitchen/completePreparation',
  async (kitchenOrderId, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/kitchen-orders/${kitchenOrderId}/complete`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to complete preparation');
    }
  }
);

export const updateKitchenOrderStatus = createAsyncThunk(
  'kitchen/updateStatus',
  async ({ kitchenOrderId, status }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/kitchen-orders/${kitchenOrderId}/status?status=${status}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update status');
    }
  }
);
