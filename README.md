# 📜 NGT EXTENSION Coding Standards

This summary highlights the key coding standards for the **NGT EXTENSION** project to maintain consistency and readability.

---

## 1. 📂 Project Structure
```
NGTEXTENSION
└── src
    ├── Codeunits
    │   ├── Events
    │   │   └── NGT_CambodianTaxEventMgmt.CodeUnit.al
    │   └── Helpers    
    │       └── NGT_ReportHelper.CodeUnit.al
    ├── Extensions
    │   ├── Pages
        |    └── Customers
                    └── Subforms
    │   └── Tables
                └── Customers
    ├── Pages
    ├── Tables
    ├── PermissionSets
    └── Reports
        ├── Company
        |    └── NGT
        |        └─── Layouts
        |        |       ├── Excels
        |        |       ├── RDLC
        |        |       ├── Words   
        |        NGD
        |         └─────Layouts
        |                ├── Excels
        |                ├── RDLC
        |                ├── Words                  
```

---

## 2. 🏷️ Naming Conventions
- Prefix all objects with `NGT_`.
- Use **PascalCase** for file and object names.
- Match file names with object names.
- Suffix helpers with `Helper` or `Utility`.

---

## 3. ⚡ Codeunits
- **Naming:** Reflect purpose clearly.
- **Access:** Use `local` for private procedures.
- **Structure:** Use `#region` for grouping procedures.

---

## 4. 📝 Reports
- Use descriptive names (`NGT_SalesInvoice.Report.al`).
- Store layouts under `Reports/Layouts` with matching names.

---

## 5. 🚀 Procedures
- Use action-based names (`CalculateTotalAmount`, `GetCustomerBalance`).
- Provide descriptive error messages.

---

## 6. 🛠️ Events
- Prefer event subscribers over direct modifications.
- Prefix event triggers with `On` (e.g., `OnBeforeValidateCustomer`).

---

## 7. 💬 Documentation
- Add **XML documentation** for public procedures.
- Use inline comments sparingly and only for complex logic.

---

## 8. 🎨 Formatting
- **Indentation:** 4 spaces per level.
- **Braces:** Same line as statements.

---

## 9. 🔒 Permissions
- Store permission sets in `PermissionSets`.
- Use clear names (`NGT_Admin`, `NGT_Viewer`) with least privilege by default.

---

## 10. 💡 Best Practices
- Promote **reusability** through helper Codeunits.
- Maintain **consistency** in naming and formatting.
- Optimize for **performance** by reducing unnecessary operations.
- Ensure **testing** coverage for critical features.