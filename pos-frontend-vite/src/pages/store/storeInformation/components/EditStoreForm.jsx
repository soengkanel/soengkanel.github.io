import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Loader2 } from "lucide-react";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StoreValidationSchema, BUSINESS_TYPE_OPTIONS } from "./validation";

const EditStoreForm = ({ initialValues, onSubmit, onCancel, isSubmitting }) => {
  return (
    <Formik
      initialValues={initialValues}
      validationSchema={StoreValidationSchema}
      onSubmit={onSubmit}
      enableReinitialize
    >
      {({ isSubmitting: formikSubmitting, errors, touched, values }) => (
        <Form className="space-y-5">
          {/* Basic Information */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-muted-foreground">Basic Information</h4>

            <div className="space-y-2">
              <Label htmlFor="brand" className="text-sm">Store Name *</Label>
              <Field
                as={Input}
                id="brand"
                name="brand"
                placeholder="Enter store name"
                className={errors.brand && touched.brand ? "border-red-500" : ""}
              />
              <ErrorMessage name="brand" component="div" className="text-red-500 text-xs" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="businessType" className="text-sm">Business Type *</Label>
              <Field name="businessType">
                {({ field, form }) => (
                  <Select
                    value={field.value}
                    onValueChange={(value) => form.setFieldValue(field.name, value)}
                  >
                    <SelectTrigger
                      className={`w-full ${
                        errors.businessType && touched.businessType ? "border-red-500" : ""
                      }`}
                    >
                      <SelectValue placeholder="Select business type" />
                    </SelectTrigger>
                    <SelectContent>
                      {BUSINESS_TYPE_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </Field>
              <ErrorMessage name="businessType" component="div" className="text-red-500 text-xs" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description" className="text-sm">Description</Label>
              <Field
                as={Textarea}
                id="description"
                name="description"
                placeholder="Enter store description"
                rows={3}
                className={errors.description && touched.description ? "border-red-500" : ""}
              />
              <ErrorMessage name="description" component="div" className="text-red-500 text-xs" />
            </div>
          </div>

          <Separator />

          {/* Contact Information */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-muted-foreground">Contact Information</h4>

            <div className="space-y-2">
              <Label htmlFor="contact.address" className="text-sm">Address *</Label>
              <Field
                as={Textarea}
                id="contact.address"
                name="contact.address"
                placeholder="Enter store address"
                rows={2}
                className={errors.contact?.address && touched.contact?.address ? "border-red-500" : ""}
              />
              <ErrorMessage name="contact.address" component="div" className="text-red-500 text-xs" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contact.phone" className="text-sm">Phone Number *</Label>
                <Field
                  as={Input}
                  id="contact.phone"
                  name="contact.phone"
                  placeholder="+855 12 345 678"
                  className={errors.contact?.phone && touched.contact?.phone ? "border-red-500" : ""}
                />
                <ErrorMessage name="contact.phone" component="div" className="text-red-500 text-xs" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contact.email" className="text-sm">Email Address *</Label>
                <Field
                  as={Input}
                  id="contact.email"
                  name="contact.email"
                  type="email"
                  placeholder="store@example.com"
                  className={errors.contact?.email && touched.contact?.email ? "border-red-500" : ""}
                />
                <ErrorMessage name="contact.email" component="div" className="text-red-500 text-xs" />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-2 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={formikSubmitting || isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={formikSubmitting || isSubmitting}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              {formikSubmitting || isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                "Update Store"
              )}
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default EditStoreForm; 