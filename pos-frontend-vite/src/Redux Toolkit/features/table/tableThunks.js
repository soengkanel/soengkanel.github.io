import { createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../../utils/api';

export const fetchTables = createAsyncThunk(
  'table/fetchAll',
  async (branchId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/tables?branchId=${branchId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch tables');
    }
  }
);

export const fetchAvailableTables = createAsyncThunk(
  'table/fetchAvailable',
  async (branchId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/tables/available?branchId=${branchId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch available tables');
    }
  }
);

export const createTable = createAsyncThunk(
  'table/create',
  async ({ tableData, branchId }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/tables?branchId=${branchId}`, tableData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create table');
    }
  }
);

export const updateTable = createAsyncThunk(
  'table/update',
  async ({ tableId, tableData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/tables/${tableId}`, tableData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update table');
    }
  }
);

export const updateTableStatus = createAsyncThunk(
  'table/updateStatus',
  async ({ tableId, status }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/tables/${tableId}/status?status=${status}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update table status');
    }
  }
);

export const assignOrderToTable = createAsyncThunk(
  'table/assignOrder',
  async ({ tableId, orderId }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/tables/${tableId}/assign-order?orderId=${orderId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to assign order to table');
    }
  }
);

export const releaseTable = createAsyncThunk(
  'table/release',
  async (tableId, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/tables/${tableId}/release`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to release table');
    }
  }
);

export const deleteTable = createAsyncThunk(
  'table/delete',
  async (tableId, { rejectWithValue }) => {
    try {
      await api.delete(`/tables/${tableId}`);
      return tableId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete table');
    }
  }
);
