/// <summary>
/// Page Extension NGT_ItemList (ID 50107) extends Item List.
/// Displays the Item Class field as a column in the Item List page.
/// </summary>
pageextension 50107 "NGT_ItemList" extends "Item List"
{
    layout
    {
        addlast(Control1)
        {
            field(NGT_ItemClass; Rec."NGT_ItemClass")
            {
                ApplicationArea = All;
                ToolTip = 'Specifies the classification of the item.';
            }
        }
    }
}
