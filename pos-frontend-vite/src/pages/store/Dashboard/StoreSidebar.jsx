import React, { useMemo } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { useDispatch, useSelector } from "react-redux";
import { logout } from "../../../Redux Toolkit/features/user/userThunks";
import {
  LayoutDashboard,
  Store,
  Users,
  ShoppingCart,
  BarChart2,
  Settings,
  FileText,
  Tag,
  Truck,
  UtensilsCrossed,
  Coffee,
  ChefHat,
  TableProperties,
  ClipboardList,
  QrCode,
} from "lucide-react";
import { Button } from "../../../components/ui/button";
import { BadgeDollarSign } from "lucide-react";

// Common menu items for all business types
const commonNavLinks = [
  {
    name: "Dashboard",
    path: "/store/dashboard",
    icon: <LayoutDashboard className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
  {
    name: "Stores",
    path: "/store/stores",
    icon: <Store className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
  {
    name: "Branches",
    path: "/store/branches",
    icon: <Store className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
  {
    name: "Employees",
    path: "/store/employees",
    icon: <Users className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
];

// Retail-specific menu items
const retailNavLinks = [
  {
    name: "Products",
    path: "/store/products",
    icon: <ShoppingCart className="w-5 h-5" />,
    businessTypes: ["RETAIL", "HYBRID"],
  },
  {
    name: "Categories",
    path: "/store/categories",
    icon: <Tag className="w-5 h-5" />,
    businessTypes: ["RETAIL", "HYBRID"],
  },
  {
    name: "Inventory Alerts",
    path: "/store/alerts",
    icon: <Truck className="w-5 h-5" />,
    businessTypes: ["RETAIL", "HYBRID"],
  },
];

// F&B-specific menu items
const fnbNavLinks = [
  {
    name: "Menu Items",
    path: "/store/menu-items",
    icon: <UtensilsCrossed className="w-5 h-5" />,
    businessTypes: ["FNB", "HYBRID"],
  },
  {
    name: "Menu Categories",
    path: "/store/menu-categories",
    icon: <Coffee className="w-5 h-5" />,
    businessTypes: ["FNB", "HYBRID"],
  },
  {
    name: "eMenu",
    path: "/store/emenu",
    icon: <QrCode className="w-5 h-5" />,
    businessTypes: ["FNB", "HYBRID"],
  },
  {
    name: "Tables",
    path: "/store/tables",
    icon: <TableProperties className="w-5 h-5" />,
    businessTypes: ["FNB", "HYBRID"],
  },
  {
    name: "Kitchen Orders",
    path: "/store/kitchen-orders",
    icon: <ChefHat className="w-5 h-5" />,
    businessTypes: ["FNB", "HYBRID"],
  },
];

// Bottom menu items (same for all)
const bottomNavLinks = [
  {
    name: "Sales",
    path: "/store/sales",
    icon: <BarChart2 className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
  {
    name: "Reports",
    path: "/store/reports",
    icon: <FileText className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
  {
    name: "Upgrade Plan",
    path: "/store/upgrade",
    icon: <BadgeDollarSign className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
  {
    name: "Settings",
    path: "/store/settings",
    icon: <Settings className="w-5 h-5" />,
    businessTypes: ["RETAIL", "FNB", "HYBRID"],
  },
];

export default function StoreSidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);

  // Get business type from store, default to RETAIL if not set
  const businessType = store?.businessType || "RETAIL";

  // Filter navigation links based on business type
  const navLinks = useMemo(() => {
    const filteredLinks = [
      ...commonNavLinks,
      ...retailNavLinks.filter((link) =>
        link.businessTypes.includes(businessType)
      ),
      ...fnbNavLinks.filter((link) =>
        link.businessTypes.includes(businessType)
      ),
      ...bottomNavLinks,
    ];

    return filteredLinks.filter((link) =>
      link.businessTypes.includes(businessType)
    );
  }, [businessType]);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/auth/login");
  };

  // Helper function to get business type badge
  const getBusinessTypeBadge = () => {
    const badges = {
      RETAIL: { label: "Retail", color: "bg-blue-500/10 text-blue-600 dark:text-blue-400", icon: <ShoppingCart className="w-3 h-3" /> },
      FNB: { label: "F&B", color: "bg-orange-500/10 text-orange-600 dark:text-orange-400", icon: <UtensilsCrossed className="w-3 h-3" /> },
      HYBRID: { label: "Hybrid", color: "bg-purple-500/10 text-purple-600 dark:text-purple-400", icon: <Store className="w-3 h-3" /> },
    };
    return badges[businessType] || badges.RETAIL;
  };

  const badge = getBusinessTypeBadge();

  return (
    <aside className="h-screen w-56 bg-background border-r border-border flex flex-col py-4 px-3">
      {/* Compact Header */}
      <div className="mb-4 px-2">
        <div className="text-lg font-bold text-foreground flex items-center gap-2 mb-2">
          <Store className="w-5 h-5" />
          POS
        </div>
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md ${badge.color} text-xs font-medium w-fit`}>
          {badge.icon}
          {badge.label}
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto scrollbar-thin">
        <ul className="space-y-0.5">
          {/* Common Links */}
          {commonNavLinks
            .filter((link) => link.businessTypes.includes(businessType))
            .map((link) => (
              <li key={link.name}>
                <Link
                  to={link.path}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-sm font-medium ${
                    location.pathname.startsWith(link.path)
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  {React.cloneElement(link.icon, { className: "w-4 h-4" })}
                  {link.name}
                </Link>
              </li>
            ))}

          {/* Retail Section */}
          {(businessType === "RETAIL" || businessType === "HYBRID") && retailNavLinks.length > 0 && (
            <>
              <li className="pt-3 pb-1 px-2">
                <div className="text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider">
                  Retail
                </div>
              </li>
              {retailNavLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-sm font-medium ${
                      location.pathname.startsWith(link.path)
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-accent hover:text-foreground"
                    }`}
                  >
                    {React.cloneElement(link.icon, { className: "w-4 h-4" })}
                    {link.name}
                  </Link>
                </li>
              ))}
            </>
          )}

          {/* F&B Section */}
          {(businessType === "FNB" || businessType === "HYBRID") && fnbNavLinks.length > 0 && (
            <>
              <li className="pt-3 pb-1 px-2">
                <div className="text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider">
                  F&B
                </div>
              </li>
              {fnbNavLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-sm font-medium ${
                      location.pathname.startsWith(link.path)
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-accent hover:text-foreground"
                    }`}
                  >
                    {React.cloneElement(link.icon, { className: "w-4 h-4" })}
                    {link.name}
                  </Link>
                </li>
              ))}
            </>
          )}

          {/* Bottom Links */}
          <li className="pt-3 pb-1">
            <div className="border-t border-border"></div>
          </li>
          {bottomNavLinks.map((link) => (
            <li key={link.name}>
              <Link
                to={link.path}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-sm font-medium ${
                  location.pathname.startsWith(link.path)
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                {React.cloneElement(link.icon, { className: "w-4 h-4" })}
                {link.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="mt-auto pt-3 border-t border-border">
        <Button
          onClick={handleLogout}
          variant="ghost"
          size="sm"
          className="w-full justify-start text-sm font-medium"
        >
          Logout
        </Button>
      </div>
    </aside>
  );
}
