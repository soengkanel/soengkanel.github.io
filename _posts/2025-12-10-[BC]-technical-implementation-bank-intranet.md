---
layout: post
title: "[BC] Technical Guide: Implementing the Bank Intranet (Zero Code)"
date: 2025-12-10 09:00:00 +0700
categories: [BC]
tags: [SharePoint, Tutorial, Implementation, No-Code, Microsoft 365]
author: Soeng Kanel
thumbnail: /images/bc.png
description: "A step-by-step technical guide to implementing the 'Client Bank' intranet. From Site Columns and Content Types to constructing the dynamic Product Catalog list."
---

Following our [intranet design case study]({% post_url 2025-12-09-[BC]-case-study-bank-intranet-design %}), this article provides the technical "How-To". We will implement the "Client Bank" intranet using **zero custom code**, relying entirely on native SharePoint Online features.

This guide assumes you have **SharePoint Administrator** or **Site Owner** permissions.

## Phase 1: Environment & Site Creation

The first step is selecting the correct site template. Do not use a "Team Site" (which creates a Microsoft 365 Group/Teams integration you don't need for an intranet).

1.  **Go to SharePoint Admin Center**.
2.  **Create Site** -> **Communication Site**.
3.  **Design**: Choose "Topic" (provides a good default layout) or "Blank".
4.  **Site Name**: `Client Bank Intranet`.
5.  **Language**: `English`.

**Why Communication Site?** It assumes a small number of content creators and a large number of readers—perfect for an intranet.

## Phase 2: Information Architecture (The Backbone)

We never create columns directly on a list if we can avoid it. We create **Site Columns** and **Content Types** for reusability and better search indexing.

### Step 1: Create Site Columns
Go to **Site Settings** -> **Site information** -> **View all site settings** -> **Site columns**.

Create the following columns (Group: `Client Bank Columns`):

| Column Name | Type | Choices/Configuration |
| :--- | :--- | :--- |
| `Product Segment` | Choice | Retail, Commercial, Staff |
| `Product Status` | Choice | Active, Obsolete, Pipeline |
| `Target Market` | Text | (Single line of text) |
| `Investment Complexity` | Choice | Low, Medium, High |
| `Fees and Charges` | Multiple lines of text | Plain text or Rich text |

### Step 2: Create "Bank Product" Content Type
Go to **Site Settings** -> **Site content types**.

1.  **Create Content Type**.
2.  **Name**: `Bank Product`.
3.  **Parent Category**: `List Content Types`.
4.  **Parent Content Type**: `Item`.
5.  **Add Columns**: Add the site columns you created in Step 1.

## Phase 3: The "Products & Services" Engine

Now we build the catalog.

1.  **Site Contents** -> **New** -> **List** -> **Blank List**.
2.  **Name**: `Products and Services`.
3.  **Settings** -> **Advanced Settings**:
    *   **Allow management of content types**: `Yes`.
4.  **Settings** -> **Content Types**:
    *   Add `Bank Product`.
    *   Remove `Item` (so `Bank Product` is the default).
5.  **Views**:
    *   Create a View named `Retail Products`: Filter where `Product Segment` is `Retail` AND `Status` is `Active`.
    *   Create a View named `Commercial Products`: Filter where `Product Segment` is `Commercial` AND `Status` is `Active`.

## Phase 4: The Home Page Configuration

We will use the **Modern Script Editor** (if enabled) or standard Web Parts to layout the homepage.

### 1. The Hero Web Part (Top Banner)
*   **Layout**: `Three layers` or `One layer` (Carousel).
*   **Content**: Link to `Vision & Strategy`, `Latest CEO Message`.

### 2. News Web Part (Headlines)
*   **Layout**: `Top story`.
*   **Filter**: We need a "Headline" tag.
    *   *Implementation*: Go to **Site Pages Library** -> Add Column `IsHeadline` (Yes/No).
    *   In the Web Part settings: **Filter** -> `Page properties` -> `IsHeadline` equals `Yes`.

### 3. Quick Links (Applications)
*   **Layout**: `Compact` or `Tiles`.
*   **Links**: Add URLs for `Core Banking`, `HRMS`, `IT Helpdesk`.
*   **Icons**: Use custom uploaded icons for branding consistency.

## Phase 5: Navigation (Mega Menu)

1.  **Settings** (Gear Icon) -> **Change the look** -> **Navigation**.
2.  **Style**: `Mega Menu`.
3.  **Edit Navigation**:
    *   Create Label `Products & Services`.
    *   Add Sub-link `Retail Banking` -> Link to the `Retail Products` List View URL.
    *   Add Sub-link `Commercial Banking` -> Link to the `Commercial Products` List View URL.
    *   Repeat for HR, Tools, etc.

## Phase 6: Search & Refiners (Advanced)

To allow users to filter search results by "Product Segment" (e.g., in the global search bar), we need to map the Crawled Properties.

1.  **Wait for Indexing**: Add some dummy data to your Product List and wait 24 hours.
2.  **SharePoint Admin Center** -> **More features** -> **Search**.
3.  **Manage Search Schema**.
4.  **Crawled Properties**: Search for your column `ows_ProductSegment`.
5.  **Managed Properties**: Find a generic `RefinableString00`.
6.  **Mapping**: Map `ows_ProductSegment` to `RefinableString00`.
7.  **Alias**: Give it an alias `ProductSegment`.

Now, you can use the **PnP Search Web Parts** (if allowed) or the standard **Page Properties Filter** to filter content dynamically.

## Checklist for Go-Live

*   [ ] **Permissions**: Added "All Staff" (Security Group) to `Site Visitors`.
*   [ ] **Content**: Loaded initial 50 products.
*   [ ] **Testing**: Verify "Retail" user cannot edit "HR" documents (if item-level permissions required, though usually Site-level is enough).
*   [ ] **Mobile**: Checked layout on SharePoint Mobile App.

## Summary

By using **Content Types**, we ensured that "Products" are standardized data objects, not just loose text. By using **Views**, we created "Apps" for Retail and Commercial teams without writing a single line of code.

This foundation is scalable, searchable, and fully supported by Microsoft.
