/// <summary>
/// Table Extension NGT_GenJournalBatch (ID 53000) extends Gen. Journal Batch.
/// Adds VAT Type field to classify payment journal batches for VAT compliance.
/// </summary>
tableextension 53000 "NGT_GenJournalBatch" extends "Gen. Journal Batch"
{
    fields
    {
        field(53000; "NGT_VATType"; Option)
        {
            Caption = 'VAT Type';
            OptionMembers = " ","VAT","Non-VAT";
            OptionCaption = ' ,VAT,Non-VAT';
            DataClassification = CustomerContent;
        }
    }
}
