import React, { useEffect } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useDispatch, useSelector } from 'react-redux';
import { getAllBranchesByStore } from '@/Redux Toolkit/features/branch/branchThunks';
import { toast } from '@/components/ui/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { TableProperties, Users, MapPin, Building2 } from 'lucide-react';

const validationSchema = Yup.object({
  tableNumber: Yup.string().required('Table number is required'),
  capacity: Yup.number()
    .required('Capacity is required')
    .min(1, 'Capacity must be at least 1')
    .max(50, 'Capacity cannot exceed 50'),
  branchId: Yup.number().required('Branch is required'),
  location: Yup.string().required('Location is required'),
  area: Yup.string().optional(),
  status: Yup.string().required('Status is required'),
  qrCode: Yup.string().optional(),
  notes: Yup.string().optional(),
});

const TableFormModal = ({ open, onClose, table, onSubmit }) => {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { branches } = useSelector((state) => state.branch);

  // Fetch branches when component mounts
  useEffect(() => {
    if (store?.id && open) {
      dispatch(getAllBranchesByStore({
        storeId: store.id,
        jwt: localStorage.getItem('jwt'),
      }));
    }
  }, [dispatch, store?.id, open]);

  const defaultValues = {
    tableNumber: '',
    capacity: 4,
    branchId: '',
    location: '',
    area: '',
    status: 'AVAILABLE',
    qrCode: '',
    notes: '',
    isActive: true,
    ...table
  };

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      // TODO: Replace with actual API call
      // const token = localStorage.getItem('jwt');
      // if (table?.id) {
      //   await dispatch(updateTable({ id: table.id, dto: values, token })).unwrap();
      // } else {
      //   await dispatch(createTable({ dto: values, token })).unwrap();
      // }

      console.log('Table form submitted:', values);

      toast({
        title: 'Success',
        description: `Table ${table?.id ? 'updated' : 'added'} successfully`
      });

      resetForm();
      if (onSubmit) onSubmit(values);
      onClose();
    } catch (err) {
      toast({
        title: 'Error',
        description: err || `Failed to ${table?.id ? 'update' : 'add'} table`,
        variant: 'destructive'
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <TableProperties className="w-5 h-5 text-primary" />
            {table?.id ? 'Edit Table' : 'Add New Table'}
          </DialogTitle>
        </DialogHeader>

        <Formik
          initialValues={defaultValues}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
          enableReinitialize
        >
          {({ isSubmitting, touched, errors, values, setFieldValue }) => (
            <Form className="space-y-6 py-2">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Table Number */}
                <div className="space-y-2">
                  <Label htmlFor="tableNumber" className="flex items-center gap-2">
                    <TableProperties className="w-4 h-4 text-primary" />
                    Table Number *
                  </Label>
                  <Field
                    as={Input}
                    id="tableNumber"
                    name="tableNumber"
                    placeholder="e.g., T1, Table-01"
                    className={touched.tableNumber && errors.tableNumber ? 'border-red-300' : ''}
                  />
                  <ErrorMessage name="tableNumber" component="div" className="text-red-500 text-sm" />
                </div>

                {/* Capacity */}
                <div className="space-y-2">
                  <Label htmlFor="capacity" className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-primary" />
                    Capacity (seats) *
                  </Label>
                  <Field
                    as={Input}
                    id="capacity"
                    name="capacity"
                    type="number"
                    min="1"
                    max="50"
                    placeholder="4"
                    className={touched.capacity && errors.capacity ? 'border-red-300' : ''}
                  />
                  <ErrorMessage name="capacity" component="div" className="text-red-500 text-sm" />
                </div>

                {/* Branch */}
                <div className="space-y-2">
                  <Label htmlFor="branchId" className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-primary" />
                    Branch *
                  </Label>
                  <Field
                    as="select"
                    id="branchId"
                    name="branchId"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
                      touched.branchId && errors.branchId ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select a branch</option>
                    {branches && branches.length > 0 ? (
                      branches.map((branch) => (
                        <option key={branch.id} value={branch.id}>
                          {branch.name}
                        </option>
                      ))
                    ) : (
                      <option disabled>No branches available</option>
                    )}
                  </Field>
                  <ErrorMessage name="branchId" component="div" className="text-red-500 text-sm" />
                </div>

                {/* Status */}
                <div className="space-y-2">
                  <Label htmlFor="status">Status *</Label>
                  <Field
                    as="select"
                    id="status"
                    name="status"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
                      touched.status && errors.status ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="AVAILABLE">Available</option>
                    <option value="OCCUPIED">Occupied</option>
                    <option value="RESERVED">Reserved</option>
                    <option value="CLEANING">Cleaning</option>
                  </Field>
                  <ErrorMessage name="status" component="div" className="text-red-500 text-sm" />
                </div>

                {/* Location */}
                <div className="space-y-2">
                  <Label htmlFor="location" className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-primary" />
                    Location *
                  </Label>
                  <Field
                    as={Input}
                    id="location"
                    name="location"
                    placeholder="e.g., Main Dining, Patio"
                    className={touched.location && errors.location ? 'border-red-300' : ''}
                  />
                  <ErrorMessage name="location" component="div" className="text-red-500 text-sm" />
                </div>

                {/* Area */}
                <div className="space-y-2">
                  <Label htmlFor="area">Area</Label>
                  <Field
                    as={Input}
                    id="area"
                    name="area"
                    placeholder="e.g., VIP, Outdoor"
                  />
                </div>
              </div>

              {/* QR Code */}
              <div className="space-y-2">
                <Label htmlFor="qrCode">QR Code (Optional)</Label>
                <Field
                  as={Input}
                  id="qrCode"
                  name="qrCode"
                  placeholder="e.g., QR-T1-001"
                />
                <p className="text-xs text-gray-500">Used for customer self-ordering via QR scan</p>
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label htmlFor="notes">Notes (Optional)</Label>
                <Field
                  as="textarea"
                  id="notes"
                  name="notes"
                  rows={3}
                  placeholder="Any special notes about this table..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Active Status */}
              <div className="flex items-center gap-2">
                <Field
                  type="checkbox"
                  id="isActive"
                  name="isActive"
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <Label htmlFor="isActive" className="cursor-pointer">
                  Table is active and visible to staff
                </Label>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="bg-emerald-600 hover:bg-emerald-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {table?.id ? 'Updating...' : 'Adding...'}
                    </span>
                  ) : (
                    table?.id ? 'Update Table' : 'Add Table'
                  )}
                </Button>
              </div>
            </Form>
          )}
        </Formik>
      </DialogContent>
    </Dialog>
  );
};

export default TableFormModal;
