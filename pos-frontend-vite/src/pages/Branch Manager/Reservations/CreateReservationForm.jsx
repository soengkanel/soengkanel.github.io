import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import reservationApi from '../../../utils/reservationApi';
import api from '../../../utils/api';

const CreateReservationForm = ({ branchId, onClose, onSuccess, editData = null }) => {
  const [formData, setFormData] = useState({
    customerId: editData?.customerId || '',
    branchId: branchId,
    tableId: editData?.tableId || '',
    reservationDate: editData?.reservationDate || new Date().toISOString().split('T')[0],
    reservationTime: editData?.reservationTime || '12:00',
    numberOfGuests: editData?.numberOfGuests || 2,
    specialRequests: editData?.specialRequests || '',
    durationMinutes: editData?.durationMinutes || 120,
  });

  const [customers, setCustomers] = useState([]);
  const [tables, setTables] = useState([]);
  const [availableTables, setAvailableTables] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showNewCustomer, setShowNewCustomer] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    fullName: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    fetchCustomers();
    fetchTables();
  }, []);

  useEffect(() => {
    if (formData.reservationDate && formData.reservationTime && formData.numberOfGuests) {
      checkAvailableTables();
    }
  }, [formData.reservationDate, formData.reservationTime, formData.numberOfGuests, formData.durationMinutes]);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/api/customers');
      setCustomers(response.data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const fetchTables = async () => {
    try {
      const response = await api.get(`/api/tables/branch/${branchId}`);
      setTables(response.data);
    } catch (error) {
      console.error('Error fetching tables:', error);
    }
  };

  const checkAvailableTables = async () => {
    try {
      const tableIds = await reservationApi.getAvailableTables(
        branchId,
        formData.reservationDate,
        formData.reservationTime,
        formData.numberOfGuests,
        formData.durationMinutes
      );
      setAvailableTables(tableIds);
    } catch (error) {
      console.error('Error checking available tables:', error);
    }
  };

  const handleCreateCustomer = async () => {
    try {
      const response = await api.post('/api/customers', newCustomer);
      setCustomers([...customers, response.data]);
      setFormData({ ...formData, customerId: response.data.id });
      setShowNewCustomer(false);
      setNewCustomer({ fullName: '', email: '', phone: '' });
    } catch (error) {
      console.error('Error creating customer:', error);
      alert('Failed to create customer');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const dataToSubmit = {
        ...formData,
        customerId: parseInt(formData.customerId),
        branchId: parseInt(formData.branchId),
        tableId: formData.tableId ? parseInt(formData.tableId) : null,
        numberOfGuests: parseInt(formData.numberOfGuests),
        durationMinutes: parseInt(formData.durationMinutes),
      };

      if (editData) {
        await reservationApi.updateReservation(editData.id, dataToSubmit);
      } else {
        await reservationApi.createReservation(dataToSubmit);
      }

      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving reservation:', error);
      setError(error.response?.data?.message || 'Failed to save reservation');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold">
            {editData ? 'Edit Reservation' : 'Create New Reservation'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer *
            </label>
            {!showNewCustomer ? (
              <div className="flex gap-2">
                <select
                  name="customerId"
                  value={formData.customerId}
                  onChange={handleChange}
                  required
                  className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a customer</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.fullName} - {customer.phone}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => setShowNewCustomer(true)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  New Customer
                </button>
              </div>
            ) : (
              <div className="border rounded-lg p-4 space-y-3">
                <h3 className="font-medium mb-2">New Customer</h3>
                <input
                  type="text"
                  placeholder="Full Name *"
                  value={newCustomer.fullName}
                  onChange={(e) => setNewCustomer({ ...newCustomer, fullName: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={newCustomer.email}
                  onChange={(e) => setNewCustomer({ ...newCustomer, email: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <input
                  type="tel"
                  placeholder="Phone"
                  value={newCustomer.phone}
                  onChange={(e) => setNewCustomer({ ...newCustomer, phone: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleCreateCustomer}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowNewCustomer(false)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reservation Date *
              </label>
              <input
                type="date"
                name="reservationDate"
                value={formData.reservationDate}
                onChange={handleChange}
                min={new Date().toISOString().split('T')[0]}
                required
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reservation Time *
              </label>
              <input
                type="time"
                name="reservationTime"
                value={formData.reservationTime}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Guests *
              </label>
              <input
                type="number"
                name="numberOfGuests"
                value={formData.numberOfGuests}
                onChange={handleChange}
                min="1"
                max="50"
                required
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (minutes) *
              </label>
              <select
                name="durationMinutes"
                value={formData.durationMinutes}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="60">1 hour</option>
                <option value="90">1.5 hours</option>
                <option value="120">2 hours</option>
                <option value="150">2.5 hours</option>
                <option value="180">3 hours</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Table (Optional)
            </label>
            <select
              name="tableId"
              value={formData.tableId}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">No table assigned yet</option>
              {tables
                .filter((table) => availableTables.includes(table.id) || table.id === editData?.tableId)
                .map((table) => (
                  <option key={table.id} value={table.id}>
                    {table.tableNumber} - Capacity: {table.capacity}
                    {availableTables.includes(table.id) ? ' (Available)' : ''}
                  </option>
                ))}
            </select>
            {availableTables.length === 0 && (
              <p className="text-sm text-red-600 mt-1">
                No tables available for this time slot with {formData.numberOfGuests} guests
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Special Requests
            </label>
            <textarea
              name="specialRequests"
              value={formData.specialRequests}
              onChange={handleChange}
              rows="3"
              maxLength="500"
              placeholder="Any dietary restrictions, accessibility needs, or special occasions..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              {formData.specialRequests.length}/500 characters
            </p>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium"
            >
              {loading ? 'Saving...' : editData ? 'Update Reservation' : 'Create Reservation'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg hover:bg-gray-200 font-medium"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateReservationForm;
