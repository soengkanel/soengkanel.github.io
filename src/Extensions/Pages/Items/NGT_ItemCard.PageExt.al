/// <summary>
/// Page Extension NGT_ItemCard (ID 50106) extends Item Card.
/// Displays the Item Class field in the Item Card page.
/// </summary>
pageextension 50106 "NGT_ItemCard" extends "Item Card"
{
    layout
    {
        addafter(Description)
        {
            field(NGT_ItemClass; Rec."NGT_ItemClass")
            {
                ApplicationArea = All;
                ToolTip = 'Specifies the classification of the item (e.g., Raw Material, Finished Good, Service, etc.).';
            }
        }
    }
}
