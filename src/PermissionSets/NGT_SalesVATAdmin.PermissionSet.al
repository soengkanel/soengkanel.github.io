/// <summary>
/// Permission Set NGT_SalesVATAdmin (ID 50002).
/// Grants full administrative permissions for NGT Sales VAT configuration.
/// Assign this to system administrators who configure VAT number series.
/// </summary>
permissionset 50002 "NGT_SalesVATAdmin"
{
    Assignable = true;
    Caption = 'NGT Sales VAT Administrator';

    IncludedPermissionSets = "NGT_SalesVATUser";

    Permissions =
        // Sales & Receivables Setup - Full permissions for configuration
        tabledata "Sales & Receivables Setup" = RIMD,

        // Additional admin permissions
        tabledata "No. Series" = RIMD,
        tabledata "No. Series Line" = RIMD,
        tabledata "No. Series Relationship" = RIMD;
}
