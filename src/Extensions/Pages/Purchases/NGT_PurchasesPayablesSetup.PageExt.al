/// <summary>
/// Page Extension NGT_PurchPayablesSetup (ID 50102) extends Purchases Payables Setup.
/// Adds VAT and Non-VAT number series configuration fields for Purchase Orders and Invoices.
/// </summary>
pageextension 50102 "NGT_PurchPayablesSetup" extends "Purchases & Payables Setup"
{
    layout
    {
        addafter("Number Series")
        {
            group("NGT_CustomNumberSeries")
            {
                Caption = 'Custom Number Series';

                field(NGT_VATPurchOrderSeries; Rec."NGT_VATPurchOrderSeries")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for VAT Purchase Orders (vendors with VAT Registration No.)';
                }

                // field(NGT_NonVATPurchOrderSeries; Rec."NGT_NonVATPurchOrderSeries")
                // {
                //     ApplicationArea = All;
                //     ToolTip = 'Specifies the number series for Non-VAT Purchase Orders (vendors without VAT Registration No.)';
                // }

                // field(NGT_VATPurchInvoiceSeries; Rec."NGT_VATPurchInvoiceSeries")
                // {
                //     ApplicationArea = All;
                //     ToolTip = 'Specifies the number series for VAT Purchase Invoices (vendors with VAT Registration No.)';
                // }

                field(NGT_NonVATPurchInvoiceSeries; Rec."NGT_NonVATPurchInvoiceSeries")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for Non-VAT Purchase Invoices (vendors without VAT Registration No.)';
                }
                field(NGT_PostedCommInvoiceNos; Rec."NGT_PostedCommInvoiceNos")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for Posted Commercial Purchase Invoices (vendors without VAT Registration No.)';
                }
                field(NGT_PostedCommCreditMemoNos; Rec."NGT_PostedCommCreditMemoNos")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for Posted Commercial Purchase Credit Memos (vendors without VAT Registration No.)';
                }
            }
        }
    }
}
