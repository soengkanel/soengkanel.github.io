/// <summary>
/// Codeunit NGT_PaymentJournalVATValidator (ID 53000).
/// Validates that vendor VAT registration status matches the payment journal batch VAT Type.
/// Prevents posting of mismatched vendor payments to ensure compliance.
/// </summary>
codeunit 53000 "NGT_PaymentJnlVATValidator"
{
    #region Event Subscribers

    /// <summary>
    /// Event subscriber triggered when Account No. is validated on Gen. Journal Line.
    /// Validates that vendor VAT status matches the batch VAT Type.
    /// </summary>
    /// <param name="Rec">Gen. Journal Line record being modified.</param>
    /// <param name="xRec">Previous Gen. Journal Line record state.</param>
    [EventSubscriber(ObjectType::Table, Database::"Gen. Journal Line", 'OnAfterValidateEvent', 'Account No.', false, false)]
    local procedure ValidateVATBatchMatch(var Rec: Record "Gen. Journal Line"; var xRec: Record "Gen. Journal Line")
    var
        Batch: Record "Gen. Journal Batch";
        Vendor: Record Vendor;
        VendorType: Text;
        BatchType: Text;
    begin
        // Only validate Vendor accounts
        if Rec."Account Type" <> Rec."Account Type"::Vendor then
            exit;

        // Get Journal Batch
        if not Batch.Get(Rec."Journal Template Name", Rec."Journal Batch Name") then
            exit;

        // Get Vendor record
        if not Vendor.Get(Rec."Account No.") then
            exit;

        // Determine Vendor Type based on VAT Registration No.
        if Vendor."VAT Registration No." <> '' then
            VendorType := 'VAT'
        else
            VendorType := 'Non-VAT';

        // Determine Batch Type
        case Batch."NGT_VATType" of
            Batch."NGT_VATType"::"VAT":
                BatchType := 'VAT';
            Batch."NGT_VATType"::"Non-VAT":
                BatchType := 'Non-VAT';
            else
                exit; // Batch type not set, skip validation
        end;

        // Validate: Vendor Type must match Batch Type
        if VendorType <> BatchType then
            Error(
                'Vendor %1 is a %2 vendor, but you are using a %3 batch. Please select a matching batch or change the vendor.',
                Vendor."No.", VendorType, BatchType);
    end;

    #endregion
}
