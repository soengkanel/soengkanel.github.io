import { createSlice } from '@reduxjs/toolkit';
import {
  fetchRetailProducts,
  createRetailProduct,
  updateRetailProduct,
  deleteRetailProduct,
  searchRetailProducts,
  fetchRetailProductByBarcode,
} from './retailProductThunks';

const initialState = {
  products: [],
  currentProduct: null,
  loading: false,
  error: null,
  searchResults: [],
};

const retailProductSlice = createSlice({
  name: 'retailProduct',
  initialState,
  reducers: {
    clearCurrentProduct: (state) => {
      state.currentProduct = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch products
      .addCase(fetchRetailProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRetailProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchRetailProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Create product
      .addCase(createRetailProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createRetailProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.products.push(action.payload);
      })
      .addCase(createRetailProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update product
      .addCase(updateRetailProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateRetailProduct.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.products.findIndex((p) => p.id === action.payload.id);
        if (index !== -1) {
          state.products[index] = action.payload;
        }
      })
      .addCase(updateRetailProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete product
      .addCase(deleteRetailProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteRetailProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.products = state.products.filter((p) => p.id !== action.payload);
      })
      .addCase(deleteRetailProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Search products
      .addCase(searchRetailProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchRetailProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchRetailProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch by barcode
      .addCase(fetchRetailProductByBarcode.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRetailProductByBarcode.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProduct = action.payload;
      })
      .addCase(fetchRetailProductByBarcode.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearCurrentProduct, clearError, clearSearchResults } = retailProductSlice.actions;
export default retailProductSlice.reducer;
