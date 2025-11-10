import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getStoreByAdmin } from "@/Redux Toolkit/features/store/storeThunks";
import { toast } from "@/components/ui/use-toast";
import { Store, Bell, Shield, CreditCard, Settings as SettingsIcon } from "lucide-react";
import {
  SettingsHeader,
  SettingsContent
} from "./components";

export default function Settings() {
  const dispatch = useDispatch();
  const { store} = useSelector((state) => state.store);
  // Sample store settings data - in a real app, this would come from Redux
  const [storeSettings, setStoreSettings] = useState({
    storeName: "My POS Store",
    storeEmail: "contact@myposstore.com",
    storePhone: "(555) 123-4567",
    storeAddress: "123 Main St, Anytown, USA 12345",
    storeLogo: "/logo.png",
    storeDescription: "A modern point of sale system for retail businesses.",
    currency: "KHR",
    taxRate: "7.5",
    timezone: "America/New_York",
    dateFormat: "MM/DD/YYYY",
    receiptFooter: "Thank you for shopping with us!",
  });

  // Sample notification settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    lowStockAlerts: true,
    salesReports: true,
    employeeActivity: true,
  });

  // Sample security settings
  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    passwordExpiry: "90",
    sessionTimeout: "30",
    ipRestriction: false,
  });

  // Sample payment settings
  const [paymentSettings, setPaymentSettings] = useState({
    acceptCash: true,
    acceptCredit: true,
    acceptDebit: true,
    acceptMobile: true,
    stripeEnabled: false,
    paypalEnabled: false,
  });

  const [activeTab, setActiveTab] = useState("store-settings");

  const tabs = [
    { id: "store-settings", label: "Store", icon: Store },
    { id: "notification-settings", label: "Notifications", icon: Bell },
    { id: "security-settings", label: "Security", icon: Shield },
    { id: "payment-settings", label: "Payments", icon: CreditCard },
  ];

  // Fetch store data on component mount
  useEffect(() => {
    const fetchStoreData = async () => {
      try {
        await dispatch(getStoreByAdmin()).unwrap();
      } catch (err) {
        toast({
          title: "Error",
          description: err || "Failed to fetch store data",
          variant: "destructive",
        });
      }
    };

    fetchStoreData();
  }, [dispatch]);

  // Update store settings when store data is loaded
  useEffect(() => {
    if (store) {
      setStoreSettings({
        storeName: store.brand || "",
        storeEmail: store.contact?.email || "",
        storePhone: store.contact?.phone || "",
        storeAddress: store.contact?.address || "",
        storeDescription: store.description || "",
        currency: store.currency || "KHR",
        taxRate: store.taxRate?.toString() || "0",
        timezone: store.timezone || "America/New_York",
        dateFormat: store.dateFormat || "MM/DD/YYYY",
        receiptFooter: store.receiptFooter || "",
      });
    }
  }, [store]);

  const handleStoreSettingsChange = (name, value) => {
    setStoreSettings({
      ...storeSettings,
      [name]: value,
    });
  };

  const handleNotificationSettingsChange = (name, value) => {
    setNotificationSettings({
      ...notificationSettings,
      [name]: value,
    });
  };

  const handleSecuritySettingsChange = (name, value) => {
    setSecuritySettings({
      ...securitySettings,
      [name]: value,
    });
  };

  const handlePaymentSettingsChange = (name, value) => {
    setPaymentSettings({
      ...paymentSettings,
      [name]: value,
    });
  };



  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <SettingsIcon className="w-5 h-5 text-primary" />
        <h1 className="text-lg font-bold text-gray-900">Settings</h1>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-4" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                  ${isActive
                    ? 'border-primary text-primary bg-primary/5'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white border rounded-lg">
        <SettingsContent
          activeSection={activeTab}
          storeSettings={storeSettings}
          notificationSettings={notificationSettings}
          securitySettings={securitySettings}
          paymentSettings={paymentSettings}
          onStoreSettingsChange={handleStoreSettingsChange}
          onNotificationSettingsChange={handleNotificationSettingsChange}
          onSecuritySettingsChange={handleSecuritySettingsChange}
          onPaymentSettingsChange={handlePaymentSettingsChange}
        />
      </div>
    </div>
  );
}