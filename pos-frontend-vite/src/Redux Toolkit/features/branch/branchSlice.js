import { createSlice } from '@reduxjs/toolkit';
import {
  createBranch,
  getBranchById,
  getAllBranchesByStore,
  updateBranch,
  deleteBranch,
  // addEmployeeToBranch,
  // getEmployeesByBranch
} from './branchThunks';
import { mockBranches } from '../../../data/mockBranches';

const initialState = {
  branch: null,
  branches: mockBranches, // Initialize with mock data
  employees: [],
  loading: false,
  error: null,
};

const branchSlice = createSlice({
  name: 'branch',
  initialState,
  reducers: {
    clearBranchState: (state) => {
      state.branch = null;
      state.branches = [];
      state.employees = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createBranch.pending, (state) => {
        state.loading = true;
      })
      .addCase(createBranch.fulfilled, (state, action) => {
        state.loading = false;
        state.branch = action.payload;
        state.branches.push(action.payload);
      })
      .addCase(createBranch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(getBranchById.pending, (state) => {
        state.loading = true;
      })
      .addCase(getBranchById.fulfilled, (state, action) => {
        state.loading = false;
        state.branch = action.payload;
      })
      .addCase(getBranchById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(getAllBranchesByStore.fulfilled, (state, action) => {
        // If API returns data, merge it with mock data, otherwise keep mock data
        if (action.payload && action.payload.length > 0) {
          // Merge API branches with mock branches, prioritizing API data
          const apiBranchIds = action.payload.map(b => b.id);
          const mockOnlyBranches = mockBranches.filter(mb => !apiBranchIds.includes(mb.id));
          state.branches = [...action.payload, ...mockOnlyBranches];
        }
        // If no API data, branches already contains mock data from initialState
      })

      .addCase(updateBranch.fulfilled, (state, action) => {
        state.branch = action.payload;
      })

      .addCase(deleteBranch.fulfilled, (state, action) => {
        state.branches = state.branches.filter((b) => b.id !== action.payload);
      })



      .addMatcher(
        (action) => action.type.startsWith('branch/') && action.type.endsWith('/rejected'),
        (state, action) => {
          state.error = action.payload;
          state.loading = false;
        }
      );
  },
});

export const { clearBranchState } = branchSlice.actions;
export default branchSlice.reducer;
