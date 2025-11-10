import React, { useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getAllBranchesByStore } from "@/Redux Toolkit/features/branch/branchThunks";
import { useFormik } from "formik";
import * as Yup from "yup";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

const EmployeeForm = ({ initialData, onSubmit, roles }) => {
  const dispatch = useDispatch();
  const { branches } = useSelector((state) => state.branch);
  const { store } = useSelector((state) => state.store);

  useEffect(() => {
    dispatch(
      getAllBranchesByStore({
        storeId: store?.id,
        jwt: localStorage.getItem("jwt"),
      })
    );
  }, [dispatch, store?.id]);

  // Dynamic validation schema based on whether we're editing or adding
  const validationSchema = useMemo(() => {
    return Yup.object({
      fullName: Yup.string().required("Employee name is required"),
      email: Yup.string()
        .email("Invalid email address")
        .required("Email is required"),
      phone: Yup.string().required("Phone number is required"),
      role: Yup.string().required("Role is required"),
      branchId: Yup.string().notRequired(), // Branch assignment is optional for all roles
      password: initialData
        ? Yup.string().notRequired() // Password is optional when editing
        : Yup.string()
            .min(8, "Password must be at least 8 characters")
            .required("Password is required"),
    });
  }, [initialData]);


  const formik = useFormik({
    initialValues: {
      fullName: initialData?.fullName || "",
      email: initialData?.email || "",
      password: initialData?.password || "",
      phone: initialData?.phone || "",
      role: initialData?.role || "",
      branchId: initialData?.branchId ? String(initialData.branchId) : "none",
    },
    validationSchema: validationSchema,
    enableReinitialize: true, // This allows the form to reinitialize when initialData changes
    onSubmit: (values) => {
      // Remove password from values if it's empty (for edit mode)
      const submitValues = { ...values };
      if (initialData && !submitValues.password) {
        delete submitValues.password;
      }
      // Convert "none" back to null/empty for branchId
      if (submitValues.branchId === "none") {
        submitValues.branchId = null;
      }
      onSubmit(submitValues);
    },
  });

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-4 py-2 pr-2">
      <div className="space-y-2">
        <Label htmlFor="fullName">Full Name</Label>
        <Input
          id="fullName"
          name="fullName"
          value={formik.values.fullName || ""}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          placeholder="Enter employee name"
        />
        {formik.touched.fullName && formik.errors.fullName ? (
          <div className="text-red-500 text-sm">{formik.errors.fullName}</div>
        ) : null}
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          value={formik.values.email || ""}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          placeholder="Enter email address"
        />
        {formik.touched.email && formik.errors.email ? (
          <div className="text-red-500 text-sm">{formik.errors.email}</div>
        ) : null}
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">
          Password {initialData && <span className="text-muted-foreground text-xs">(Leave empty to keep current)</span>}
        </Label>
        <Input
          id="password"
          name="password"
          type="password"
          value={formik.values.password || ""}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          placeholder={initialData ? "Leave empty to keep current password" : "Enter password"}
        />
        {formik.touched.password && formik.errors.password ? (
          <div className="text-red-500 text-sm">{formik.errors.password}</div>
        ) : null}
      </div>
      <div className="space-y-2">
        <Label htmlFor="phone">Phone</Label>
        <Input
          id="phone"
          name="phone"
          value={formik.values.phone || ""}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          placeholder="Enter phone number"
        />
        {formik.touched.phone && formik.errors.phone ? (
          <div className="text-red-500 text-sm">{formik.errors.phone}</div>
        ) : null}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="role">Role</Label>
          <Select
            value={formik.values.role || ""}
            onValueChange={(value) => formik.setFieldValue("role", value)}
            onOpenChange={() => formik.setFieldTouched("role", true)}
            className="w-full"
          >
            <SelectTrigger>
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent>
              {roles && roles.length > 0 ? (
                roles.map((role) => (
                  <SelectItem key={role} value={role}>
                    {role}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="no-roles" disabled>No roles available</SelectItem>
              )}
            </SelectContent>
          </Select>
          {formik.touched.role && formik.errors.role ? (
            <div className="text-red-500 text-sm">{formik.errors.role}</div>
          ) : null}
        </div>
        <div className="space-y-2">
          <Label htmlFor="branchId">Branch (Optional)</Label>
          <Select
            value={formik.values.branchId && formik.values.branchId !== "none" ? String(formik.values.branchId) : "none"}
            onValueChange={(value) => formik.setFieldValue("branchId", value)}
            onOpenChange={() => formik.setFieldTouched("branchId", true)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select branch" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">No Branch Assignment</SelectItem>
              {branches && branches.length > 0 ? (
                branches.map((branch) => (
                  <SelectItem key={branch.id} value={String(branch.id)}>
                    {branch.name}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="no-branches" disabled>No branches available</SelectItem>
              )}
            </SelectContent>
          </Select>
          {formik.touched.branchId && formik.errors.branchId ? (
            <div className="text-red-500 text-sm">{formik.errors.branchId}</div>
          ) : null}
        </div>
      </div>
      <div className="flex justify-end pt-4">
        <Button type="submit" className="">
          {initialData ? "Save Changes" : "Add Employee"}
        </Button>
      </div>
    </form>
  );
};

export default EmployeeForm;
