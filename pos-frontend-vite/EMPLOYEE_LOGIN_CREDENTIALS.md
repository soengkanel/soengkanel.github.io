# Employee Login Credentials

This document contains ready-to-use test employee accounts for the NGPOS system.

---

## 🏢 Store Managers
**Access Level**: Full store management, all branches

| Name | Email | Password | Department |
|------|-------|----------|------------|
| Sarah Johnson | `sarah.manager@ngpos.com` | `Manager@123` | Management |
| Michael Chen | `michael.manager@ngpos.com` | `Manager@123` | Management |

---

## 🏪 Branch Managers
**Access Level**: Single branch management

| Name | Email | Password | Branch | Department |
|------|-------|----------|--------|------------|
| Emily Rodriguez | `emily.branch@ngpos.com` | `Branch@123` | Downtown | Operations |
| James Wilson | `james.branch@ngpos.com` | `Branch@123` | Mall | Operations |
| Lisa Anderson | `lisa.branch@ngpos.com` | `Branch@123` | Airport | Operations |

---

## 💰 Cashiers
**Access Level**: POS operations, sales transactions

| Name | Email | Password | Branch | Shift |
|------|-------|----------|--------|-------|
| David Martinez | `david.cashier@ngpos.com` | `Cashier@123` | Downtown | 09:00-17:00 |
| Jennifer Lee | `jennifer.cashier@ngpos.com` | `Cashier@123` | Downtown | 13:00-21:00 |
| Robert Taylor | `robert.cashier@ngpos.com` | `Cashier@123` | Mall | 09:00-17:00 |
| Amanda White | `amanda.cashier@ngpos.com` | `Cashier@123` | Mall | 10:00-18:00 |
| Christopher Brown | `chris.cashier@ngpos.com` | `Cashier@123` | Airport | 06:00-14:00 |
| Sophia Garcia | `sophia.cashier@ngpos.com` | `Cashier@123` | Airport | 14:00-22:00 |

---

## 👨‍🍳 Kitchen Staff (F&B)
**Access Level**: Kitchen order management

| Name | Email | Password | Branch | Specialization |
|------|-------|----------|--------|----------------|
| Antonio Rossi | `antonio.chef@ngpos.com` | `Kitchen@123` | Downtown | Italian Cuisine |
| Marie Dubois | `marie.chef@ngpos.com` | `Kitchen@123` | Mall | French Cuisine |

---

## 🍽️ Waiters/Servers (F&B)
**Access Level**: Table service, order taking

| Name | Email | Password | Branch | Shift |
|------|-------|----------|--------|-------|
| Kevin Thompson | `kevin.waiter@ngpos.com` | `Waiter@123` | Downtown | 11:00-19:00 |
| Rachel Green | `rachel.waiter@ngpos.com` | `Waiter@123` | Mall | 17:00-23:00 |

---

## 📦 Other Staff Roles
**Access Level**: Specialized departments

| Name | Email | Password | Role | Department |
|------|-------|----------|------|------------|
| Daniel Kim | `daniel.inventory@ngpos.com` | `Inventory@123` | Inventory Manager | Inventory |
| Patricia Miller | `patricia.accountant@ngpos.com` | `Account@123` | Accountant | Finance |
| Thomas Anderson | `thomas.hr@ngpos.com` | `HRManager@123` | HR Manager | Human Resources |

---

## ⏰ Part-Time Staff

| Name | Email | Password | Branch | Type | Shift |
|------|-------|----------|--------|------|-------|
| Jessica Davis | `jessica.parttime@ngpos.com` | `Cashier@123` | Downtown | Part-Time Cashier | 17:00-21:00 |
| Ryan Mitchell | `ryan.parttime@ngpos.com` | `Cashier@123` | Mall | Part-Time Cashier | 18:00-22:00 |

---

## 🔐 Quick Login Guide

### Testing Cashier Interface
```
Email: david.cashier@ngpos.com
Password: Cashier@123
Branch: Downtown
```

### Testing Branch Manager
```
Email: emily.branch@ngpos.com
Password: Branch@123
Branch: Downtown
```

### Testing Store Manager
```
Email: sarah.manager@ngpos.com
Password: Manager@123
Access: All Branches
```

---

## 📝 Notes

1. **Password Policy**: All passwords follow the format `Role@123` for easy testing
2. **Branches**:
   - Branch 1: Downtown Branch
   - Branch 2: Mall Branch
   - Branch 3: Airport Branch
3. **Employee Roles**:
   - `ROLE_STORE_MANAGER` - Full store access
   - `ROLE_BRANCH_MANAGER` - Branch-level management
   - `ROLE_BRANCH_CASHIER` - POS operations
   - `ROLE_KITCHEN_STAFF` - Kitchen operations (F&B)
   - `ROLE_WAITER` - Table service (F&B)
   - `ROLE_INVENTORY_MANAGER` - Stock management
   - `ROLE_ACCOUNTANT` - Financial operations
   - `ROLE_HR_MANAGER` - HR operations

4. **Data Location**: All employee data is stored in:
   - `/src/data/mockEmployees.js`

---

## 🚀 Usage in Code

```javascript
import { mockEmployees, loginCredentials, getEmployeeByEmail } from '@/data/mockEmployees';

// Get specific employee
const employee = getEmployeeByEmail('david.cashier@ngpos.com');

// Get all cashiers
const cashiers = mockEmployees.filter(emp => emp.role === 'ROLE_BRANCH_CASHIER');

// Get employees by branch
const downtownStaff = mockEmployees.filter(emp => emp.branchId === 1);
```

---

**Created**: 2025
**Last Updated**: 2025-10-15
**Total Employees**: 20
