/// <summary>
/// Table Extension NGT_PurchaseHeader (ID 51001) extends Purchase Header.
/// Adds VAT Type field to distinguish between VAT and Non-VAT purchase documents.
/// </summary>
tableextension 51001 "NGT_PurchaseHeader" extends "Purchase Header"
{
    fields
    {
        field(51000; "NGT_VATType"; Option)
        {
            Caption = 'VAT Type';
            OptionMembers = " ","VAT","Non-VAT";
            OptionCaption = ' ,VAT,Non-VAT';
            DataClassification = CustomerContent;
            Editable = false;
        }
    }
}
