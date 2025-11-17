/// <summary>
/// Table Extension NGT_SalesReceivablesSetup (ID 50000) extends Sales Receivables Setup.
/// Adds VAT and Non-VAT number series configuration fields for Sales Orders.
/// </summary>
tableextension 50000 "NGT_SalesReceivablesSetup" extends "Sales & Receivables Setup"
{
    fields
    {
        field(50000; "NGT_VATSalesNoSeries"; Code[20])
        {
            Caption = 'Sales Order VAT';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }

        field(50001; "NGT_NonVATSalesNoSeries"; Code[20])
        {
            Caption = 'Sales Order Non VAT';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }
        field(50107; "NGT_PostedCommInvoiceNos"; Code[20])
        {
            Caption = 'Posted Comm Invoice Nos.';
            TableRelation = "No. Series";
        }
        field(50108; "NGT_PostedCommCreditMemoNos"; Code[20])
        {
            Caption = 'Posted Comm Credit Memo Nos.';
            TableRelation = "No. Series";
        }
    }
}
