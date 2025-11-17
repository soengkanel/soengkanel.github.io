/// <summary>
/// Permission Set NGT_PaymentJnlUser (ID 50005).
/// Grants permissions for users to work with Payment Journals with VAT validation.
/// Assign this to finance staff and payment processors.
/// </summary>
permissionset 50005 "NGT_PaymentJnlUser"
{
    Assignable = true;
    Caption = 'NGT Payment Journal User';

    Permissions =
        // Gen. Journal Batch - Read for batch selection
        tabledata "Gen. Journal Batch" = R,

        // Gen. Journal Line - Full permissions for payment processing
        tabledata "Gen. Journal Line" = RIMD,

        // Vendor - Read to check VAT registration
        tabledata "Vendor" = R;
}
