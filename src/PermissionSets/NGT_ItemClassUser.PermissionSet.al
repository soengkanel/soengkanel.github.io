/// <summary>
/// Permission Set NGT_ItemClassUser (ID 50003).
/// Grants permissions for users to work with Item Class field.
/// Assign this to inventory staff and item managers.
/// </summary>
permissionset 50003 "NGT_ItemClassUser"
{
    Assignable = true;
    Caption = 'NGT Item Class User';

    Permissions =
        // Item - Full permissions for item management
        tabledata "Item" = RIMD;
}
