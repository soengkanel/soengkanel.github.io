/// <summary>
/// Page Extension NGT_PurchaseInvoice (ID 50104) extends Purchase Invoice.
/// Displays the read-only VAT Type field on the Purchase Invoice page.
/// </summary>
pageextension 50104 "NGT_PurchaseInvoice" extends "Purchase Invoice"
{
    layout
    {
        addafter("Buy-from Vendor Name")
        {
            field(NGT_VATType; Rec."NGT_VATType")
            {
                ApplicationArea = All;
                Editable = false;
                ToolTip = 'Indicates whether this is a VAT or Non-VAT purchase invoice, automatically determined based on vendor VAT registration status.';
            }
        }
    }
}
