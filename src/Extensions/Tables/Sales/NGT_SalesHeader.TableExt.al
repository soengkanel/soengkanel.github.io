/// <summary>
/// Table Extension NGT_SalesHeader (ID 50001) extends Sales Header.
/// Adds VAT Type field to distinguish between VAT and Non-VAT sales orders.
/// </summary>
tableextension 50001 "NGT_SalesHeader" extends "Sales Header"
{
    fields
    {
        field(50000; "NGT_VATType"; Option)
        {
            Caption = 'VAT Type';
            OptionMembers = " ","VAT","Non-VAT";
            OptionCaption = ' ,VAT,Non-VAT';
            DataClassification = CustomerContent;
            Editable = false;
        }

        field(50001; "NGT_CustomerName"; Text[250])
        {
            Caption = 'Customer name';
            Editable = false;
            DataClassification = CustomerContent;
        }
    }

    trigger OnBeforeInsert()
    var
        SalesSetup: Record "Sales & Receivables Setup";
        Customer: Record Customer;
        NoSeriesManagement: Codeunit "No. Series";
        NewNo: Code[20];
    begin
        // Only apply for Sales Orders with a customer and no number assigned yet
        if ("Document Type" <> "Document Type"::Order) or ("Sell-to Customer No." = '') or ("No." <> '') then
            exit;

        if not SalesSetup.Get() then
            exit;

        if not Customer.Get("Sell-to Customer No.") then
            exit;

        // Override No. Series and generate number based on customer VAT status
        if Customer."VAT Registration No." <> '' then begin
            if SalesSetup."NGT_VATSalesNoSeries" <> '' then begin
                "No. Series" := SalesSetup."NGT_VATSalesNoSeries";
                NewNo := NoSeriesManagement.GetNextNo(SalesSetup."NGT_VATSalesNoSeries", WorkDate(), true);
                "No." := NewNo;
            end;
        end else begin
            if SalesSetup."NGT_NonVATSalesNoSeries" <> '' then begin
                "No. Series" := SalesSetup."NGT_NonVATSalesNoSeries";
                NewNo := NoSeriesManagement.GetNextNo(SalesSetup."NGT_NonVATSalesNoSeries", WorkDate(), true);
                "No." := NewNo;
            end;
        end;
    end;

    procedure UpdateCustomerNoDisplay()
    var
        Customer: Record Customer;
        VATTypeText: Text[10];
    begin
        if "Sell-to Customer No." = '' then begin
            "NGT_CustomerName" := '';
            exit;
        end;

        case "NGT_VATType" of
            "NGT_VATType"::VAT:
                VATTypeText := 'VAT';
            "NGT_VATType"::"Non-VAT":
                VATTypeText := 'NVAT';
            else
                VATTypeText := '';
        end;

        if Customer.Get("Sell-to Customer No.") then begin
            "NGT_CustomerName" := "Sell-to Customer Name";
        end;
    end;
}
