---
layout: post
title: "[BC] Mastering SharePoint Implementation: 5 Golden Rules for Success"
date: 2025-12-08 11:10:00 +0700
categories: [BC]
tags: [SharePoint, Project Management, Best Practices, Governance, Architecture]
author: Soeng Kanel
thumbnail: /images/bc.png
description: "Implementing SharePoint is easy; keeping it useful is hard. Here are the 5 key principles successful consultants use to master SharePoint projects."
---

After designing and building the "Client Bank" intranet, you might feel ready to deploy. But wait.

Technically building a site is only 20% of the work. The other 80% is Strategy, Governance, and Adoption. If you want to move from a "SharePoint Builder" to a "SharePoint Architect", you need to master these 5 Golden Rules.

## Rule #1: Flatten Your Architecture (Death to Subsites)

In the old days (SharePoint 2010/2013), we built deep hierarchies:
*   `Home > HR > Benefits > 2025`

**Do NOT do this.** Microsoft has deprecated this model.

**The Master Strategy**: Use a **Flat Architecture**.
*   Every site is a top-level site collection.
*   Use **Hub Sites** to connect them together initially.
*   **Why?** If the "Benefits" department moves from HR to Finance next year, you just change the Hub association link. In a subsite model, you would have to migrate gigabytes of data.

## Rule #2: Content Types are King

Beginners create columns directly on the list (`Add Column > Text`).
Masters create **Site Columns** and **Content Types**.

**The Scenario**: You have 10 different libraries (HR Polices, IT Guides, Finance Forms). They all need a "Review Date" and "Owner" column.
*   **Junior Approach**: Create "Review Date" 10 times manually.
*   **Master Approach**: Create a Site Column *once*. Add it to a Content Type "Corporate Document".
*   **The Payoff**: If you want to search for *all* documents with a "Review Date" next month, you can do it instantly because they share the same internal ID.

## Rule #3: Search is the Real UI

Stop forcing users to click through 5 layers of navigation.
*   *Bad:* "Go to HR, then Policies, then 2025, then click the Pdf."
*   *Good:* "Type 'Travel Policy' in the search bar."

**Master implementation**:
1.  Map your columns to **RefinableManagedProperties** (as we did in the [Technical Guide]({% post_url 2025-12-08-[BC]-technical-implementation-bank-intranet %})).
2.  Build "Search-Driven Pages". A page that just says "Latest News" should actually be a Search Web Part showing "content type = News AND date = This Month".

## Rule #4: Governance Before Growth

If you don't set rules, your clean intranet will become a dumpster fire in 6 months.

**Define these 3 things before launch:**
1.  **Site Creation**: Who can create a new site? (Hint: *Not* everyone. Turn off self-service site creation).
2.  **Lifecycle**: What happens when a project ends? Is the site archived? Deleted? Read-only?
3.  **Ownership**: Every site typically needs *two* owners. If one leaves the company, the site isn't orphaned.

## Rule #5: Vanilla First (Avoid Custom Code)

Just because you *can* write code (SPFx), doesn't mean you *should*.

**The "Vanilla" Test**:
*   Can I do this with a List View?
*   Can I do this with Power Automate?
*   Can I do this with JSON formatting?

Only write code if the answer is "No" to all of the above. Custom code breaks. It requires maintenance. It creates "Technical Debt". Native SharePoint features (like our Client Bank intranet) update automatically and cost \$0 to maintain.

## Summary

Mastering SharePoint isn't about knowing every button in the settings menu. It's about designing a system that is **Flexible** (Flat Architecture), **Consistent** (Content Types), and **Maintainable** (Vanilla Features).
