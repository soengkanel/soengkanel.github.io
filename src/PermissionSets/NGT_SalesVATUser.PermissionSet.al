/// <summary>
/// Permission Set NGT_SalesVATUser (ID 50001).
/// Grants permissions for users to work with Sales Orders with VAT/Non-VAT logic.
/// Assign this to sales staff and order processors.
/// </summary>
permissionset 50001 "NGT_SalesVATUser"
{
    Assignable = true;
    Caption = 'NGT Sales VAT User';

    Permissions =
        // Sales & Receivables Setup - Read only for users
        tabledata "Sales & Receivables Setup" = R,

        // Sales Header - Full permissions for order processing
        tabledata "Sales Header" = RIMD,
        tabledata "Sales Line" = RIMD,

        // Customer - Read to check VAT registration
        tabledata "Customer" = R,

        // Item - Read to view item class
        tabledata "Item" = R,

        // No. Series - Read only
        tabledata "No. Series" = R,
        tabledata "No. Series Line" = R;
}
