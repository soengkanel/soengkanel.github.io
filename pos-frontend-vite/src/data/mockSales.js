// Mock Sales Data for Testing - Cambodia
// This file contains ready-to-use sales transactions from different branches

// Generate random sales for the last 30 days
const generateSalesData = () => {
  const sales = [];
  const branches = [
    { id: 1, name: "Phnom Penh Central" },
    { id: 2, name: "Aeon Mall" },
    { id: 3, name: "Pochentong Airport" },
    { id: 4, name: "Riverside Cafe" },
    { id: 5, name: "BKK1 Express" },
  ];

  const paymentMethods = ["CASH", "CARD", "ABA_PAY", "WING", "PI_PAY"];
  const cashiers = [
    "Dara Pich",
    "Channary Seng",
    "Piseth Rath",
    "Bopha Keo",
    "Ratanak Mao",
    "Sreymom Nov",
  ];

  let saleId = 1;

  // Generate sales for last 30 days
  for (let day = 29; day >= 0; day--) {
    const date = new Date();
    date.setDate(date.getDate() - day);
    date.setHours(0, 0, 0, 0);

    // Number of sales per day (higher on weekends)
    const isWeekend = date.getDay() === 0 || date.getDay() === 6;
    const salesPerDay = isWeekend ? 30 + Math.floor(Math.random() * 20) : 20 + Math.floor(Math.random() * 15);

    for (let i = 0; i < salesPerDay; i++) {
      // Random time during business hours (8 AM - 10 PM)
      const hour = 8 + Math.floor(Math.random() * 14);
      const minute = Math.floor(Math.random() * 60);
      const saleDate = new Date(date);
      saleDate.setHours(hour, minute, 0, 0);

      // Random branch (weighted towards popular ones)
      const branchWeights = [0.35, 0.25, 0.20, 0.12, 0.08]; // More sales at main branches
      let random = Math.random();
      let branchIndex = 0;
      for (let j = 0; j < branchWeights.length; j++) {
        random -= branchWeights[j];
        if (random <= 0) {
          branchIndex = j;
          break;
        }
      }
      const branch = branches[branchIndex];

      // Random payment method (Cambodia specific - cash and mobile payments popular)
      const paymentWeights = [0.30, 0.20, 0.20, 0.20, 0.10]; // Cash still popular
      random = Math.random();
      let paymentIndex = 0;
      for (let j = 0; j < paymentWeights.length; j++) {
        random -= paymentWeights[j];
        if (random <= 0) {
          paymentIndex = j;
          break;
        }
      }
      const paymentMethod = paymentMethods[paymentIndex];

      // Random amount (in KHR - Cambodian Riel)
      // Average meal: 20,000 - 200,000 KHR ($5 - $50)
      const baseAmount = 20000 + Math.floor(Math.random() * 180000);
      const items = 1 + Math.floor(Math.random() * 5);
      const totalAmount = baseAmount * items;

      // Tax (10% VAT in Cambodia)
      const tax = Math.floor(totalAmount * 0.10);
      const subtotal = totalAmount - tax;

      // Random cashier
      const cashier = cashiers[Math.floor(Math.random() * cashiers.length)];

      sales.push({
        id: saleId++,
        orderNumber: `ORD-${String(saleId).padStart(6, '0')}`,
        branchId: branch.id,
        branchName: branch.name,
        date: saleDate.toISOString(),
        timestamp: saleDate.getTime(),
        subtotal: subtotal,
        tax: tax,
        totalAmount: totalAmount,
        paymentMethod: paymentMethod,
        cashierName: cashier,
        itemCount: items,
        status: "COMPLETED",
        customerType: Math.random() > 0.3 ? "WALK_IN" : "REGULAR",
      });
    }
  }

  return sales;
};

export const mockSales = generateSalesData();

// Calculate daily sales for charts
export const getDailySales = () => {
  const dailyMap = {};

  mockSales.forEach((sale) => {
    const date = new Date(sale.date);
    const dateKey = date.toISOString().split('T')[0];

    if (!dailyMap[dateKey]) {
      dailyMap[dateKey] = {
        date: dateKey,
        totalAmount: 0,
        orderCount: 0,
        averageOrder: 0,
      };
    }

    dailyMap[dateKey].totalAmount += sale.totalAmount;
    dailyMap[dateKey].orderCount += 1;
  });

  // Calculate averages
  Object.keys(dailyMap).forEach((key) => {
    dailyMap[key].averageOrder = Math.floor(
      dailyMap[key].totalAmount / dailyMap[key].orderCount
    );
  });

  return Object.values(dailyMap).sort((a, b) =>
    new Date(a.date) - new Date(b.date)
  );
};

// Calculate sales by payment method
export const getSalesByPaymentMethod = () => {
  const paymentMap = {};

  mockSales.forEach((sale) => {
    if (!paymentMap[sale.paymentMethod]) {
      paymentMap[sale.paymentMethod] = {
        paymentMethod: sale.paymentMethod,
        totalAmount: 0,
        orderCount: 0,
      };
    }

    paymentMap[sale.paymentMethod].totalAmount += sale.totalAmount;
    paymentMap[sale.paymentMethod].orderCount += 1;
  });

  return Object.values(paymentMap).sort((a, b) => b.totalAmount - a.totalAmount);
};

// Calculate sales by branch
export const getSalesByBranch = () => {
  const branchMap = {};

  mockSales.forEach((sale) => {
    if (!branchMap[sale.branchId]) {
      branchMap[sale.branchId] = {
        branchId: sale.branchId,
        branchName: sale.branchName,
        totalAmount: 0,
        orderCount: 0,
        averageOrder: 0,
      };
    }

    branchMap[sale.branchId].totalAmount += sale.totalAmount;
    branchMap[sale.branchId].orderCount += 1;
  });

  // Calculate averages
  Object.keys(branchMap).forEach((key) => {
    branchMap[key].averageOrder = Math.floor(
      branchMap[key].totalAmount / branchMap[key].orderCount
    );
  });

  return Object.values(branchMap).sort((a, b) => b.totalAmount - a.totalAmount);
};

// Get store overview
export const getStoreOverview = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const lastWeekStart = new Date(today);
  lastWeekStart.setDate(lastWeekStart.getDate() - 7);

  const previousWeekStart = new Date(lastWeekStart);
  previousWeekStart.setDate(previousWeekStart.getDate() - 7);

  // Today's sales
  const todaySales = mockSales.filter((sale) => {
    const saleDate = new Date(sale.date);
    return saleDate >= today;
  });

  // Yesterday's sales
  const yesterdaySales = mockSales.filter((sale) => {
    const saleDate = new Date(sale.date);
    return saleDate >= yesterday && saleDate < today;
  });

  // Last 7 days
  const lastWeekSales = mockSales.filter((sale) => {
    const saleDate = new Date(sale.date);
    return saleDate >= lastWeekStart;
  });

  // Previous 7 days
  const previousWeekSales = mockSales.filter((sale) => {
    const saleDate = new Date(sale.date);
    return saleDate >= previousWeekStart && saleDate < lastWeekStart;
  });

  // Calculate totals
  const totalSales = lastWeekSales.reduce((sum, sale) => sum + sale.totalAmount, 0);
  const previousPeriodSales = previousWeekSales.reduce((sum, sale) => sum + sale.totalAmount, 0);

  const todayOrders = todaySales.length;
  const yesterdayOrders = yesterdaySales.length;

  const averageOrderValue = lastWeekSales.length > 0
    ? Math.floor(totalSales / lastWeekSales.length)
    : 0;

  const previousPeriodAverageOrderValue = previousWeekSales.length > 0
    ? Math.floor(previousPeriodSales / previousWeekSales.length)
    : 0;

  // Get unique cashiers
  const uniqueCashiers = new Set(todaySales.map((sale) => sale.cashierName));
  const activeCashiers = uniqueCashiers.size;

  return {
    totalSales,
    previousPeriodSales,
    todayOrders,
    yesterdayOrders,
    averageOrderValue,
    previousPeriodAverageOrderValue,
    activeCashiers,
    totalOrders: lastWeekSales.length,
  };
};

// Get top selling items (mock data)
export const getTopSellingItems = () => {
  return [
    { id: 1, name: "Amok Trey (Fish Amok)", quantity: 145, revenue: 29000000 },
    { id: 2, name: "Lok Lak (Khmer Stir Fry)", quantity: 132, revenue: 26400000 },
    { id: 3, name: "Kuy Teav (Noodle Soup)", quantity: 198, revenue: 19800000 },
    { id: 4, name: "Bai Sach Chrouk (Pork & Rice)", quantity: 167, revenue: 16700000 },
    { id: 5, name: "Fresh Coconut Juice", quantity: 223, revenue: 8920000 },
  ];
};

// Helper functions
export const getSalesInDateRange = (startDate, endDate) => {
  return mockSales.filter((sale) => {
    const saleDate = new Date(sale.date);
    return saleDate >= startDate && saleDate <= endDate;
  });
};

export const getSalesByBranchInDateRange = (branchId, startDate, endDate) => {
  return mockSales.filter((sale) => {
    const saleDate = new Date(sale.date);
    return (
      sale.branchId === branchId &&
      saleDate >= startDate &&
      saleDate <= endDate
    );
  });
};

export default mockSales;
