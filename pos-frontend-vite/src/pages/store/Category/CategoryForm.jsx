import React, { useEffect } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { useDispatch, useSelector } from 'react-redux';
import { createCategory, updateCategory } from '@/Redux Toolkit/features/category/categoryThunks';
import { getAllBranchesByStore } from '@/Redux Toolkit/features/branch/branchThunks';
import { toast } from '@/components/ui/use-toast';
import { Building2, Info } from 'lucide-react';

const validationSchema = Yup.object({
  name: Yup.string().required('Category name is required'),
  description: Yup.string().optional(),
  branchIds: Yup.array().optional(),
});

const CategoryForm = ({ initialValues, onSubmit, onCancel, isEditing = false }) => {
  const dispatch = useDispatch();
  const { loading } = useSelector((state) => state.category);
  const { store } = useSelector((state) => state.store);
  const { branches } = useSelector((state) => state.branch);

  // Fetch branches when component mounts
  useEffect(() => {
    if (store?.id) {
      dispatch(getAllBranchesByStore({
        storeId: store.id,
        jwt: localStorage.getItem('jwt'),
      }));
    }
  }, [dispatch, store?.id]);

  const defaultValues = {
    name: '',
    description: '',
    branchIds: [], // Empty array means available at all branches
    ...initialValues
  };

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      const token = localStorage.getItem('jwt');
      const dto = {
        ...values,
        storeId: store.id,
      };

      if (isEditing && initialValues?.id) {
        await dispatch(updateCategory({ id: initialValues.id, dto, token })).unwrap();
        toast({ title: 'Success', description: 'Category updated successfully' });
      } else {
        await dispatch(createCategory({ dto, token })).unwrap();
        toast({ title: 'Success', description: 'Category added successfully' });
        resetForm();
      }

      if (onSubmit) onSubmit();
    } catch (err) {
      toast({ 
        title: 'Error', 
        description: err || `Failed to ${isEditing ? 'update' : 'add'} category`, 
        variant: 'destructive' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={defaultValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      enableReinitialize
    >
      {({ isSubmitting, touched, errors, values, setFieldValue }) => (
        <Form className="space-y-4 py-2 pr-2">
          <div className="space-y-2">
            <label htmlFor="name" className="block text-sm font-medium">Category Name</label>
            <Field
              as={Input}
              id="name"
              name="name"
              placeholder="Enter category name"
              className={touched.name && errors.name ? 'border-red-300' : ''}
            />
            <ErrorMessage name="name" component="div" className="text-red-500 text-sm" />
          </div>

          <div className="space-y-2">
            <label htmlFor="description" className="block text-sm font-medium">Description</label>
            <Field
              as={Textarea}
              id="description"
              name="description"
              placeholder="Enter category description"
              rows={3}
            />
            <ErrorMessage name="description" component="div" className="text-red-500 text-sm" />
          </div>

          {/* Branch Availability Section */}
          <div className="space-y-3 border-t pt-4">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Building2 className="w-4 h-4 text-primary" />
              <span>Branch Availability</span>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <p className="text-xs text-blue-900">
                Leave unchecked to make this category available at all branches. Select specific branches to restrict availability.
              </p>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto p-2 border rounded-lg bg-gray-50">
              <div className="flex items-center space-x-2 p-2 bg-white rounded border">
                <Checkbox
                  id="all-branches"
                  checked={!values.branchIds || values.branchIds.length === 0}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setFieldValue('branchIds', []);
                    }
                  }}
                />
                <Label
                  htmlFor="all-branches"
                  className="text-sm font-semibold cursor-pointer flex-1"
                >
                  All Branches (Default)
                </Label>
              </div>

              {branches && branches.length > 0 ? (
                branches.map((branch) => {
                  const isChecked = values.branchIds && values.branchIds.includes(branch.id);
                  return (
                    <div key={branch.id} className="flex items-center space-x-2 p-2 hover:bg-white rounded">
                      <Checkbox
                        id={`branch-${branch.id}`}
                        checked={isChecked}
                        onCheckedChange={(checked) => {
                          const currentBranchIds = values.branchIds || [];
                          if (checked) {
                            setFieldValue('branchIds', [...currentBranchIds, branch.id]);
                          } else {
                            setFieldValue('branchIds', currentBranchIds.filter(id => id !== branch.id));
                          }
                        }}
                      />
                      <Label
                        htmlFor={`branch-${branch.id}`}
                        className="text-sm cursor-pointer flex-1"
                      >
                        <div className="flex items-center justify-between">
                          <span>{branch.name}</span>
                          <span className="text-xs text-gray-500">{branch.location || branch.address}</span>
                        </div>
                      </Label>
                    </div>
                  );
                })
              ) : (
                <div className="text-sm text-gray-500 text-center py-4">
                  No branches available. Category will be available at all branches.
                </div>
              )}
            </div>

            {values.branchIds && values.branchIds.length > 0 && (
              <div className="text-xs text-gray-600 bg-yellow-50 border border-yellow-200 rounded p-2">
                <strong>Note:</strong> This category will only be available at {values.branchIds.length} selected branch{values.branchIds.length !== 1 ? 'es' : ''}.
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
              >
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              className="bg-emerald-600 hover:bg-emerald-700"
              disabled={isSubmitting || loading}
            >
              {isSubmitting || loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {isEditing ? 'Updating...' : 'Adding...'}
                </span>
              ) : (
                isEditing ? 'Update Category' : 'Add Category'
              )}
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default CategoryForm;