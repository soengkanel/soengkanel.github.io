import { createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../../utils/api';

export const fetchRetailProducts = createAsyncThunk(
  'retailProduct/fetchAll',
  async (storeId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/retail-products?storeId=${storeId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch products');
    }
  }
);

export const createRetailProduct = createAsyncThunk(
  'retailProduct/create',
  async ({ productData, storeId }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/retail-products?storeId=${storeId}`, productData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create product');
    }
  }
);

export const updateRetailProduct = createAsyncThunk(
  'retailProduct/update',
  async ({ productId, productData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/retail-products/${productId}`, productData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update product');
    }
  }
);

export const deleteRetailProduct = createAsyncThunk(
  'retailProduct/delete',
  async (productId, { rejectWithValue }) => {
    try {
      await api.delete(`/retail-products/${productId}`);
      return productId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete product');
    }
  }
);

export const searchRetailProducts = createAsyncThunk(
  'retailProduct/search',
  async ({ storeId, keyword }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/retail-products/search?storeId=${storeId}&keyword=${keyword}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search products');
    }
  }
);

export const fetchRetailProductByBarcode = createAsyncThunk(
  'retailProduct/fetchByBarcode',
  async (barcode, { rejectWithValue }) => {
    try {
      const response = await api.get(`/retail-products/barcode/${barcode}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Product not found');
    }
  }
);
