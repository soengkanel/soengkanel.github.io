import React, { useState, useEffect } from 'react';
import { Download, RefreshCw, QrCode, Printer } from 'lucide-react';
import emenuApi from '../../../utils/emenuApi';
import api from '../../../utils/api';

const QRCodeManagement = ({ branchId }) => {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [qrCodeUrl, setQrCodeUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTables();
  }, [branchId]);

  const fetchTables = async () => {
    try {
      const response = await api.get(`/api/tables/branch/${branchId}`);
      setTables(response.data);
    } catch (error) {
      console.error('Error fetching tables:', error);
    }
  };

  const generateQRCode = async (tableId) => {
    try {
      setLoading(true);
      const qrBlob = await emenuApi.generateQRCode(tableId);
      const url = URL.createObjectURL(qrBlob);
      setQrCodeUrl(url);
      setSelectedTable(tables.find(t => t.id === tableId));
    } catch (error) {
      console.error('Error generating QR code:', error);
      alert('Failed to generate QR code');
    } finally {
      setLoading(false);
    }
  };

  const regenerateToken = async (tableId) => {
    if (!window.confirm('This will invalidate the old QR code. Continue?')) {
      return;
    }

    try {
      await emenuApi.regenerateToken(tableId);
      alert('QR code token regenerated successfully');
      generateQRCode(tableId);
    } catch (error) {
      console.error('Error regenerating token:', error);
      alert('Failed to regenerate token');
    }
  };

  const downloadQRCode = () => {
    if (!qrCodeUrl || !selectedTable) return;

    const link = document.createElement('a');
    link.href = qrCodeUrl;
    link.download = `table-${selectedTable.tableNumber}-qr.png`;
    link.click();
  };

  const printQRCode = () => {
    if (!qrCodeUrl) return;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Table ${selectedTable.tableNumber} QR Code</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              text-align: center;
              padding: 40px;
            }
            .container {
              max-width: 400px;
              margin: 0 auto;
              border: 2px solid #000;
              padding: 30px;
              border-radius: 10px;
            }
            h1 { margin: 0 0 10px 0; font-size: 28px; }
            h2 { margin: 0 0 20px 0; font-size: 48px; font-weight: bold; }
            img { width: 300px; height: 300px; margin: 20px 0; }
            p { font-size: 16px; margin: 10px 0; }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>Welcome to</h1>
            <h2>Table ${selectedTable.tableNumber}</h2>
            <img src="${qrCodeUrl}" alt="QR Code" />
            <p><strong>Scan to view menu & order</strong></p>
            <p style="font-size: 14px; color: #666;">Contactless ordering available</p>
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    setTimeout(() => {
      printWindow.print();
    }, 250);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2 mb-2">
          <QrCode size={28} />
          QR Code Management
        </h2>
        <p className="text-gray-600">Generate and print QR codes for table-side ordering</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Table List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Select Table</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
            {tables.map((table) => (
              <button
                key={table.id}
                onClick={() => generateQRCode(table.id)}
                className={`p-4 border-2 rounded-lg hover:bg-blue-50 transition-colors ${
                  selectedTable?.id === table.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="text-center">
                  <div className="font-semibold text-lg">{table.tableNumber}</div>
                  <div className="text-sm text-gray-600">
                    Capacity: {table.capacity}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* QR Code Display */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">QR Code</h3>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : qrCodeUrl && selectedTable ? (
            <div className="text-center">
              <div className="bg-gray-50 p-6 rounded-lg mb-4 inline-block">
                <img
                  src={qrCodeUrl}
                  alt="QR Code"
                  className="w-64 h-64 mx-auto"
                />
              </div>

              <div className="mb-4">
                <h4 className="text-xl font-bold">Table {selectedTable.tableNumber}</h4>
                <p className="text-sm text-gray-600">
                  {selectedTable.location || 'General Area'}
                </p>
              </div>

              <div className="flex flex-col gap-3">
                <button
                  onClick={downloadQRCode}
                  className="flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
                >
                  <Download size={20} />
                  Download QR Code
                </button>

                <button
                  onClick={printQRCode}
                  className="flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700"
                >
                  <Printer size={20} />
                  Print QR Code
                </button>

                <button
                  onClick={() => regenerateToken(selectedTable.id)}
                  className="flex items-center justify-center gap-2 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300"
                >
                  <RefreshCw size={20} />
                  Regenerate QR Code
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <div className="text-center">
                <QrCode size={48} className="mx-auto mb-2 opacity-50" />
                <p>Select a table to generate QR code</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">Instructions:</h4>
        <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
          <li>Select a table to generate its unique QR code</li>
          <li>Download or print the QR code</li>
          <li>Place the QR code on or near the table</li>
          <li>Customers can scan to view menu and place orders</li>
          <li>Regenerate QR codes if they are compromised or for security</li>
        </ul>
      </div>
    </div>
  );
};

export default QRCodeManagement;
