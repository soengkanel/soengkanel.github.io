/// <summary>
/// Codeunit NGT_SalesInvoiceVATSeriesHandler (ID 50001).
/// Handles automatic VAT Type assignment and number series selection for Sales Orders
/// based on customer VAT registration status.
/// </summary>
codeunit 50001 "NGT_SalesInvVATSeriesHandler"
{
    #region Event Subscribers

    /// <summary>
    /// Event subscriber triggered before posting a Sales document.
    /// Automatically assigns appropriate posting number series based on customer VAT registration status.
    /// For customers without VAT Registration No., uses Commercial Invoice/Credit Memo series.
    /// For customers with VAT Registration No., uses standard Invoice/Credit Memo series.
    /// </summary>
    /// <param name="SalesHeader">Sales Header record being posted.</param>
    /// <param name="CommitIsSuppressed">Indicates if commit is suppressed.</param>
    /// <param name="PreviewMode">Indicates if posting is in preview mode.</param>
    /// <param name="HideProgressWindow">Controls visibility of progress window.</param>
    /// <param name="IsHandled">Indicates if the event has been handled.</param>
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Sales-Post", OnBeforePostSalesDoc, '', false, false)]
    local procedure OnBeforePostSalesDoc(var SalesHeader: Record "Sales Header"; CommitIsSuppressed: Boolean; PreviewMode: Boolean; var HideProgressWindow: Boolean; var IsHandled: Boolean)
    var
        Customer: Record Customer;
        SalesSetup: Record "Sales & Receivables Setup";
    begin
        if PreviewMode then
            exit;

        SalesSetup.Get;
        if (SalesHeader."Document Type" in [SalesHeader."Document Type"::Order, SalesHeader."Document Type"::Invoice]) and (SalesHeader."Sell-to Customer No." <> '') then begin
            Customer.Get(SalesHeader."Sell-to Customer No.");
            if (Customer."VAT Registration No." = '') then begin
                SalesSetup.Testfield("NGT_PostedCommInvoiceNos");
                SalesHeader."Posting No. Series" := SalesSetup."NGT_PostedCommInvoiceNos";
            end else begin
                SalesSetup.Testfield("Posted Invoice Nos.");
                SalesHeader."Posting No. Series" := SalesSetup."Posted Invoice Nos.";
            end;
        end;

        if (SalesHeader."Document Type" in [SalesHeader."Document Type"::"Return Order", SalesHeader."Document Type"::"Credit Memo"]) and (SalesHeader."Sell-to Customer No." <> '') then begin
            Customer.Get(SalesHeader."Sell-to Customer No.");
            if (Customer."VAT Registration No." = '') then begin
                SalesSetup.Testfield("NGT_PostedCommCreditMemoNos");
                SalesHeader."Posting No. Series" := SalesSetup."NGT_PostedCommCreditMemoNos";
            end else begin
                SalesSetup.Testfield("Posted Credit Memo Nos.");
                SalesHeader."Posting No. Series" := SalesSetup."Posted Credit Memo Nos.";
            end;
        end;
    end;

    #endregion
}