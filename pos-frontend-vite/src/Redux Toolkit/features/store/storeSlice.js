import { createSlice } from '@reduxjs/toolkit';
import {
  createStore,
  getStoreById,
  getAllStores,
  updateStore,
  deleteStore,
  getStoreByAdmin,
  getStoreByEmployee,
  getStoreEmployees,
  addEmployee,
  moderateStore, // <-- Add this import
} from './storeThunks';

const initialState = {
  store: null,
  stores: [],
  employees: [],
  loading: false,
  error: null,
};

const storeSlice = createSlice({
  name: 'store',
  initialState,
  reducers: {
    clearStoreState: (state) => {
      state.store = null;
      state.error = null;
      state.employees = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createStore.pending, (state) => {
        state.loading = true;
      })
      .addCase(createStore.fulfilled, (state, action) => {
        state.loading = false;
        state.store = action.payload;
      })
      .addCase(createStore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(getStoreById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getStoreById.fulfilled, (state, action) => {
        state.loading = false;
        state.store = action.payload;
      })
      .addCase(getStoreById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch store';
      })
      .addCase(getAllStores.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getAllStores.fulfilled, (state, action) => {
        state.loading = false;
        state.stores = action.payload;
      })
      .addCase(getAllStores.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch stores';
      })
      .addCase(updateStore.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateStore.fulfilled, (state, action) => {
        state.loading = false;
        state.store = action.payload;
      })
      .addCase(updateStore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update store';
      })
      .addCase(deleteStore.fulfilled, (state) => {
        state.store = null;
      })
      .addCase(getStoreByAdmin.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getStoreByAdmin.fulfilled, (state, action) => {
        state.loading = false;
        state.store = action.payload;
      })
      .addCase(getStoreByAdmin.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch store';
        state.store = null;
      })
      .addCase(getStoreByEmployee.fulfilled, (state, action) => {
        state.store = action.payload;
      })
      .addCase(getStoreEmployees.fulfilled, (state, action) => {
        state.employees = action.payload;
      })
      .addCase(addEmployee.fulfilled, (state, action) => {
        state.employees.push(action.payload);
      })

      // Update store in list after moderation
      .addCase(moderateStore.fulfilled, (state, action) => {
        const updated = action.payload;
        state.stores = state.stores.map(store =>
          store.id === updated.id ? updated : store
        );
      })

      .addMatcher(
        (action) => action.type.startsWith('store/') && action.type.endsWith('/rejected'),
        (state, action) => {
          state.error = action.payload;
        }
      );
  },
});

export const { clearStoreState } = storeSlice.actions;
export default storeSlice.reducer;
