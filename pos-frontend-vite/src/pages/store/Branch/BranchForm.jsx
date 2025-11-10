import React, { useEffect, useMemo } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { useDispatch, useSelector } from "react-redux";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";
import { createBranch, updateBranch } from "@/Redux Toolkit/features/branch/branchThunks";
import { findStoreEmployees } from "@/Redux Toolkit/features/employee/employeeThunks";
import { mockEmployees, getEmployeesByRole } from "@/data/mockEmployees";

const BranchForm = ({ initialValues, onSubmit, onCancel, isEditing }) => {
  const dispatch = useDispatch();
  const { loading } = useSelector((state) => state.branch);
  const { store } = useSelector((state) => state.store);
  const { employees: reduxEmployees } = useSelector((state) => state.employee);

  // Fetch employees when component mounts
  useEffect(() => {
    const jwt = localStorage.getItem("jwt");
    if (store?.id && jwt) {
      dispatch(findStoreEmployees({ storeId: store.id, jwt }));
    }
  }, [dispatch, store?.id]);

  // Get branch managers - use Redux data if available, otherwise use mock data
  const branchManagers = useMemo(() => {
    const employees = reduxEmployees && reduxEmployees.length > 0
      ? reduxEmployees
      : mockEmployees;

    // Filter for branch managers only
    return employees.filter(emp =>
      emp.role === "ROLE_BRANCH_MANAGER" || emp.role === "ROLE_STORE_MANAGER"
    );
  }, [reduxEmployees]);

  const validationSchema = Yup.object({
    name: Yup.string().required("Branch Name is required"),
    address: Yup.string().required("Address is required"),
    managerId: Yup.number().required("Manager is required"),
    phone: Yup.string().required("Phone Number is required"),
  });

  // Get businessType from store - this is NOT user-editable
  // Store uses 'businessType' field
  const storeBusinessType = store?.businessType || "RETAIL";

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      const jwt = localStorage.getItem("jwt");
      if (!store?.id) {
        toast({
          title: "Error",
          description: "Store information or authentication JWT missing!",
          variant: "destructive",
        });
        setSubmitting(false);
        return;
      }

      const branchData = {
        ...values,
        storeId: store.id,
        businessType: storeBusinessType, // Automatically set from store
      };

      console.log("📤 Sending branch data to backend:", branchData);

      if (isEditing) {
        const result = await dispatch(updateBranch({ id: initialValues.id, dto: branchData, jwt })).unwrap();
        console.log("📥 Backend returned updated branch:", result);
        toast({ title: "Success", description: "Branch updated successfully" });
      } else {
        const result = await dispatch(createBranch({ dto: branchData, jwt })).unwrap();
        console.log("📥 Backend returned created branch:", result);
        toast({ title: "Success", description: "Branch created successfully" });
      }
      onSubmit();
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || `Failed to ${isEditing ? "update" : "create"} branch`,
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Helper to get business type label
  const getBusinessTypeLabel = (type) => {
    const labels = {
      FNB: "Food & Beverage (Tables, Menu, Kitchen)",
      RETAIL: "Retail (Inventory, Products)",
      HYBRID: "Hybrid (F&B + Retail)"
    };
    return labels[type] || type;
  };

  return (
    <Formik
      initialValues={initialValues || { name: "", address: "", managerId: "", phone: "" }}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      enableReinitialize
    >
      {({ isSubmitting, values, setFieldValue }) => (
        <Form className="space-y-4 py-2 pr-2">
          {/* Business Type Info (Read-only) */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm font-semibold text-blue-900 mb-1">Business Type (Inherited from Store)</p>
            <p className="text-sm text-blue-700">{getBusinessTypeLabel(storeBusinessType)}</p>
            <p className="text-xs text-blue-600 mt-1">All branches automatically inherit the business type from the store.</p>
          </div>

          <div className="space-y-2">
            <label htmlFor="name">Branch Name</label>
            <Field
              as={Input}
              id="name"
              name="name"
              placeholder="Enter branch name"
            />
            <ErrorMessage name="name" component="div" className="text-red-500 text-sm" />
          </div>

          <div className="space-y-2">
            <label htmlFor="address">Address</label>
            <Field
              as={Input}
              id="address"
              name="address"
              placeholder="Enter branch address"
            />
            <ErrorMessage name="address" component="div" className="text-red-500 text-sm" />
          </div>

          <div className="space-y-2">
            <label htmlFor="managerId">Branch Manager</label>
            <Select
              value={values.managerId?.toString()}
              onValueChange={(value) => setFieldValue("managerId", parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a branch manager" />
              </SelectTrigger>
              <SelectContent>
                {branchManagers.length === 0 ? (
                  <div className="px-2 py-6 text-center text-sm text-muted-foreground">
                    No managers available
                  </div>
                ) : (
                  branchManagers.map((manager) => (
                    <SelectItem key={manager.id} value={manager.id.toString()}>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{manager.fullName}</span>
                        <span className="text-xs text-muted-foreground">
                          ({manager.role === "ROLE_STORE_MANAGER" ? "Store Manager" : "Branch Manager"})
                        </span>
                      </div>
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            <ErrorMessage name="managerId" component="div" className="text-red-500 text-sm" />
          </div>

          <div className="space-y-2">
            <label htmlFor="phone">Phone Number</label>
            <Field
              as={Input}
              id="phone"
              name="phone"
              placeholder="Enter phone number"
            />
            <ErrorMessage name="phone" component="div" className="text-red-500 text-sm" />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || loading}>
              {isSubmitting || loading ? (isEditing ? "Updating..." : "Adding...") : (isEditing ? "Update Branch" : "Add Branch")}
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default BranchForm;