// Mock F&B Menu Items Data for Testing
// This file contains fake restaurant menu items across various categories

// Menu categories with store and branch relationships
// storeId: null means it's a template available to all stores
// branchIds: [] means available to all branches, or specify specific branches
export const mockMenuCategories = [
  {
    id: 1,
    name: "Appetizers",
    description: "Start your meal with these delicious starters",
    displayOrder: 1,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1541529086526-db283c563270?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null, // Available as template for all stores
    branchIds: [] // Empty means available to all branches of a store
  },
  {
    id: 2,
    name: "Main Course",
    description: "Hearty and satisfying main dishes",
    displayOrder: 2,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null,
    branchIds: []
  },
  {
    id: 3,
    name: "Beverages",
    description: "Refreshing drinks and beverages",
    displayOrder: 3,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null,
    branchIds: []
  },
  {
    id: 4,
    name: "Desserts",
    description: "Sweet treats to end your meal",
    displayOrder: 4,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null,
    branchIds: []
  },
  {
    id: 5,
    name: "Salads",
    description: "Fresh and healthy salad options",
    displayOrder: 5,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null,
    branchIds: []
  },
  {
    id: 6,
    name: "Pasta & Noodles",
    description: "Classic pasta and noodle dishes",
    displayOrder: 6,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null,
    branchIds: []
  },
  {
    id: 7,
    name: "Breakfast",
    description: "Morning favorites",
    displayOrder: 7,
    isActive: true,
    imageUrl: "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400&h=300&fit=crop",
    createdAt: "2024-01-15T10:00:00Z",
    storeId: null,
    branchIds: [1, 4] // Only available at Phnom Penh Central and Riverside Cafe (breakfast service)
  }
];

// Menu items with branch-specific availability and pricing
// branchPricing: [{ branchId, price, available }]
// Empty array = available at all branches with basePrice
export const mockMenuItems = [
  // Appetizers
  {
    id: 1,
    name: "Classic Bruschetta",
    description: "Toasted bread topped with fresh tomatoes, basil, garlic, and olive oil",
    basePrice: 8.99, // Default price for all branches
    categoryId: 1,
    categoryName: "Appetizers",
    isAvailable: true,
    preparationTime: 10,
    calories: 180,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten"],
    imageUrl: "https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=400&h=300&fit=crop",
    station: "KITCHEN",
    storeId: null, // Template for all stores
    branchPricing: [
      { branchId: 2, price: 9.99, available: true },  // Aeon Mall (premium pricing)
      { branchId: 3, price: null, available: false }  // Airport (not available - quick service only)
    ]
    // Branch 1 (Downtown) and 4 (Riverside) use basePrice
  },
  {
    id: 2,
    name: "Buffalo Wings",
    description: "Crispy chicken wings tossed in spicy buffalo sauce, served with ranch",
    basePrice: 12.99,
    categoryId: 1,
    categoryName: "Appetizers",
    isAvailable: true,
    preparationTime: 15,
    calories: 420,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 3,
    allergens: ["dairy"],
    imageUrl: "https://images.unsplash.com/photo-1608039829572-78524f79c4c7?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: [] // Available at all branches with base price
  },
  {
    id: 3,
    name: "Mozzarella Sticks",
    description: "Golden fried mozzarella cheese with marinara dipping sauce",
    basePrice: 9.99,
    branchPricing: [],
    categoryId: 1,
    categoryName: "Appetizers",
    isAvailable: true,
    preparationTime: 12,
    calories: 350,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["dairy", "gluten"],
    imageUrl: "https://images.unsplash.com/photo-1531749668029-2db88e4276c7?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 4,
    name: "Spring Rolls",
    description: "Crispy vegetable spring rolls with sweet chili sauce",
    basePrice:7.99,
    categoryId: 1,
    categoryName: "Appetizers",
    isAvailable: true,
    preparationTime: 8,
    calories: 220,
    isVegetarian: true,
    isVegan: true,
    isGlutenFree: false,
    spicyLevel: 1,
    allergens: ["gluten", "soy"],
    imageUrl: "https://images.unsplash.com/photo-1593501947551-c5c1e95b9b2e?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },

  // Main Course
  {
    id: 5,
    name: "Grilled Salmon",
    description: "Atlantic salmon fillet with lemon butter sauce, served with vegetables",
    basePrice:24.99,
    categoryId: 2,
    categoryName: "Main Course",
    isAvailable: true,
    preparationTime: 20,
    calories: 480,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: ["fish", "dairy"],
    imageUrl: "https://images.unsplash.com/photo-1485921325833-c519f76c4927?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 6,
    name: "BBQ Ribs",
    description: "Slow-cooked pork ribs with house BBQ sauce, coleslaw, and fries",
    basePrice:22.99,
    categoryId: 2,
    categoryName: "Main Course",
    isAvailable: true,
    preparationTime: 25,
    calories: 780,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 1,
    allergens: [],
    imageUrl: "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 7,
    name: "Chicken Parmesan",
    description: "Breaded chicken breast with marinara sauce and melted cheese",
    basePrice:18.99,
    categoryId: 2,
    categoryName: "Main Course",
    isAvailable: true,
    preparationTime: 18,
    calories: 620,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy"],
    imageUrl: "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 8,
    name: "Beef Steak",
    description: "8oz prime ribeye steak with garlic butter and mashed potatoes",
    basePrice:32.99,
    categoryId: 2,
    categoryName: "Main Course",
    isAvailable: true,
    preparationTime: 22,
    calories: 850,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: ["dairy"],
    imageUrl: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 9,
    name: "Vegetable Curry",
    description: "Mixed vegetables in aromatic curry sauce with basmati rice",
    basePrice:15.99,
    categoryId: 2,
    categoryName: "Main Course",
    isAvailable: true,
    preparationTime: 15,
    calories: 420,
    isVegetarian: true,
    isVegan: true,
    isGlutenFree: true,
    spicyLevel: 2,
    allergens: [],
    imageUrl: "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },

  // Beverages
  {
    id: 10,
    name: "Fresh Orange Juice",
    description: "Freshly squeezed orange juice",
    basePrice:4.99,
    categoryId: 3,
    categoryName: "Beverages",
    isAvailable: true,
    preparationTime: 3,
    calories: 110,
    isVegetarian: true,
    isVegan: true,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: [],
    imageUrl: "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop",
    station: "BAR",
    branchPricing: []
  },
  {
    id: 11,
    name: "Cappuccino",
    description: "Espresso with steamed milk and foam",
    basePrice:4.50,
    categoryId: 3,
    categoryName: "Beverages",
    isAvailable: true,
    preparationTime: 5,
    calories: 120,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: ["dairy"],
    imageUrl: "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400&h=300&fit=crop",
    station: "BAR",
    branchPricing: []
  },
  {
    id: 12,
    name: "Iced Tea",
    description: "Refreshing iced tea with lemon",
    basePrice:3.50,
    categoryId: 3,
    categoryName: "Beverages",
    isAvailable: true,
    preparationTime: 2,
    calories: 80,
    isVegetarian: true,
    isVegan: true,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: [],
    imageUrl: "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop",
    station: "BAR",
    branchPricing: []
  },
  {
    id: 13,
    name: "Mango Smoothie",
    description: "Blended mango with yogurt and honey",
    basePrice:5.99,
    categoryId: 3,
    categoryName: "Beverages",
    isAvailable: true,
    preparationTime: 4,
    calories: 210,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: ["dairy"],
    imageUrl: "https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=400&h=300&fit=crop",
    station: "BAR",
    branchPricing: []
  },
  {
    id: 14,
    name: "Craft Beer",
    description: "Local craft beer on tap",
    basePrice:6.50,
    categoryId: 3,
    categoryName: "Beverages",
    isAvailable: true,
    preparationTime: 1,
    calories: 180,
    isVegetarian: true,
    isVegan: true,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten"],
    imageUrl: "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400&h=300&fit=crop",
    station: "BAR",
    branchPricing: []
  },

  // Desserts
  {
    id: 15,
    name: "Chocolate Lava Cake",
    description: "Warm chocolate cake with molten center, served with vanilla ice cream",
    basePrice:8.99,
    categoryId: 4,
    categoryName: "Desserts",
    isAvailable: true,
    preparationTime: 12,
    calories: 520,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 16,
    name: "Tiramisu",
    description: "Classic Italian dessert with coffee-soaked ladyfingers and mascarpone",
    basePrice:7.99,
    categoryId: 4,
    categoryName: "Desserts",
    isAvailable: true,
    preparationTime: 5,
    calories: 450,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 17,
    name: "New York Cheesecake",
    description: "Creamy cheesecake with graham cracker crust and berry compote",
    basePrice:8.50,
    categoryId: 4,
    categoryName: "Desserts",
    isAvailable: true,
    preparationTime: 5,
    calories: 480,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1533134242-9a72389ec0d1?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 18,
    name: "Ice Cream Sundae",
    description: "Three scoops of ice cream with toppings and whipped cream",
    basePrice:6.99,
    categoryId: 4,
    categoryName: "Desserts",
    isAvailable: true,
    preparationTime: 5,
    calories: 420,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: ["dairy"],
    imageUrl: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },

  // Salads
  {
    id: 19,
    name: "Caesar Salad",
    description: "Romaine lettuce with Caesar dressing, croutons, and parmesan",
    basePrice:11.99,
    categoryId: 5,
    categoryName: "Salads",
    isAvailable: true,
    preparationTime: 8,
    calories: 280,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "fish"],
    imageUrl: "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 20,
    name: "Greek Salad",
    description: "Fresh vegetables with feta cheese, olives, and olive oil",
    basePrice:10.99,
    categoryId: 5,
    categoryName: "Salads",
    isAvailable: true,
    preparationTime: 7,
    calories: 220,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: ["dairy"],
    imageUrl: "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 21,
    name: "Grilled Chicken Salad",
    description: "Mixed greens with grilled chicken, avocado, and balsamic vinaigrette",
    basePrice:14.99,
    categoryId: 5,
    categoryName: "Salads",
    isAvailable: true,
    preparationTime: 10,
    calories: 320,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 0,
    allergens: [],
    imageUrl: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },

  // Pasta & Noodles
  {
    id: 22,
    name: "Spaghetti Carbonara",
    description: "Classic pasta with bacon, eggs, parmesan, and black pepper",
    basePrice:16.99,
    categoryId: 6,
    categoryName: "Pasta & Noodles",
    isAvailable: true,
    preparationTime: 15,
    calories: 580,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 23,
    name: "Pad Thai",
    description: "Thai stir-fried rice noodles with shrimp, peanuts, and tamarind sauce",
    basePrice:15.99,
    categoryId: 6,
    categoryName: "Pasta & Noodles",
    isAvailable: true,
    preparationTime: 12,
    calories: 520,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: true,
    spicyLevel: 2,
    allergens: ["shellfish", "peanuts", "soy"],
    imageUrl: "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 24,
    name: "Fettuccine Alfredo",
    description: "Fettuccine pasta in creamy parmesan sauce",
    basePrice:14.99,
    categoryId: 6,
    categoryName: "Pasta & Noodles",
    isAvailable: true,
    preparationTime: 13,
    calories: 640,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy"],
    imageUrl: "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 25,
    name: "Ramen Bowl",
    description: "Japanese noodle soup with pork, soft-boiled egg, and vegetables",
    basePrice:13.99,
    categoryId: 6,
    categoryName: "Pasta & Noodles",
    isAvailable: true,
    preparationTime: 18,
    calories: 550,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 1,
    allergens: ["gluten", "eggs", "soy"],
    imageUrl: "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },

  // Breakfast
  {
    id: 26,
    name: "Classic Pancakes",
    description: "Fluffy pancakes with maple syrup and butter",
    basePrice: 9.99,
    branchPricing: [],
    categoryId: 7,
    categoryName: "Breakfast",
    isAvailable: true,
    preparationTime: 10,
    calories: 420,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1528207776546-365bb710ee93?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 27,
    name: "Eggs Benedict",
    description: "Poached eggs on English muffin with hollandaise sauce and bacon",
    basePrice:12.99,
    categoryId: 7,
    categoryName: "Breakfast",
    isAvailable: true,
    preparationTime: 12,
    calories: 520,
    isVegetarian: false,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1608039829572-78524f79c4c7?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 28,
    name: "Avocado Toast",
    description: "Smashed avocado on sourdough with cherry tomatoes and feta",
    basePrice:11.99,
    categoryId: 7,
    categoryName: "Breakfast",
    isAvailable: true,
    preparationTime: 8,
    calories: 380,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy"],
    imageUrl: "https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 29,
    name: "Breakfast Burrito",
    description: "Scrambled eggs, cheese, beans, and salsa in a flour tortilla",
    basePrice:10.99,
    categoryId: 7,
    categoryName: "Breakfast",
    isAvailable: true,
    preparationTime: 10,
    calories: 580,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 1,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  },
  {
    id: 30,
    name: "French Toast",
    description: "Thick-cut brioche French toast with berries and whipped cream",
    basePrice:10.99,
    categoryId: 7,
    categoryName: "Breakfast",
    isAvailable: true,
    preparationTime: 12,
    calories: 480,
    isVegetarian: true,
    isVegan: false,
    isGlutenFree: false,
    spicyLevel: 0,
    allergens: ["gluten", "dairy", "eggs"],
    imageUrl: "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=400&h=300&fit=crop",
    station: "KITCHEN",
    branchPricing: []
  }
];

// Tables with branch relationships (Cambodia branches)
export const mockTables = [
  // Phnom Penh Central Branch (Branch ID: 1)
  {
    id: 1,
    tableNumber: "T1",
    capacity: 2,
    status: "AVAILABLE",
    location: "Main Dining",
    area: "Main Dining",
    qrCode: "QR-T1-001",
    isActive: true,
    branchId: 1,
    branchName: "Phnom Penh Central Branch"
  },
  {
    id: 2,
    tableNumber: "T2",
    capacity: 4,
    status: "OCCUPIED",
    location: "Main Dining",
    area: "Main Dining",
    qrCode: "QR-T2-002",
    isActive: true,
    branchId: 1,
    branchName: "Phnom Penh Central Branch"
  },
  {
    id: 3,
    tableNumber: "T3",
    capacity: 4,
    status: "AVAILABLE",
    location: "Main Dining",
    area: "Main Dining",
    qrCode: "QR-T3-003",
    isActive: true,
    branchId: 1,
    branchName: "Phnom Penh Central Branch"
  },
  {
    id: 4,
    tableNumber: "T4",
    capacity: 6,
    status: "RESERVED",
    location: "Private Room",
    area: "VIP",
    qrCode: "QR-T4-004",
    isActive: true,
    branchId: 1,
    branchName: "Phnom Penh Central Branch"
  },
  {
    id: 5,
    tableNumber: "T5",
    capacity: 2,
    status: "AVAILABLE",
    location: "Patio",
    area: "Outdoor",
    qrCode: "QR-T5-005",
    isActive: true,
    branchId: 1,
    branchName: "Phnom Penh Central Branch"
  },

  // Aeon Mall Branch (Branch ID: 2)
  {
    id: 6,
    tableNumber: "T1",
    capacity: 4,
    status: "AVAILABLE",
    location: "Food Court",
    area: "Main Area",
    qrCode: "QR-T6-006",
    isActive: true,
    branchId: 2,
    branchName: "Aeon Mall"
  },
  {
    id: 7,
    tableNumber: "T2",
    capacity: 4,
    status: "OCCUPIED",
    location: "Food Court",
    area: "Main Area",
    qrCode: "QR-T7-007",
    isActive: true,
    branchId: 2,
    branchName: "Aeon Mall"
  },
  {
    id: 8,
    tableNumber: "T3",
    capacity: 2,
    status: "AVAILABLE",
    location: "Food Court",
    area: "Main Area",
    qrCode: "QR-T8-008",
    isActive: true,
    branchId: 2,
    branchName: "Aeon Mall"
  },

  // Pochentong Airport Branch (Branch ID: 3)
  {
    id: 9,
    tableNumber: "T1",
    capacity: 2,
    status: "AVAILABLE",
    location: "Terminal 1",
    area: "Gate Area",
    qrCode: "QR-T9-009",
    isActive: true,
    branchId: 3,
    branchName: "Pochentong Airport"
  },
  {
    id: 10,
    tableNumber: "T2",
    capacity: 2,
    status: "CLEANING",
    location: "Terminal 1",
    area: "Gate Area",
    qrCode: "QR-T10-010",
    isActive: true,
    branchId: 3,
    branchName: "Pochentong Airport"
  },

  // Riverside Cafe (Branch ID: 4)
  {
    id: 11,
    tableNumber: "T1",
    capacity: 4,
    status: "AVAILABLE",
    location: "Riverside View",
    area: "Outdoor Terrace",
    qrCode: "QR-T11-011",
    isActive: true,
    branchId: 4,
    branchName: "Riverside Cafe"
  },
  {
    id: 12,
    tableNumber: "T2",
    capacity: 6,
    status: "RESERVED",
    location: "Riverside View",
    area: "Outdoor Terrace",
    qrCode: "QR-T12-012",
    isActive: true,
    branchId: 4,
    branchName: "Riverside Cafe"
  },
  {
    id: 13,
    tableNumber: "T3",
    capacity: 2,
    status: "OCCUPIED",
    location: "Indoor Seating",
    area: "AC Room",
    qrCode: "QR-T13-013",
    isActive: true,
    branchId: 4,
    branchName: "Riverside Cafe"
  }
];

export const mockKitchenOrders = [
  {
    id: 1,
    orderNumber: "ORD-001",
    tableNumber: "T2",
    items: [
      { id: 1, name: "Grilled Salmon", quantity: 2, status: "PREPARING", station: "KITCHEN", prepTime: 20, notes: "No lemon" },
      { id: 2, name: "Caesar Salad", quantity: 1, status: "READY", station: "KITCHEN", prepTime: 8, notes: "Extra dressing" }
    ],
    status: "PREPARING",
    orderTime: "10:30 AM",
    elapsedTime: 15,
    priority: "NORMAL",
    preparedBy: "Chef John"
  },
  {
    id: 2,
    orderNumber: "ORD-002",
    tableNumber: "T6",
    items: [
      { id: 3, name: "Spaghetti Carbonara", quantity: 3, status: "PREPARING", station: "KITCHEN", prepTime: 15, notes: "" },
      { id: 4, name: "Buffalo Wings", quantity: 2, status: "PREPARING", station: "KITCHEN", prepTime: 15, notes: "Extra spicy" }
    ],
    status: "PREPARING",
    orderTime: "10:35 AM",
    elapsedTime: 10,
    priority: "URGENT",
    preparedBy: "Chef Maria"
  },
  {
    id: 3,
    orderNumber: "ORD-003",
    tableNumber: "T4",
    items: [
      { id: 5, name: "Beef Steak", quantity: 1, status: "PENDING", station: "KITCHEN", prepTime: 22, notes: "Medium rare" },
      { id: 6, name: "Greek Salad", quantity: 1, status: "READY", station: "KITCHEN", prepTime: 7, notes: "" }
    ],
    status: "PENDING",
    orderTime: "10:40 AM",
    elapsedTime: 5,
    priority: "NORMAL",
    preparedBy: null
  },
  {
    id: 4,
    orderNumber: "ORD-004",
    tableNumber: "T8",
    items: [
      { id: 7, name: "Cappuccino", quantity: 3, status: "READY", station: "BAR", prepTime: 5, notes: "" },
      { id: 8, name: "Chocolate Lava Cake", quantity: 2, status: "READY", station: "KITCHEN", prepTime: 12, notes: "" }
    ],
    status: "READY",
    orderTime: "10:25 AM",
    elapsedTime: 20,
    priority: "NORMAL",
    preparedBy: "Chef Alex"
  },
  {
    id: 5,
    orderNumber: "ORD-005",
    tableNumber: "T1",
    items: [
      { id: 9, name: "Pad Thai", quantity: 2, status: "PREPARING", station: "KITCHEN", prepTime: 12, notes: "" },
      { id: 10, name: "Spring Rolls", quantity: 1, status: "READY", station: "KITCHEN", prepTime: 8, notes: "" }
    ],
    status: "PREPARING",
    orderTime: "10:38 AM",
    elapsedTime: 7,
    priority: "NORMAL",
    preparedBy: "Chef John"
  }
];

// Helper function to get items by category
export const getItemsByCategory = (categoryId) => {
  return mockMenuItems.filter(item => item.categoryId === categoryId);
};

// Helper function to get available items only
export const getAvailableItems = () => {
  return mockMenuItems.filter(item => item.isAvailable);
};

// Helper function to get vegetarian items
export const getVegetarianItems = () => {
  return mockMenuItems.filter(item => item.isVegetarian);
};

// Helper function to get vegan items
export const getVeganItems = () => {
  return mockMenuItems.filter(item => item.isVegan);
};

// Helper function to get items by station
export const getItemsByStation = (station) => {
  return mockMenuItems.filter(item => item.station === station);
};

// ====== BRANCH-SPECIFIC HELPERS ======

// ---------- TABLES ----------

// Get tables by branch ID
export const getTablesByBranch = (branchId) => {
  if (!branchId) return mockTables;
  return mockTables.filter(table => table.branchId === branchId);
};

// Get available tables by branch
export const getAvailableTablesByBranch = (branchId) => {
  const branchTables = getTablesByBranch(branchId);
  return branchTables.filter(table => table.status === "AVAILABLE");
};

// Get table count by branch
export const getTableCountByBranch = (branchId) => {
  return getTablesByBranch(branchId).length;
};

// Get branch table statistics
export const getBranchTableStats = (branchId) => {
  const tables = getTablesByBranch(branchId);
  return {
    total: tables.length,
    available: tables.filter(t => t.status === "AVAILABLE").length,
    occupied: tables.filter(t => t.status === "OCCUPIED").length,
    reserved: tables.filter(t => t.status === "RESERVED").length,
    cleaning: tables.filter(t => t.status === "CLEANING").length,
  };
};

// ---------- MENU CATEGORIES ----------

// Get categories available for a specific branch
export const getCategoriesByBranch = (branchId) => {
  if (!branchId) return mockMenuCategories;

  return mockMenuCategories.filter(category => {
    // If branchIds is empty, available to all branches
    if (!category.branchIds || category.branchIds.length === 0) return true;
    // Otherwise, check if this branch is in the list
    return category.branchIds.includes(branchId);
  });
};

// ---------- MENU ITEMS ----------

// Get menu items available for a specific branch (with branch-specific pricing)
export const getMenuItemsByBranch = (branchId) => {
  if (!branchId) return mockMenuItems.map(item => ({ ...item, price: item.basePrice }));

  return mockMenuItems
    .filter(item => {
      // Check if item is available at this branch
      if (!item.branchPricing || item.branchPricing.length === 0) return true; // Available everywhere
      const branchData = item.branchPricing.find(bp => bp.branchId === branchId);
      return !branchData || branchData.available !== false;
    })
    .map(item => {
      // Apply branch-specific pricing
      const branchData = item.branchPricing?.find(bp => bp.branchId === branchId);
      return {
        ...item,
        price: branchData?.price || item.basePrice
      };
    });
};

// Get items by category for a specific branch
export const getItemsByCategoryAndBranch = (categoryId, branchId) => {
  const branchItems = getMenuItemsByBranch(branchId);
  return branchItems.filter(item => item.categoryId === categoryId);
};

// Check if item is available at specific branch
export const isItemAvailableAtBranch = (itemId, branchId) => {
  const item = mockMenuItems.find(i => i.id === itemId);
  if (!item) return false;
  if (!item.branchPricing || item.branchPricing.length === 0) return true; // Available everywhere
  const branchData = item.branchPricing.find(bp => bp.branchId === branchId);
  return !branchData || branchData.available !== false;
};

// Get item price for specific branch
export const getItemPriceForBranch = (itemId, branchId) => {
  const item = mockMenuItems.find(i => i.id === itemId);
  if (!item) return 0;
  const branchData = item.branchPricing?.find(bp => bp.branchId === branchId);
  return branchData?.price || item.basePrice;
};

// Get branch menu statistics
export const getBranchMenuStats = (branchId) => {
  const items = getMenuItemsByBranch(branchId);
  const categories = getCategoriesByBranch(branchId);

  return {
    totalItems: items.length,
    totalCategories: categories.length,
    vegetarianItems: items.filter(i => i.isVegetarian).length,
    veganItems: items.filter(i => i.isVegan).length,
    avgPrice: items.length > 0
      ? (items.reduce((sum, i) => sum + i.price, 0) / items.length).toFixed(2)
      : 0
  };
};
