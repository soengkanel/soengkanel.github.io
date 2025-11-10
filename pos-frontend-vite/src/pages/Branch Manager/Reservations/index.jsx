import React, { useState } from 'react';
import { Plus, Calendar } from 'lucide-react';
import ReservationList from './ReservationList';
import CreateReservationForm from './CreateReservationForm';

const ReservationsPage = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingReservation, setEditingReservation] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // TODO: Get branchId from context or props
  const branchId = 1; // This should come from your auth/context

  const handleSuccess = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleEditReservation = (reservation) => {
    setEditingReservation(reservation);
    setShowCreateForm(true);
  };

  const handleCloseForm = () => {
    setShowCreateForm(false);
    setEditingReservation(null);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Calendar size={32} />
              Reservations
            </h1>
            <p className="text-gray-600 mt-1">
              Manage your restaurant table reservations
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md"
          >
            <Plus size={20} />
            New Reservation
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <ReservationList
          key={refreshKey}
          branchId={branchId}
          onEditReservation={handleEditReservation}
        />
      </div>

      {showCreateForm && (
        <CreateReservationForm
          branchId={branchId}
          onClose={handleCloseForm}
          onSuccess={handleSuccess}
          editData={editingReservation}
        />
      )}
    </div>
  );
};

export default ReservationsPage;
