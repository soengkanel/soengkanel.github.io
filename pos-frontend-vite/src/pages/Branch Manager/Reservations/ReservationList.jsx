import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Users, Phone, Mail, CheckCircle, XCircle, Clock as ClockIcon, AlertCircle } from 'lucide-react';
import reservationApi from '../../../utils/reservationApi';

const ReservationList = ({ branchId, onEditReservation }) => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchReservations();
  }, [branchId, filter, selectedDate]);

  const fetchReservations = async () => {
    try {
      setLoading(true);
      let data;

      if (filter === 'all') {
        data = await reservationApi.getReservationsByBranchAndDate(branchId, selectedDate);
      } else if (filter === 'upcoming') {
        data = await reservationApi.getUpcomingReservations(branchId);
      } else {
        data = await reservationApi.getReservationsByBranchAndStatus(branchId, filter.toUpperCase());
      }

      setReservations(data);
    } catch (error) {
      console.error('Error fetching reservations:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      PENDING: { color: 'bg-yellow-100 text-yellow-800', icon: ClockIcon },
      CONFIRMED: { color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
      SEATED: { color: 'bg-green-100 text-green-800', icon: Users },
      COMPLETED: { color: 'bg-gray-100 text-gray-800', icon: CheckCircle },
      CANCELLED: { color: 'bg-red-100 text-red-800', icon: XCircle },
      NO_SHOW: { color: 'bg-orange-100 text-orange-800', icon: AlertCircle },
    };

    const config = statusConfig[status] || statusConfig.PENDING;
    const Icon = config.icon;

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${config.color}`}>
        <Icon size={14} />
        {status}
      </span>
    );
  };

  const handleConfirm = async (id) => {
    try {
      await reservationApi.confirmReservation(id);
      fetchReservations();
    } catch (error) {
      console.error('Error confirming reservation:', error);
      alert('Failed to confirm reservation');
    }
  };

  const handleCancel = async (id) => {
    const reason = prompt('Please enter cancellation reason:');
    if (reason) {
      try {
        await reservationApi.cancelReservation(id, reason);
        fetchReservations();
      } catch (error) {
        console.error('Error cancelling reservation:', error);
        alert('Failed to cancel reservation');
      }
    }
  };

  const handleSeat = async (id, tableId) => {
    if (!tableId) {
      alert('Please assign a table first');
      return;
    }
    try {
      await reservationApi.seatReservation(id, tableId);
      fetchReservations();
    } catch (error) {
      console.error('Error seating reservation:', error);
      alert('Failed to seat reservation');
    }
  };

  const handleComplete = async (id) => {
    try {
      await reservationApi.completeReservation(id);
      fetchReservations();
    } catch (error) {
      console.error('Error completing reservation:', error);
      alert('Failed to complete reservation');
    }
  };

  const handleNoShow = async (id) => {
    if (window.confirm('Mark this reservation as no-show?')) {
      try {
        await reservationApi.markAsNoShow(id);
        fetchReservations();
      } catch (error) {
        console.error('Error marking as no-show:', error);
        alert('Failed to mark as no-show');
      }
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading reservations...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-4 items-center mb-6">
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        />

        <div className="flex gap-2">
          {['all', 'upcoming', 'pending', 'confirmed', 'seated'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg capitalize ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {reservations.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No reservations found for the selected criteria
        </div>
      ) : (
        <div className="grid gap-4">
          {reservations.map((reservation) => (
            <div
              key={reservation.id}
              className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">{reservation.customerName}</h3>
                    {getStatusBadge(reservation.status)}
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Calendar size={16} />
                      <span>{new Date(reservation.reservationDate).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock size={16} />
                      <span>{reservation.reservationTime}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users size={16} />
                      <span>{reservation.numberOfGuests} guests</span>
                    </div>
                    {reservation.tableNumber && (
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Table:</span>
                        <span>{reservation.tableNumber}</span>
                      </div>
                    )}
                  </div>

                  <div className="mt-3 space-y-1 text-sm text-gray-600">
                    {reservation.customerPhone && (
                      <div className="flex items-center gap-2">
                        <Phone size={14} />
                        <span>{reservation.customerPhone}</span>
                      </div>
                    )}
                    {reservation.customerEmail && (
                      <div className="flex items-center gap-2">
                        <Mail size={14} />
                        <span>{reservation.customerEmail}</span>
                      </div>
                    )}
                  </div>

                  {reservation.specialRequests && (
                    <div className="mt-3 p-3 bg-yellow-50 rounded border border-yellow-200">
                      <p className="text-sm">
                        <span className="font-medium">Special Requests: </span>
                        {reservation.specialRequests}
                      </p>
                    </div>
                  )}

                  <div className="mt-2 text-xs text-gray-500">
                    Confirmation Code: {reservation.confirmationCode}
                  </div>
                </div>
              </div>

              <div className="flex gap-2 flex-wrap">
                {reservation.status === 'PENDING' && (
                  <>
                    <button
                      onClick={() => handleConfirm(reservation.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => handleCancel(reservation.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                    >
                      Cancel
                    </button>
                  </>
                )}

                {reservation.status === 'CONFIRMED' && (
                  <>
                    <button
                      onClick={() => handleSeat(reservation.id, reservation.tableId)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                    >
                      Seat Customer
                    </button>
                    <button
                      onClick={() => handleNoShow(reservation.id)}
                      className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm"
                    >
                      No Show
                    </button>
                    <button
                      onClick={() => handleCancel(reservation.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                    >
                      Cancel
                    </button>
                  </>
                )}

                {reservation.status === 'SEATED' && (
                  <button
                    onClick={() => handleComplete(reservation.id)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
                  >
                    Complete
                  </button>
                )}

                <button
                  onClick={() => onEditReservation(reservation)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                >
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReservationList;
