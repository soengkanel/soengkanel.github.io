import React, { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { QrCode, Eye, Copy, ExternalLink, Smartphone, Monitor, CheckCircle, Download, Search, TableProperties } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Input } from "../../../components/ui/input";
import { fetchTables } from "../../../Redux Toolkit/features/table/tableThunks";
import QRCodeLib from "qrcode";
import { mockTables, getTablesByBranch } from "../../../data/mockFnBData";

export default function EMenu() {
  const dispatch = useDispatch();
  const { store } = useSelector((state) => state.store);
  const { branches } = useSelector((state) => state.branch);
  const { tables: reduxTables, loading: tablesLoading } = useSelector((state) => state.table);
  const [copied, setCopied] = useState(false);
  const [copiedTableId, setCopiedTableId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBranch, setSelectedBranch] = useState(null); // null = all branches
  const qrCanvasRef = useRef(null);
  const [tableQRs, setTableQRs] = useState({});

  // Generate eMenu URL based on store
  const eMenuUrl = store?.id
    ? `${window.location.origin}/emenu/${store.id}`
    : `${window.location.origin}/emenu/preview`;

  // Use mock tables if Redux tables are empty, then filter by branch if selected
  const allTables = (reduxTables && reduxTables.length > 0) ? reduxTables : mockTables;
  const tables = selectedBranch ? getTablesByBranch(selectedBranch) : allTables;

  // Fetch tables on component mount
  useEffect(() => {
    // You'll need to pass the appropriate branchId here
    // For now, we'll use a placeholder or get from store
    if (store?.branches?.[0]?.id) {
      dispatch(fetchTables(store.branches[0].id));
    }
  }, [dispatch, store?.branches]);

  // Generate QR code preview - square shape
  useEffect(() => {
    if (qrCanvasRef.current && eMenuUrl) {
      QRCodeLib.toCanvas(qrCanvasRef.current, eMenuUrl, {
        width: 180,
        height: 180,
        margin: 1,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      }).catch(err => {
        console.error('Error generating QR preview:', err);
      });
    }
  }, [eMenuUrl]);

  // Generate QR codes for all tables
  useEffect(() => {
    const generateTableQRs = async () => {
      const qrs = {};
      for (const table of tables) {
        try {
          const tableUrl = store?.id
            ? `${window.location.origin}/emenu/${store.id}?table=${table.id}`
            : `${window.location.origin}/emenu/preview?table=${table.id}`;

          const canvas = document.createElement('canvas');
          await QRCodeLib.toCanvas(canvas, tableUrl, {
            width: 80,
            height: 80,
            margin: 0,
            color: {
              dark: '#000000',
              light: '#FFFFFF'
            }
          });
          qrs[table.id] = canvas.toDataURL();
        } catch (err) {
          console.error('Error generating table QR:', err);
        }
      }
      setTableQRs(qrs);
    };

    if (tables && tables.length > 0) {
      generateTableQRs();
    }
  }, [tables, store?.id]);

  // Generate table-specific URL
  const getTableUrl = (tableId) => {
    return store?.id
      ? `${window.location.origin}/emenu/${store.id}?table=${tableId}`
      : `${window.location.origin}/emenu/preview?table=${tableId}`;
  };

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(eMenuUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyTableUrl = (tableId) => {
    navigator.clipboard.writeText(getTableUrl(tableId));
    setCopiedTableId(tableId);
    setTimeout(() => setCopiedTableId(null), 2000);
  };

  const handlePreview = () => {
    window.open(eMenuUrl, '_blank');
  };

  const handlePreviewTable = (tableId) => {
    window.open(getTableUrl(tableId), '_blank');
  };

  const handleDownloadQR = async () => {
    try {
      const canvas = document.createElement('canvas');
      await QRCodeLib.toCanvas(canvas, eMenuUrl, {
        width: 512,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });

      const url = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `menu-qr-code.png`;
      link.href = url;
      link.click();
    } catch (error) {
      console.error('Error generating QR code:', error);
      alert('Failed to generate QR code');
    }
  };

  const handleDownloadTableQR = async (table) => {
    try {
      const canvas = document.createElement('canvas');
      const tableUrl = getTableUrl(table.id);

      // Generate QR code
      await QRCodeLib.toCanvas(canvas, tableUrl, {
        width: 512,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });

      // Create a larger canvas with text
      const finalCanvas = document.createElement('canvas');
      const ctx = finalCanvas.getContext('2d');
      finalCanvas.width = 600;
      finalCanvas.height = 700;

      // Fill background
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, finalCanvas.width, finalCanvas.height);

      // Draw QR code
      ctx.drawImage(canvas, 44, 50, 512, 512);

      // Add store name
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 28px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(store?.name || 'Restaurant Menu', finalCanvas.width / 2, 35);

      // Add table information
      ctx.font = 'bold 36px Arial';
      ctx.fillText(`Table ${table.tableNumber}`, finalCanvas.width / 2, 610);

      // Add area if available
      if (table.area) {
        ctx.font = '20px Arial';
        ctx.fillStyle = '#666666';
        ctx.fillText(table.area, finalCanvas.width / 2, 640);
      }

      // Add instruction text
      ctx.font = '18px Arial';
      ctx.fillStyle = '#666666';
      ctx.fillText('Scan to view menu & order', finalCanvas.width / 2, 670);

      // Download
      const url = finalCanvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `table-${table.tableNumber}-qr-code.png`;
      link.href = url;
      link.click();
    } catch (error) {
      console.error('Error generating QR code:', error);
      alert('Failed to generate QR code');
    }
  };

  const handleDownloadAllTableQRs = async () => {
    try {
      for (const table of filteredTables) {
        await handleDownloadTableQR(table);
        // Add a small delay between downloads to prevent browser blocking
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    } catch (error) {
      console.error('Error generating QR codes:', error);
      alert('Failed to generate all QR codes');
    }
  };

  // Filter tables based on search query
  const filteredTables = (tables || []).filter((table) => {
    const searchLower = searchQuery.toLowerCase();
    return (
      table.tableNumber.toLowerCase().includes(searchLower) ||
      table.location?.toLowerCase().includes(searchLower) ||
      table.area?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Digital Menu QR Codes</h1>
          <p className="text-sm text-muted-foreground mt-1">Generate and download QR codes for your menu</p>
        </div>
        <Button
          variant="outline"
          onClick={handlePreview}
          className="gap-2"
        >
          <Eye className="w-4 h-4" />
          Preview Menu
        </Button>
      </div>

      {/* Branch Info Alert */}
      {selectedBranch && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
          <p className="text-blue-900">
            <span className="font-semibold">Branch Filter Active:</span> Showing tables for{" "}
            <span className="font-semibold">
              {branches.find((b) => b.id === selectedBranch)?.name}
            </span>
          </p>
        </div>
      )}

      {/* General Menu QR */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">General Menu QR Code</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">Use this QR for general menu access</p>
            </div>
            <Button onClick={handleDownloadQR} size="sm" className="gap-2">
              <Download className="w-4 h-4" />
              Download QR
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-start gap-6">
            {/* QR Code Preview - Perfect Square */}
            <div className="w-48 h-48 bg-white border-2 border-gray-200 rounded-lg flex items-center justify-center p-4 flex-shrink-0">
              <canvas ref={qrCanvasRef} className="w-full h-full"></canvas>
            </div>

            {/* URL and Info */}
            <div className="flex-1 space-y-3">
              <div>
                <label className="text-sm font-medium mb-2 block">Menu URL</label>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    value={eMenuUrl}
                    readOnly
                    className="flex-1 font-mono text-sm"
                    onClick={(e) => e.target.select()}
                  />
                  <Button
                    variant="outline"
                    onClick={handleCopyUrl}
                    className="gap-2"
                  >
                    {copied ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </div>

              <div className="bg-muted/50 rounded-lg p-4">
                <h4 className="text-sm font-semibold mb-2">How to use:</h4>
                <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                  <li>Download the QR code using the button above</li>
                  <li>Print the QR code and place it in your store</li>
                  <li>Customers can scan to view your digital menu</li>
                </ol>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table QR Codes List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Table-Specific QR Codes</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {filteredTables.length} table{filteredTables.length !== 1 ? 's' : ''} available
              </p>
            </div>
            <div className="flex gap-2">
              <div className="relative w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  type="text"
                  placeholder="Search tables..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <select
                value={selectedBranch || "all"}
                onChange={(e) => setSelectedBranch(e.target.value === "all" ? null : parseInt(e.target.value))}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Branches</option>
                {(branches || []).map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
              <Button
                onClick={handleDownloadAllTableQRs}
                variant="outline"
                className="gap-2"
                disabled={filteredTables.length === 0}
              >
                <Download className="w-4 h-4" />
                Download All
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {tablesLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-sm text-muted-foreground mt-3">Loading tables...</p>
            </div>
          ) : filteredTables.length === 0 ? (
            <div className="text-center py-12 bg-muted/30 rounded-lg">
              <TableProperties className="w-12 h-12 text-muted-foreground/60 mx-auto mb-3" />
              <p className="text-sm text-foreground font-medium">
                {searchQuery ? "No tables found" : "No tables available"}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                {searchQuery ? "Try a different search term" : "Add tables to generate QR codes"}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredTables.map((table) => (
                <div
                  key={table.id}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:bg-accent transition-colors"
                >
                  {/* QR Code Preview */}
                  <div className="w-20 h-20 bg-white border border-gray-200 rounded flex items-center justify-center flex-shrink-0">
                    {tableQRs[table.id] ? (
                      <img
                        src={tableQRs[table.id]}
                        alt={`QR Code for Table ${table.tableNumber}`}
                        className="w-full h-full object-contain"
                      />
                    ) : (
                      <div className="animate-pulse bg-gray-200 w-full h-full rounded"></div>
                    )}
                  </div>

                  {/* Table Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-base">Table {table.tableNumber}</h3>
                      <Badge
                        variant="outline"
                        className={`${
                          table.status === "AVAILABLE"
                            ? "border-green-200 bg-green-50 text-green-700"
                            : table.status === "OCCUPIED"
                            ? "border-red-200 bg-red-50 text-red-700"
                            : "border-yellow-200 bg-yellow-50 text-yellow-700"
                        }`}
                      >
                        {table.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                      {(table.area || table.location) && (
                        <span>{table.area || table.location}</span>
                      )}
                      <span>Capacity: {table.capacity} guests</span>
                    </div>
                  </div>

                  {/* URL */}
                  <div className="flex items-center gap-2 flex-1 max-w-md">
                    <Input
                      type="text"
                      value={getTableUrl(table.id)}
                      readOnly
                      className="font-mono text-xs"
                      onClick={(e) => e.target.select()}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopyTableUrl(table.id)}
                      className="flex-shrink-0"
                    >
                      {copiedTableId === table.id ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePreviewTable(table.id)}
                      className="gap-2"
                    >
                      <Eye className="w-4 h-4" />
                      Preview
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleDownloadTableQR(table)}
                      className="gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download QR
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
