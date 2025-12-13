---
layout: post
title: "[BC] SharePoint List Formatting: Transforming Data into a Modern UI"
date: 2025-12-08 10:50:00 +0700
categories: [BC]
tags: [SharePoint, JSON Formatting, UI Design, Microsoft 365, Low-Code]
author: Soeng Kanel
thumbnail: /images/bc.png
description: "How to customize SharePoint List Views using JSON formatting. A practical guide for 'Client Bank' including data source explanation and real-world code examples."
---

In our previous [Implementation Guide]({% post_url 2025-12-08-[BC]-sharepoint-sitemap-implementation-guide %}), we decided to use **SharePoint Lists** for the "Products" and "Tools" sections of the Client Bank intranet.

A common implementation question is: *"A default SharePoint list looks like a boring Excel spreadsheet. How do we make it look like a modern App or Product Catalog?"*

The answer is **JSON View Formatting**.

## Part 1: Where is the "Data Source"?

Beginners often look for a "Database Connection" button. In SharePoint, **the List IS the Database.**

For Client Bank Cambodia, the data comes from:
1.  **Manual Entry**: The Product Owner (Marketing Team) clicks "New" and fills in the form.
2.  **Excel Import**: You can "Create List from Excel" to upload the initial 500 products.
3.  **Power Automate**: You could build a flow that syncs data from the Core Banking System (SQL) to this SharePoint List every night.

**Key Definition**: The text, numbers, and status choices stored in the list columns *are* your data source. The "View" is just the visual layer on top of it.

## Part 2: Customizing the Look (The "Gallery View")

We don't want the "Tools Portal" to look like a spreadsheet. We want it to look like an App Store.

### Use Case: The "Tools" Portal
**Goal**: Display tools (HRMS, Core Banking) as cards with icons.

**Technique**: Gallery View Formatting.
1.  Go to your List View.
2.  Click the creating view dropdown -> **Format current view**.
3.  Select **"Gallery"**.
4.  Click **"Edit Card"** or paste custom JSON.

### The JSON Code (Copy-Paste this)
Here is a simple JSON template that creates a "Card" layout.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/sp/v2/tile-formatting.schema.json",
  "height": 150,
  "width": 250,
  "hideSelection": false,
  "fillHorizontally": true,
  "formatter": {
    "elmType": "div",
    "style": {
      "display": "flex",
      "flex-direction": "column",
      "align-items": "center",
      "justify-content": "center",
      "background-color": "#f3f2f1",
      "border-radius": "8px",
      "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
      "margin": "10px",
      "cursor": "pointer"
    },
    "attributes": {
      "class": "ms-bgColor-neutralLighterHelper ms-bgColor-themePrimary--hover"
    },
    "children": [
      {
        "elmType": "a",
        "attributes": {
          "href": "[$URL]",
          "target": "_blank"
        },
        "style": {
          "text-decoration": "none",
          "color": "#333",
          "width": "100%",
          "height": "100%",
          "display": "flex",
          "flex-direction": "column",
          "align-items": "center",
          "justify-content": "center"
        },
        "children": [
          {
            "elmType": "img",
            "attributes": {
              "src": "[$IconLink]"
            },
            "style": {
              "width": "48px",
              "height": "48px",
              "margin-bottom": "10px"
            }
          },
          {
            "elmType": "div",
            "txtContent": "[$Title]",
            "style": {
              "font-size": "16px",
              "font-weight": "600"
            }
          }
        ]
      }
    ]
  }
}
```
*Note: This assumes you have columns named `URL`, `IconLink`, and `Title`.*

## Part 3: Column Formatting (Traffic Lights)

For the **Products & Services** list, we want a spreadsheet view, but we want the "Status" column to pop.

### Use Case: Product Status
*   **Active**: Green background
*   **Obsolete**: Red background, strike-through text
*   **Pipeline**: Yellow background

1.  Click the column header "Status".
2.  **Column settings** -> **Format this column**.
3.  Use **Conditional Formatting** (No code required!) OR use JSON for advanced control.

### The JSON Approach (Advanced)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/sp/v2/column-formatting.schema.json",
  "elmType": "div",
  "txtContent": "@currentField",
  "style": {
    "background-color": "=if(@currentField == 'Active', '#cff6cf', if(@currentField == 'Obsolete', '#fde7e9', '#fff4ce'))",
    "color": "=if(@currentField == 'Active', '#107c10', if(@currentField == 'Obsolete', '#a80000', '#5c2d91'))",
    "padding": "5px 10px",
    "border-radius": "15px",
    "font-weight": "bold",
    "text-decoration": "=if(@currentField == 'Obsolete', 'line-through', 'none')"
  }
}
```

## Summary for Client Bank

1.  **Format the "Tools" List** as a **Gallery (Tiles)**. It makes the page look like a dashboard of apps.
2.  **Format the "Products" List** as a **Detail List** but add **Column Formatting** to Status and Complexity columns to make important data visible at a glance.
3.  **Data Source**: The list *is* the source. You manage the data by editing the rows, just like Excel.
