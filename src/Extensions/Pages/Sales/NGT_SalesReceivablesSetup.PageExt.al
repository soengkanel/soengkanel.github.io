/// <summary>
/// Page Extension NGT_SalesReceivablesSetup (ID 50100) extends Sales Receivables Setup.
/// Adds VAT and Non-VAT number series configuration fields to the setup page.
/// </summary>
pageextension 50100 "NGT_SalesReceivablesSetup" extends "Sales & Receivables Setup"
{
    layout
    {
        addafter("Number Series")
        {
            group("NGT_CustomNumberSeries")
            {
                Caption = 'Custom Number Series';

                field(NGT_VATSalesNoSeries; Rec."NGT_VATSalesNoSeries")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for VAT Sales Orders (customers with VAT Registration No.)';
                }

                field(NGT_NonVATSalesNoSeries; Rec."NGT_NonVATSalesNoSeries")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for Non-VAT Sales Orders (customers without VAT Registration No.)';
                }
                field(NGT_PostedCommInvoiceNos; Rec."NGT_PostedCommInvoiceNos")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for Posted Commercial Invoices.';
                }
                field(NGT_PostedCommCreditMemoNos; Rec."NGT_PostedCommCreditMemoNos")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the number series for Posted Commercial Credit Memos.';
                }

            }
        }
    }
    #region Event Subscribers
    #endregion
}