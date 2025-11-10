import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import EditStoreForm from "./EditStoreForm";

const EditStoreDialog = ({
  open,
  onOpenChange,
  initialValues,
  onSubmit,
  isSubmitting
}) => {
  const handleCancel = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[650px] max-h-[85vh] p-0 gap-0">
        <DialogHeader className="px-6 pt-6 pb-4">
          <DialogTitle>Edit Store Details</DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(85vh-80px)] px-6 pb-6">
          <EditStoreForm
            initialValues={initialValues}
            onSubmit={onSubmit}
            onCancel={handleCancel}
            isSubmitting={isSubmitting}
          />
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

export default EditStoreDialog; 