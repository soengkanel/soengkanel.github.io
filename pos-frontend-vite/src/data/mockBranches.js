// Mock Branches Data for Testing - Cambodia Locations
// This file contains ready-to-use branch data for multi-location stores in Cambodia

/**
 * IMPORTANT: Branch Business Type
 *
 * Each branch has a `businessType` field (FNB, RETAIL, or HYBRID) that:
 *   - Determines the branch CAPABILITIES (what it can do)
 *   - MUST match the parent store's business type
 *   - Is NOT editable by user - automatically inherited from store
 *   - Controls whether branch has: tables, menu, inventory, etc.
 *
 * Examples:
 *   - Store businessType: "FNB" → All branches get businessType: "FNB"
 *   - Store businessType: "RETAIL" → All branches get businessType: "RETAIL"
 *   - Store businessType: "HYBRID" → All branches get businessType: "HYBRID"
 *
 * The business type is the ONLY type classification we need.
 *
 * Mock Data Organization:
 *   - Branches 1-2: HYBRID store (Store ID: 1) - "Khmer Delight Group"
 *   - Branches 3-5: FNB store (Store ID: 2) - "Cambodia Kitchen"
 *   - Branches 6-10: RETAIL store (Store ID: 3) - "Cambodia Fashion"
 */

export const mockBranches = [];

// Branch statistics
export const branchStats = {
  total: mockBranches.length,
  active: mockBranches.filter(b => b.status === "ACTIVE").length,
  comingSoon: mockBranches.filter(b => b.status === "COMING_SOON").length,
  underMaintenance: mockBranches.filter(b => b.status === "UNDER_MAINTENANCE").length,
  totalEmployees: mockBranches.reduce((sum, b) => sum + b.employees, 0),
  totalRevenue: mockBranches.reduce((sum, b) => sum + b.monthlyRevenue, 0)
};

// Helper functions
export const getBranchById = (id) => {
  return mockBranches.find(branch => branch.id === id);
};

export const getBranchesByStatus = (status) => {
  return mockBranches.filter(branch => branch.status === status);
};

export const getBranchesByBusinessType = (businessType) => {
  return mockBranches.filter(branch => branch.businessType === businessType);
};

export const getBranchesByStoreId = (storeId) => {
  return mockBranches.filter(branch => branch.storeId === storeId);
};

export const getActiveBranches = () => {
  return mockBranches.filter(branch => branch.status === "ACTIVE");
};

export const getBranchesByCity = (city) => {
  return mockBranches.filter(branch => branch.city === city);
};

// Branch statuses
export const branchStatuses = {
  ACTIVE: "Active",
  COMING_SOON: "Coming Soon",
  UNDER_MAINTENANCE: "Under Maintenance",
  CLOSED: "Closed"
};

// Business types (matches store types)
export const businessTypes = {
  RETAIL: "Retail",
  FNB: "Food & Beverage",
  HYBRID: "Retail + F&B"
};

export default mockBranches;
