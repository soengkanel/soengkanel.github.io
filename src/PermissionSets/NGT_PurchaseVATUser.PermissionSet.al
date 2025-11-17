/// <summary>
/// Permission Set NGT_PurchaseVATUser (ID 50004).
/// Grants permissions for users to work with Purchase Orders and Invoices with VAT/Non-VAT logic.
/// Assign this to purchasing staff and order processors.
/// </summary>
permissionset 50004 "NGT_PurchaseVATUser"
{
    Assignable = true;
    Caption = 'NGT Purchase VAT User';

    Permissions =
        // Purchases & Payables Setup - Read only for users
        tabledata "Purchases & Payables Setup" = R,

        // Purchase Header - Full permissions for order/invoice processing
        tabledata "Purchase Header" = RIMD,
        tabledata "Purchase Line" = RIMD,

        // Vendor - Read to check VAT registration
        tabledata "Vendor" = R,

        // No. Series - Read only
        tabledata "No. Series" = R,
        tabledata "No. Series Line" = R;
}
