import { createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../../utils/api';

export const fetchMenuItems = createAsyncThunk(
  'menuItem/fetchAll',
  async (storeId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/menu-items?storeId=${storeId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch menu items');
    }
  }
);

export const fetchAvailableMenuItems = createAsyncThunk(
  'menuItem/fetchAvailable',
  async (storeId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/menu-items/available?storeId=${storeId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch available menu items');
    }
  }
);

export const createMenuItem = createAsyncThunk(
  'menuItem/create',
  async ({ menuItemData, storeId }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/menu-items?storeId=${storeId}`, menuItemData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create menu item');
    }
  }
);

export const updateMenuItem = createAsyncThunk(
  'menuItem/update',
  async ({ menuItemId, menuItemData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/menu-items/${menuItemId}`, menuItemData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update menu item');
    }
  }
);

export const deleteMenuItem = createAsyncThunk(
  'menuItem/delete',
  async (menuItemId, { rejectWithValue }) => {
    try {
      await api.delete(`/menu-items/${menuItemId}`);
      return menuItemId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete menu item');
    }
  }
);

export const toggleMenuItemAvailability = createAsyncThunk(
  'menuItem/toggleAvailability',
  async ({ menuItemId, isAvailable }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/menu-items/${menuItemId}/availability?isAvailable=${isAvailable}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to toggle availability');
    }
  }
);

export const searchMenuItems = createAsyncThunk(
  'menuItem/search',
  async ({ storeId, keyword }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/menu-items/search?storeId=${storeId}&keyword=${keyword}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search menu items');
    }
  }
);

export const fetchMenuItemsByCourseType = createAsyncThunk(
  'menuItem/fetchByCourseType',
  async ({ storeId, courseType }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/menu-items/course/${courseType}?storeId=${storeId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch menu items');
    }
  }
);
