import React from "react";
import { MapPin, Phone, Mail } from "lucide-react";
import { Label } from "@/components/ui/label";

const ContactInformation = ({ storeData }) => {
  // Handle both nested contact object and flat structure
  const address = storeData.contact?.address || storeData.address || "No address provided";
  const phone = storeData.contact?.phone || storeData.phone || "No phone provided";
  const email = storeData.contact?.email || storeData.email || "No email provided";

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <MapPin className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <Label className="text-sm text-muted-foreground">Address</Label>
            <p className="text-base mt-1">{address}</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Phone className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <Label className="text-sm text-muted-foreground">Phone</Label>
            <p className="text-base mt-1">{phone}</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Mail className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <Label className="text-sm text-muted-foreground">Email</Label>
            <p className="text-base mt-1">{email}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactInformation; 