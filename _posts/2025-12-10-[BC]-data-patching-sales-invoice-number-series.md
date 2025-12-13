---
layout: post
title: "[BC] Data Patching for Number Series of Posted Sales Invoice in Business Central"
tags: [Business Central, AL Development, Troubleshooting, Data Patching, ERP]
thumbnail: /images/bc.png
---

One of the most panic-inducing errors in Microsoft Dynamics 365 Business Central is when your Number Series gets out of sync. It usually happens right before a major deadline: a user tries to post an invoice, and BC screams that "Order No. INV-10203 already exists."

In this article, we'll dive deep into "Data Patching" for Number Series—specifically for Posted Sales Invoices. We will cover safe fixes for common sync issues and the "nuclear option" for modifying posted records (strictly for non-production/repair scenarios).

## The Problem: Why Number Series Break

Business Central's Number Series normally work flawlessly. But they break under specific conditions:
1.  **Bad Migrations:** Importing historical data without updating the "Last No. Used" pointer.
2.  **Deleted Records:** A user deletes an unposted document that had already been assigned a number.
3.  **System Crashes/Rollbacks:** A transaction fails mid-flight, but the number series line was already incremented.
4.  **Parallel Posting:** High-concurrency environments causing race conditions (rare, but possible).

## Scenario 1: The "Last No. Used" Is Out of Sync

This is the most common scenario. You have posted invoice `PSI-0099`. The system shouldn't try to use `PSI-0099` again, but the Number Series line says `Last No. Used` is `PSI-0098`.

When the next user tries to post, BC tries to grab `PSI-0099`, sees it already exists in the `Sales Invoice Header`, and throws an error.

### The Fix: Updating No. Series Lines
This doesn't require code, just permissions.

1.  Search for **No. Series**.
2.  Find the code used for Posted Invoices (often `S-INV+` or similar).
3.  Click **Lines** to view the active sequence.
4.  Locate the **Last No. Used** field.
5.  **Manually update it** to the actual highest number found in your Posted Sales Invoices.

*Tip: If the field is non-editable, you may need to check "Allow Gaps in Nos." temporarily to unlock specific editing capabilities, though usually, this field is editable.*

## Scenario 2: Filling Gaps in Posted Invoices

Auditors hate gaps. If you have `PSI-0001`, `PSI-0002`, and `PSI-0004`, they will ask: "Where is 0003? Did you delete a fraudulent invoice?"

In BC, you **cannot** simply insert a record into the `Sales Invoice Header` table to fill the gap because posted documents are immutable.

### The Workaround: Dummy Invoices
1.  Temporarily change the **Last No. Used** in the No. Series to `PSI-0002`.
2.  Create a "Dummy" Sales Order or Invoice with zero value or a correction line.
3.  Post it. It will take the ID `PSI-0003`.
4.  Reset the **Last No. Used** back to its correct state (`PSI-0004`).

This fills the gap with a traceable, explanatory record rather than a hidden deletion.

## Scenario 3: The "Nuclear Option" – Modifying Posted Invoice Numbers via AL

**WARNING:** Modifying posted document numbers (`No.` field) is generally forbidden. It breaks links to G/L Entries, Customer Ledger Entries, Value Entries, and Dimensions. **Do not do this in a live environment unless you have a script that updates ALL related tables.**

However, valid use cases exist:
*   Fixing a botched data migration in a sandbox.
*   Correcting a series format (e.g., changing `INV100` to `PSI-INV100`) before go-live.

### Why You Can't Just "Rename"
If you try to rename a record in `Sales Invoice Header` via a configuration package, it often fails because standard BC validation logic blocks renaming of posted records.

### The Code Solution
To patch this, you need a processing-only report or codeunit with explicit permissions to bypass the read-only check on the `Sales Invoice Header`.

```al
permissionset 50100 "ForceUpdate"
{
    Assignable = true;
    Permissions = tabledata "Sales Invoice Header" = RM; // RM = Read/Modify
}

codeunit 50100 "Fix Invoice Numbers"
{
    Permissions = tabledata "Sales Invoice Header" = rm;

    trigger OnRun()
    var
        SalesInvHeader: Record "Sales Invoice Header";
    begin
        // SAFELY Renaming a record
        // Note: Renaming triggers updates to related tables (Lines, Comments, etc.)
        // automatically IF the relation is defined in the table schema.
        
        if SalesInvHeader.Get('OLD-NO-123') then begin
            if SalesInvHeader.Rename('NEW-NO-123') then
                Message('Renamed Successfully')
            else
                Error('Rename failed: %1', GetLastErrorText());
        end;
    end;
}
```

### Critical Links to Patch Manually
If `Rename` works, BC handles many relations. But if you are doing SQL-level Direct patching (never recommended) or if relations are broken, you must manually update:
1.  **Sales Invoice Lines**: `Document No.`
2.  **Cust. Ledger Entry**: `Document No.`
3.  **G/L Entry**: `Document No.`
4.  **Value Entry**: `Document No.`
5.  **Detailed Cust. Ledg. Entry**: `Document No.`

A safer purely AL approach updates these in a transaction:

```al
procedure PatchInvoiceNo(OldNo: Code[20]; NewNo: Code[20])
var
    SalesInvHeader: Record "Sales Invoice Header";
    GLEntry: Record "G/L Entry";
    CustLedgEntry: Record "Cust. Ledger Entry";
begin
    // Update Header
    if SalesInvHeader.Get(OldNo) then
        SalesInvHeader.Rename(NewNo);

    // Update G/L Entries (Example of manual patch if rename doesn't cascade)
    GLEntry.SetRange("Document No.", OldNo);
    if GLEntry.FindSet() then
        repeat
            GLEntry."Document No." := NewNo;
            GLEntry.Modify();
        until GLEntry.Next() = 0;
        
    // Repeat for other ledgers...
end;
```

## Summary

Data patching number series is acceptable when fixing configuration pointers (`Last No. Used`). However, changing the actual numbers of posted documents (`Sales Invoice Header`) is a high-risk operation that jeopardizes audit trails and relational integrity.

| Action | Difficulty | Risk Level | Recommended Tool |
| :--- | :--- | :--- | :--- |
| **Fix "Last No. Used"** | Low | Low | BC UI (No. Series Page) |
| **Fill Gaps** | Medium | Medium | Manual Dummy Postings |
| **Renumber Posted Docs** | High | Critical | AL Code with Permissions |

Always backup your company data or test in a sandbox before attempting Scenario 3!
