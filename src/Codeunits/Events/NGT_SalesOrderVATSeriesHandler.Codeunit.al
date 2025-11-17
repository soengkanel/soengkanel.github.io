/// <summary>
/// Codeunit NGT_SalesVATSeriesHandler (ID 50000).
/// Handles automatic VAT Type assignment and number series selection for Sales Orders
/// based on customer VAT registration status.
/// </summary>
codeunit 50000 "NGT_SalesOrdVATSeriesHandler"
{
    #region Event Subscribers

    /// <summary>
    /// Event subscriber triggered when Sell-to Customer No. is validated on Sales Header.
    /// Automatically assigns VAT Type and appropriate number series based on customer VAT registration status.
    /// </summary>
    /// <param name="Rec">Sales Header record being modified.</param>
    /// <param name="xRec">Previous Sales Header record state.</param>
    [EventSubscriber(ObjectType::Table, Database::"Sales Header", 'OnAfterValidateEvent', 'Sell-to Customer No.', false, false)]
    local procedure OnAfterValidateSellToCustomerNo(var Rec: Record "Sales Header"; var xRec: Record "Sales Header")
    var
        SalesSetup: Record "Sales & Receivables Setup";
        Customer: Record Customer;
        xCustomer: Record Customer;
        NoSeries: Codeunit "No. Series";
        NewNo: Code[20];
        OldVATStatus: Boolean;
        NewVATStatus: Boolean;
    begin
        if Rec."Document Type" <> Rec."Document Type"::Order then
            exit;

        if not SalesSetup.Get() then
            exit;

        OldVATStatus := false;
        NewVATStatus := false;

        if xRec."Sell-to Customer No." <> '' then
            if xCustomer.Get(xRec."Sell-to Customer No.") then
                OldVATStatus := xCustomer."VAT Registration No." <> '';

        if Customer.Get(Rec."Sell-to Customer No.") then begin
            NewVATStatus := Customer."VAT Registration No." <> '';

            if (OldVATStatus <> NewVATStatus) and (Rec."No." <> '') then begin
                Error('The system has already automatically assigned a document number. Please verify the selected customer and create a new document if correction is needed.');
                exit;
            end;

            if NewVATStatus then begin
                Rec."NGT_VATType" := Rec."NGT_VATType"::"VAT";
                if SalesSetup."NGT_VATSalesNoSeries" <> '' then begin
                    if (Rec."No. Series" <> SalesSetup."NGT_VATSalesNoSeries") or (Rec."No." = '') then begin
                        if Rec."No." = '' then begin
                            Rec."No. Series" := SalesSetup."NGT_VATSalesNoSeries";
                            NewNo := NoSeries.GetNextNo(SalesSetup."NGT_VATSalesNoSeries", WorkDate(), true);
                            Rec."No." := NewNo;
                        end;
                    end;
                end;
            end else begin
                Rec."NGT_VATType" := Rec."NGT_VATType"::"Non-VAT";
                if SalesSetup."NGT_NonVATSalesNoSeries" <> '' then begin
                    if (Rec."No. Series" <> SalesSetup."NGT_NonVATSalesNoSeries") or (Rec."No." = '') then begin
                        if Rec."No." = '' then begin
                            Rec."No. Series" := SalesSetup."NGT_NonVATSalesNoSeries";
                            NewNo := NoSeries.GetNextNo(SalesSetup."NGT_NonVATSalesNoSeries", WorkDate(), true);
                            Rec."No." := NewNo;
                        end;
                    end;
                end;
            end;

            Rec.UpdateCustomerNoDisplay();
        end;
    end;

    /// <summary>
    /// Event subscriber triggered before a Sales Quote is transferred to a Sales Order.
    /// Sets the VAT Type based on customer VAT registration status.
    /// </summary>
    /// <param name="SalesOrderHeader">Sales Order Header record being created.</param>
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Sales-Quote to Order", 'OnBeforeInsertSalesOrderHeader', '', false, false)]
    local procedure OnBeforeQuoteToOrderTransfer(var SalesOrderHeader: Record "Sales Header")
    var
        Customer: Record Customer;
    begin
        if SalesOrderHeader."Sell-to Customer No." = '' then
            exit;

        if not Customer.Get(SalesOrderHeader."Sell-to Customer No.") then
            exit;

        // Set VAT Type based on customer's VAT registration status
        if Customer."VAT Registration No." <> '' then
            SalesOrderHeader."NGT_VATType" := SalesOrderHeader."NGT_VATType"::VAT
        else
            SalesOrderHeader."NGT_VATType" := SalesOrderHeader."NGT_VATType"::"Non-VAT";
    end;

    /// <summary>
    /// Event subscriber triggered after a Sales Quote is transferred to a Sales Order.
    /// Updates the customer name display after the order has been created.
    /// </summary>
    /// <param name="SalesOrderHeader">Sales Order Header record that was created.</param>
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Sales-Quote to Order", 'OnAfterInsertSalesOrderHeader', '', false, false)]
    local procedure OnAfterQuoteToOrderTransfer(var SalesOrderHeader: Record "Sales Header")
    begin
        // Update customer name display
        if SalesOrderHeader."Sell-to Customer No." <> '' then
            SalesOrderHeader.UpdateCustomerNoDisplay();
    end;

    #endregion
}
