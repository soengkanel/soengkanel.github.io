import React from "react";
import StoreSettings from "./StoreSettings";
import NotificationSettings from "./NotificationSettings";
import SecuritySettings from "./SecuritySettings";
import PaymentSettings from "./PaymentSettings";
import { Save } from "lucide-react";
import { Button } from "../../../../components/ui/button";

const SettingsContent = ({
  activeSection,
  storeSettings,
  notificationSettings,
  securitySettings,
  paymentSettings,
  onStoreSettingsChange,
  onNotificationSettingsChange,
  onSecuritySettingsChange,
  onPaymentSettingsChange,
}) => {
  const onSave = () => {
    console.log("on save");
    // Save all settings to the server
  };

  const renderContent = () => {
    switch (activeSection) {
      case "store-settings":
        return (
          <StoreSettings
            settings={storeSettings}
            onChange={onStoreSettingsChange}
          />
        );
      case "notification-settings":
        return (
          <NotificationSettings
            settings={notificationSettings}
            onChange={onNotificationSettingsChange}
          />
        );
      case "security-settings":
        return (
          <SecuritySettings
            settings={securitySettings}
            onChange={onSecuritySettingsChange}
          />
        );
      case "payment-settings":
        return (
          <PaymentSettings
            settings={paymentSettings}
            onChange={onPaymentSettingsChange}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {renderContent()}

      <div className="flex justify-end pt-4 border-t">
        <Button onClick={onSave}>
          <Save className="mr-2 h-4 w-4" /> Save Changes
        </Button>
      </div>
    </div>
  );
};

export default SettingsContent;
