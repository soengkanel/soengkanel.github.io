/// <summary>
/// Table Extension NGT_Item (ID 54000) extends Item.
/// Adds Item Class field for categorizing items by classification type.
/// </summary>
tableextension 54000 "NGT_Item" extends Item
{
    fields
    {
        field(54000; "NGT_ItemClass"; Text[255])
        {
            Caption = 'Item Class';
            DataClassification = CustomerContent;
        }
    }
}
