// Mock Employees Data for Testing
// This file contains employee accounts with proper structure

export const mockEmployees = [];

// Helper functions
export const getEmployeesByRole = (role) => {
  return mockEmployees.filter(emp => emp.role === role);
};

export const getEmployeesByBranch = (branchId) => {
  return mockEmployees.filter(emp => emp.branchId === branchId);
};

export const getActiveEmployees = () => {
  return mockEmployees.filter(emp => emp.status === "ACTIVE");
};

export const getEmployeeByEmail = (email) => {
  return mockEmployees.find(emp => emp.email === email);
};

// Export employee roles for reference
export const employeeRoles = [
  "ROLE_STORE_MANAGER",
  "ROLE_BRANCH_MANAGER",
  "ROLE_CASHIER",
  "ROLE_KITCHEN_STAFF",
  "ROLE_WAITER",
  "ROLE_INVENTORY_MANAGER",
  "ROLE_ACCOUNTANT",
  "ROLE_HR_MANAGER"
];

// Login credentials summary
export const loginCredentials = {};

export default mockEmployees;
