/// <summary>
/// Table Extension NGT_PurchPayablesSetup (ID 51000) extends Purchases Payables Setup.
/// Adds VAT and Non-VAT number series configuration fields for Purchase Orders and Purchase Invoices.
/// </summary>
tableextension 51000 "NGT_PurchPayablesSetup" extends "Purchases & Payables Setup"
{
    fields
    {
        // Purchase Order Number Series
        field(51000; "NGT_VATPurchOrderSeries"; Code[20])
        {
            Caption = 'VAT Purchase Order No. Series';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }

        field(51001; "NGT_NonVATPurchOrderSeries"; Code[20])
        {
            Caption = 'Non-VAT Purchase Order No. Series';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }

        // Purchase Invoice Number Series
        field(51002; "NGT_VATPurchInvoiceSeries"; Code[20])
        {
            Caption = 'VAT Purchase Invoice No. Series';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }

        field(51003; "NGT_NonVATPurchInvoiceSeries"; Code[20])
        {
            Caption = 'Non-VAT Purchase Invoice No. Series';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }
        field(51004; "NGT_PostedCommInvoiceNos"; Code[20])
        {
            Caption = 'Posted Non-VAT Purchase Invoice Nos.';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }
        field(51005; "NGT_PostedCommCreditMemoNos"; Code[20])
        {
            Caption = 'Posted CommCreditMemoNos';
            TableRelation = "No. Series";
            DataClassification = CustomerContent;
        }

    }
}
