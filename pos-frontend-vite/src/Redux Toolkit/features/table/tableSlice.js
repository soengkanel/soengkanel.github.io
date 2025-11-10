import { createSlice } from '@reduxjs/toolkit';
import {
  fetchTables,
  fetchAvailableTables,
  createTable,
  updateTable,
  updateTableStatus,
  assignOrderToTable,
  releaseTable,
  deleteTable,
} from './tableThunks';

const initialState = {
  tables: [],
  availableTables: [],
  currentTable: null,
  loading: false,
  error: null,
};

const tableSlice = createSlice({
  name: 'table',
  initialState,
  reducers: {
    clearCurrentTable: (state) => {
      state.currentTable = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTables.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTables.fulfilled, (state, action) => {
        state.loading = false;
        state.tables = action.payload;
      })
      .addCase(fetchTables.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(fetchAvailableTables.fulfilled, (state, action) => {
        state.availableTables = action.payload;
      })

      .addCase(createTable.fulfilled, (state, action) => {
        state.tables.push(action.payload);
      })

      .addCase(updateTable.fulfilled, (state, action) => {
        const index = state.tables.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tables[index] = action.payload;
        }
      })

      .addCase(updateTableStatus.fulfilled, (state, action) => {
        const index = state.tables.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tables[index] = action.payload;
        }
      })

      .addCase(assignOrderToTable.fulfilled, (state, action) => {
        const index = state.tables.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tables[index] = action.payload;
        }
      })

      .addCase(releaseTable.fulfilled, (state, action) => {
        const index = state.tables.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tables[index] = action.payload;
        }
      })

      .addCase(deleteTable.fulfilled, (state, action) => {
        state.tables = state.tables.filter((t) => t.id !== action.payload);
      });
  },
});

export const { clearCurrentTable, clearError } = tableSlice.actions;
export default tableSlice.reducer;
