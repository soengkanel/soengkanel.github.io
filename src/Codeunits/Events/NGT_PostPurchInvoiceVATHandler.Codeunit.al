codeunit 50030 "NGT_PostPurchInvoiceVATHandler"
{
    #region Event Subscribers
    /// <summary>
    /// Event subscriber triggered before posting a Sales document.
    /// Automatically assigns appropriate posting number series based on customer VAT registration status.
    /// For customers without VAT Registration No., uses Commercial Invoice/Credit Memo series.
    /// For customers with VAT Registration No., uses standard Invoice/Credit Memo series.
    /// </summary>
    /// <param name="PurchaseHeader">PurchaseHeader  record being posted.</param>
    /// <param name="CommitIsSuppressed">Indicates if commit is suppressed.</param>
    /// <param name="PreviewMode">Indicates if posting is in preview mode.</param>
    /// <param name="HideProgressWindow">Controls visibility of progress window.</param>
    /// <param name="IsHandled">Indicates if the event has been handled.</param>
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Purch.-Post", OnBeforePostPurchaseDoc, '', false, false)]
    local procedure OnBeforePostPurchaseDoc(var PurchaseHeader: Record "Purchase Header"; CommitIsSupressed: Boolean; PreviewMode: Boolean; var HideProgressWindow: Boolean; var IsHandled: Boolean)
    var
        Vendor: Record Vendor;
        PurchSetup: Record "Purchases & Payables Setup";
    begin
        if PreviewMode then
            exit;
        PurchSetup.Get;
        if (PurchaseHeader."Document Type" in [PurchaseHeader."Document Type"::Order
            , PurchaseHeader."Document Type"::Invoice]) and (PurchaseHeader."Buy-from Vendor No." <> '') then begin
            Vendor.Get(PurchaseHeader."Buy-from Vendor No.");
            if (Vendor."VAT Registration No." = '') then begin
                PurchSetup.Testfield("NGT_PostedCommInvoiceNos");
                PurchaseHeader."Posting No. Series" := PurchSetup."NGT_PostedCommInvoiceNos";
            end else begin
                PurchSetup.Testfield("Posted Invoice Nos.");
                PurchaseHeader."Posting No. Series" := PurchSetup."Posted Invoice Nos.";
            end;
        end;

        if (PurchaseHeader."Document Type" in [PurchaseHeader."Document Type"::"Return Order"
            , PurchaseHeader."Document Type"::"Credit Memo"]) and (PurchaseHeader."Buy-from Vendor No." <> '') then begin
            Vendor.Get(PurchaseHeader."Buy-from Vendor No.");
            if (Vendor."VAT Registration No." = '') then begin
                PurchSetup.Testfield("NGT_PostedCommCreditMemoNos");
                PurchaseHeader."Posting No. Series" := PurchSetup."NGT_PostedCommCreditMemoNos";
            end else begin
                PurchSetup.Testfield("Posted Credit Memo Nos.");
                PurchaseHeader."Posting No. Series" := PurchSetup."Posted Credit Memo Nos.";
            end;
        end;






    end;
    #endregion
}