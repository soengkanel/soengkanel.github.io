import React from "react";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Edit, Trash2, Mail, Phone, MapPin, Users } from "lucide-react";
import { toast } from "sonner";

const EmployeeTable = ({ employees, onEdit, onDelete }) => {
  if (!employees || employees.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Users className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium text-foreground">No employees found</p>
          <p className="text-sm text-muted-foreground mt-1">Add your first employee to get started</p>
        </CardContent>
      </Card>
    );
  }

  const getRoleBadgeColor = (role) => {
    const colors = {
      "ROLE_STORE_MANAGER": "bg-purple-100 text-purple-800 border-purple-200",
      "ROLE_BRANCH_MANAGER": "bg-blue-100 text-blue-800 border-blue-200",
      "ROLE_BRANCH_CASHIER": "bg-green-100 text-green-800 border-green-200",
      "ROLE_KITCHEN_STAFF": "bg-orange-100 text-orange-800 border-orange-200",
      "ROLE_WAITER": "bg-yellow-100 text-yellow-800 border-yellow-200",
      "ROLE_INVENTORY_MANAGER": "bg-indigo-100 text-indigo-800 border-indigo-200",
      "ROLE_ACCOUNTANT": "bg-pink-100 text-pink-800 border-pink-200",
      "ROLE_HR_MANAGER": "bg-teal-100 text-teal-800 border-teal-200"
    };
    return colors[role] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  const formatRole = (role) => {
    return role.replace("ROLE_", "").replace(/_/g, " ");
  };

  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Branch</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {employees.map((employee) => (
                <TableRow key={employee.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      {employee.avatar && (
                        <img
                          src={employee.avatar}
                          alt={employee.fullName}
                          className="w-10 h-10 rounded-full"
                        />
                      )}
                      <div>
                        <div className="font-medium">{employee.fullName}</div>
                        {employee.department && (
                          <div className="text-xs text-muted-foreground">{employee.department}</div>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                        <span className="text-xs">{employee.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="h-3.5 w-3.5 text-muted-foreground" />
                        <span className="text-xs">{employee.phone}</span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getRoleBadgeColor(employee.role)}>
                      {formatRole(employee.role)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {employee.branch?.name ? (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{employee.branch.name}</span>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">All Branches</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={
                      employee.status === "ACTIVE"
                        ? "bg-green-50 text-green-700 border-green-200"
                        : "bg-gray-50 text-gray-700 border-gray-200"
                    }>
                      {employee.status || "ACTIVE"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onEdit(employee)}
                        className="h-8 w-8 p-0"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          onDelete(employee.id);
                          toast.success("Employee deleted successfully!");
                        }}
                        className="h-8 w-8 p-0 text-red-600 hover:text-red-800 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default EmployeeTable;