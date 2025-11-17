/// <summary>
/// Page Extension NGT_GenJournalBatches (ID 50105) extends General Journal Batches.
/// Displays the VAT Type field for payment journal batch classification.
/// </summary>
pageextension 50105 "NGT_GenJournalBatches" extends "General Journal Batches"
{
    layout
    {
        addlast(Control1)
        {
            field(NGT_VATType; Rec."NGT_VATType")
            {
                ApplicationArea = All;
                ToolTip = 'Defines whether this batch is for VAT or Non-VAT vendor payments. System validates vendor VAT status against batch type.';
            }
        }
    }
}
