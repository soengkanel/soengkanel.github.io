import { createSlice } from '@reduxjs/toolkit';
import {
  fetchActiveKitchenOrders,
  fetchKitchenOrdersByStation,
  fetchPendingOrders,
  fetchReadyOrders,
  createKitchenOrder,
  startPreparation,
  completePreparation,
  updateKitchenOrderStatus,
} from './kitchenThunks';

const initialState = {
  activeOrders: [],
  stationOrders: [],
  pendingOrders: [],
  readyOrders: [],
  loading: false,
  error: null,
};

const kitchenSlice = createSlice({
  name: 'kitchen',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchActiveKitchenOrders.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchActiveKitchenOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.activeOrders = action.payload;
      })
      .addCase(fetchActiveKitchenOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(fetchKitchenOrdersByStation.fulfilled, (state, action) => {
        state.stationOrders = action.payload;
      })

      .addCase(fetchPendingOrders.fulfilled, (state, action) => {
        state.pendingOrders = action.payload;
      })

      .addCase(fetchReadyOrders.fulfilled, (state, action) => {
        state.readyOrders = action.payload;
      })

      .addCase(createKitchenOrder.fulfilled, (state, action) => {
        state.activeOrders.push(action.payload);
        state.pendingOrders.push(action.payload);
      })

      .addCase(startPreparation.fulfilled, (state, action) => {
        const index = state.activeOrders.findIndex((o) => o.id === action.payload.id);
        if (index !== -1) {
          state.activeOrders[index] = action.payload;
        }
        state.pendingOrders = state.pendingOrders.filter((o) => o.id !== action.payload.id);
      })

      .addCase(completePreparation.fulfilled, (state, action) => {
        state.activeOrders = state.activeOrders.filter((o) => o.id !== action.payload.id);
        state.readyOrders.push(action.payload);
      })

      .addCase(updateKitchenOrderStatus.fulfilled, (state, action) => {
        const index = state.activeOrders.findIndex((o) => o.id === action.payload.id);
        if (index !== -1) {
          state.activeOrders[index] = action.payload;
        }
      });
  },
});

export const { clearError } = kitchenSlice.actions;
export default kitchenSlice.reducer;
