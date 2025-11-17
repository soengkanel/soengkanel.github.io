/// <summary>
/// Codeunit NGT_PurchOrderVATHandler (ID 51000).
/// Handles automatic VAT Type assignment and number series selection for Purchase Orders
/// based on vendor VAT registration status.
/// </summary>
codeunit 51000 "NGT_PurchOrderVATHandler"
{
    #region Event Subscribers

    /// <summary>
    /// Event subscriber triggered when Buy-from Vendor No. is validated on Purchase Header.
    /// Automatically assigns VAT Type and appropriate number series based on vendor VAT registration status.
    /// </summary>
    /// <param name="Rec">Purchase Header record being modified.</param>
    /// <param name="xRec">Previous Purchase Header record state.</param>
    [EventSubscriber(ObjectType::Table, Database::"Purchase Header", 'OnAfterValidateEvent', 'Buy-from Vendor No.', false, false)]
    local procedure OnAfterValidateBuyfromVendorNo(var Rec: Record "Purchase Header"; var xRec: Record "Purchase Header")
    var
        PurchSetup: Record "Purchases & Payables Setup";
        Vendor: Record Vendor;
        xVendor: Record Vendor;
        NoSeries: Codeunit "No. Series";
        NewNo: Code[20];
        OldVATStatus: Boolean;
        NewVATStatus: Boolean;
    begin
        //  Message('DEBUG: OnAfterValidate Vendor - Document Type: %1, Old Vendor: %2, New Vendor: %3, Current No: %4, Current No. Series: %5',
        //          Rec."Document Type", xRec."Buy-from Vendor No.", Rec."Buy-from Vendor No.", Rec."No.", Rec."No. Series");

        // Only process Purchase Orders
        if Rec."Document Type" <> Rec."Document Type"::Order then begin
            // Message('DEBUG: Skipping - Not a Purchase Order');
            exit;
        end;

        // Get Purchases & Payables Setup
        if not PurchSetup.Get() then begin
            // Message('DEBUG: ERROR - Failed to get Purchases & Payables Setup');
            exit;
        end;

        // Message('DEBUG: Purchases Setup retrieved - VAT Series: %1, Non-VAT Series: %2',
        //         PurchSetup."NGT_VATPurchOrderSeries", PurchSetup."NGT_NonVATPurchOrderSeries");

        // Determine if vendor has changed and if VAT status changed
        OldVATStatus := false;
        NewVATStatus := false;

        if xRec."Buy-from Vendor No." <> '' then
            if xVendor.Get(xRec."Buy-from Vendor No.") then
                OldVATStatus := xVendor."VAT Registration No." <> '';

        // Get new vendor record and check VAT Registration status
        if Vendor.Get(Rec."Buy-from Vendor No.") then begin
            NewVATStatus := Vendor."VAT Registration No." <> '';
            // Message('DEBUG: Vendor found - VAT Reg No: %1, Old VAT Status: %2, New VAT Status: %3',
            //         Vendor."VAT Registration No.", OldVATStatus, NewVATStatus);

            // Check if VAT status has changed (Vendor changed from VAT to Non-VAT or vice versa)
            if (OldVATStatus <> NewVATStatus) and (Rec."No." <> '') then begin
                // Message('DEBUG: VAT status changed! Old No: %1, Old Series: %2. Vendor switching not supported after number assignment.',
                //         Rec."No.", Rec."No. Series");
                Error('The system has already automatically assigned a document number. Please verify the selected vendor and create a new document if correction is needed.');
                // Exit without making changes - BC doesn't allow renumbering existing documents
                exit;
            end;

            if NewVATStatus then begin
                // Vendor has VAT Registration No. - assign VAT type and series
                // Message('DEBUG: Vendor HAS VAT - Assigning VAT Type and Series');
                Rec."NGT_VATType" := Rec."NGT_VATType"::"VAT";
                if PurchSetup.NGT_VATPurchOrderSeries <> '' then begin
                    // Check if we need to assign number
                    if (Rec."No. Series" <> PurchSetup."NGT_VATPurchInvoiceSeries") or (Rec."No." = '') then begin
                        // Message('DEBUG: Assigning VAT series and number - Current No: %1, Current Series: %2, Target Series: %3',
                        //         Rec."No.", Rec."No. Series", PurchSetup.NGT_VATPurchOrderSeries);

                        if Rec."No." = '' then begin
                            Rec."No. Series" := PurchSetup."NGT_VATPurchOrderSeries";
                            // Generate number from VAT series
                            NewNo := NoSeries.GetNextNo(PurchSetup.NGT_VATPurchOrderSeries, WorkDate(), true);
                            Rec."No." := NewNo;
                            // Message('DEBUG: VAT Number assigned - No: %1, No. Series: %2', Rec."No.", Rec."No. Series");
                        end else begin
                            // Message('DEBUG: Already has VAT number, keeping it: %1', Rec."No.");
                        end;
                    end else begin
                        // Message('DEBUG: Already using VAT series, no change needed');
                    end;
                end else begin
                    // Message('DEBUG: WARNING - VAT Purchases No. Series is not configured in setup');
                end;
            end else begin
                // Vendor does not have VAT Registration No. - assign Non-VAT type and series
                // Message('DEBUG: Vendor NO VAT - Assigning Non-VAT Type and Series');
                Rec."NGT_VATType" := Rec."NGT_VATType"::"Non-VAT";
                if PurchSetup."NGT_NonVATPurchOrderSeries" <> '' then begin
                    // Check if we need to assign number
                    if (Rec."No. Series" <> PurchSetup."NGT_NonVATPurchOrderSeries") or (Rec."No." = '') then begin
                        // Message('DEBUG: Assigning Non-VAT series and number - Current No: %1, Current Series: %2, Target Series: %3',
                        //         Rec."No.", Rec."No. Series", PurchSetup."NGT_NonVATPurchOrderSeries");

                        if Rec."No." = '' then begin
                            Rec."No. Series" := PurchSetup."NGT_NonVATPurchOrderSeries";
                            // Generate number from Non-VAT series
                            NewNo := NoSeries.GetNextNo(PurchSetup."NGT_NonVATPurchOrderSeries", WorkDate(), true);
                            Rec."No." := NewNo;
                            // Message('DEBUG: Non-VAT Number assigned - No: %1, No. Series: %2', Rec."No.", Rec."No. Series");
                        end else begin
                            // Message('DEBUG: Already has Non-VAT number, keeping it: %1', Rec."No.");
                        end;
                    end else begin
                        // Message('DEBUG: Already using Non-VAT series, no change needed');
                    end;
                end else begin
                    // Message('DEBUG: WARNING - Non-VAT Purchases No. Series is not configured in setup');
                end;
            end;
        end else begin
            // Message('DEBUG: WARNING - Vendor not found with No: %1', Rec."Buy-from Vendor No.");
        end;
    end;

    #endregion
}
