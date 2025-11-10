import { createSlice } from '@reduxjs/toolkit';
import {
  fetchMenuItems,
  fetchAvailableMenuItems,
  createMenuItem,
  updateMenuItem,
  deleteMenuItem,
  toggleMenuItemAvailability,
  searchMenuItems,
  fetchMenuItemsByCourseType,
} from './menuItemThunks';

const initialState = {
  menuItems: [],
  availableMenuItems: [],
  currentMenuItem: null,
  loading: false,
  error: null,
  searchResults: [],
};

const menuItemSlice = createSlice({
  name: 'menuItem',
  initialState,
  reducers: {
    clearCurrentMenuItem: (state) => {
      state.currentMenuItem = null;
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
      // Fetch menu items
      .addCase(fetchMenuItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMenuItems.fulfilled, (state, action) => {
        state.loading = false;
        state.menuItems = action.payload;
      })
      .addCase(fetchMenuItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch available menu items
      .addCase(fetchAvailableMenuItems.fulfilled, (state, action) => {
        state.availableMenuItems = action.payload;
      })

      // Create menu item
      .addCase(createMenuItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createMenuItem.fulfilled, (state, action) => {
        state.loading = false;
        state.menuItems.push(action.payload);
        if (action.payload.isAvailable) {
          state.availableMenuItems.push(action.payload);
        }
      })
      .addCase(createMenuItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update menu item
      .addCase(updateMenuItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateMenuItem.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.menuItems.findIndex((m) => m.id === action.payload.id);
        if (index !== -1) {
          state.menuItems[index] = action.payload;
        }
        const availableIndex = state.availableMenuItems.findIndex((m) => m.id === action.payload.id);
        if (action.payload.isAvailable && availableIndex === -1) {
          state.availableMenuItems.push(action.payload);
        } else if (!action.payload.isAvailable && availableIndex !== -1) {
          state.availableMenuItems.splice(availableIndex, 1);
        } else if (availableIndex !== -1) {
          state.availableMenuItems[availableIndex] = action.payload;
        }
      })
      .addCase(updateMenuItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete menu item
      .addCase(deleteMenuItem.fulfilled, (state, action) => {
        state.menuItems = state.menuItems.filter((m) => m.id !== action.payload);
        state.availableMenuItems = state.availableMenuItems.filter((m) => m.id !== action.payload);
      })

      // Toggle availability
      .addCase(toggleMenuItemAvailability.fulfilled, (state, action) => {
        const index = state.menuItems.findIndex((m) => m.id === action.payload.id);
        if (index !== -1) {
          state.menuItems[index] = action.payload;
        }
        if (action.payload.isAvailable) {
          const exists = state.availableMenuItems.find((m) => m.id === action.payload.id);
          if (!exists) {
            state.availableMenuItems.push(action.payload);
          }
        } else {
          state.availableMenuItems = state.availableMenuItems.filter((m) => m.id !== action.payload.id);
        }
      })

      // Search menu items
      .addCase(searchMenuItems.fulfilled, (state, action) => {
        state.searchResults = action.payload;
      })

      // Fetch by course type
      .addCase(fetchMenuItemsByCourseType.fulfilled, (state, action) => {
        state.searchResults = action.payload;
      });
  },
});

export const { clearCurrentMenuItem, clearError, clearSearchResults } = menuItemSlice.actions;
export default menuItemSlice.reducer;
