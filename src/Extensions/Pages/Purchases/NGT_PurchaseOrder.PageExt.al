/// <summary>
/// Page Extension NGT_PurchaseOrder (ID 50103) extends Purchase Order.
/// Displays the read-only VAT Type field on the Purchase Order page.
/// </summary>
pageextension 50103 "NGT_PurchaseOrder" extends "Purchase Order"
{
    layout
    {
        addafter("Buy-from Vendor Name")
        {
            field(NGT_VATType; Rec."NGT_VATType")
            {
                ApplicationArea = All;
                Editable = false;
                ToolTip = 'Indicates whether this is a VAT or Non-VAT purchase order, automatically determined based on vendor VAT registration status.';
            }
        }
    }
}
