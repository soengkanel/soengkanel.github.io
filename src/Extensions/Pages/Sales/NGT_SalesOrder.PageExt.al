/// <summary>
/// Page Extension NGT_SalesOrder (ID 50101) extends Sales Order.
/// Displays the read-only VAT Type field on the Sales Order page.
/// </summary>
pageextension 50101 "NGT_SalesOrder" extends "Sales Order"
{
    layout
    {
        modify("Sell-to Customer No.")
        {
            ShowMandatory = true;
        }

        modify("Sell-to Customer Name")
        {
            Visible = false;
        }

        addafter("Sell-to Customer No.")
        {
            field(NGT_CustomerNoDisplay; Rec."NGT_CustomerName")
            {
                ApplicationArea = All;
                Caption = 'Customer Name';
                Editable = false;
                ToolTip = 'Displays the customer customer name after selected';
            }

            field(NGT_VATType; Rec."NGT_VATType")
            {
                ApplicationArea = All;
                Editable = false;
                ToolTip = 'Indicates whether this is a VAT or Non-VAT sales order, automatically determined based on customer VAT registration status.';
            }
        }
    }

    trigger OnInsertRecord(BelowxRec: Boolean): Boolean
    begin
        if (Rec."Sell-to Customer No." = '') or (Rec."Sell-to Customer Name" = '') then begin
            Message('Please select a customer before saving the sales order.');
            exit(false);
        end;
        exit(true);
    end;

    trigger OnModifyRecord(): Boolean
    begin
        // Only allow auto-save if customer is selected
        if (Rec."Sell-to Customer No." = '') or (Rec."Sell-to Customer Name" = '') then begin
            Message('Please select a customer before making changes to the sales order.');
            exit(false);
        end;
        exit(true);
    end;
}
