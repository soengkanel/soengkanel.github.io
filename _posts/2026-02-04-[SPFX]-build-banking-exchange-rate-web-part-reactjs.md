---
layout: post
title: "[SPFX] Build a Banking Exchange Rate Web Part using ReactJS"
date: 2026-02-04 08:00:00 +0700
categories: [SPFX]
tags: [SharePoint, SPFx, ReactJS, TypeScript, Banking, Cambodia]
author: Soeng Kanel
thumbnail: /images/spfx_react_bank.png
description: "A comprehensive, step-by-step guide to building a professional SharePoint Framework (SPFx) web part using ReactJS, featuring a real-world Cambodia Bank exchange rate example."
---

In the digital transformation of the banking sector in Cambodia, SharePoint often serves as the backbone for internal communication. While out-of-the-box web parts are great, sometimes you need a custom, branded experience—like a **Daily Exchange Rate** dashboard.

In this guide, we will build a modern SPFx web part using **ReactJS** for a hypothetical Cambodia Bank.

---

## Prerequisites

Before we start, ensure your development environment is ready.

1.  **Node.js**: Use version **v18.x** or **v16.x** (Check [compatibility matrix](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/compatibility)).
2.  **Yeoman & Gulp**: 
    ```bash
    npm install -g yo gulp
    ```
3.  **SPFx Generator**:
    ```bash
    npm install -g @microsoft/generator-sharepoint
    ```

---

## Step 1: Create the Project

Open your terminal and run the SharePoint generator:

```bash
yo @microsoft/sharepoint
```

When prompted:
*   **Solution Name**: `bank-exchange-rates`
*   **Target**: `SharePoint Online only (latest)`
*   **Component Type**: `WebPart`
*   **WebPart Name**: `ExchangeRates`
*   **Template**: `React`

---

## Step 2: Designing the Data Model

For our Cambodia Bank example, we need to handle USD, KHR, and EUR. Create a file `src/webparts/exchangeRates/models/IExchangeRate.ts`:

```typescript
export interface IExchangeRate {
  currency: string;
  symbol: string;
  buying: number;
  selling: number;
  trend: 'up' | 'down';
}
```

---

## Step 3: Building the React Component

Open `src/webparts/exchangeRates/components/ExchangeRates.tsx`. We will create a clean, premium table structure.

```tsx
import * as React from 'react';
import styles from './ExchangeRates.module.scss';
import { IExchangeRatesProps } from './IExchangeRatesProps';
import { IExchangeRate } from '../models/IExchangeRate';

const ExchangeRates: React.FC<IExchangeRatesProps> = (props) => {
  const [rates, setRates] = React.useState<IExchangeRate[]>([
    { currency: 'USD/KHR', symbol: '$', buying: 4095, selling: 4110, trend: 'up' },
    { currency: 'EUR/KHR', symbol: '€', buying: 4350, selling: 4380, trend: 'up' },
    { currency: 'USD/THB', symbol: '฿', buying: 34.50, selling: 35.20, trend: 'down' },
  ]);

  return (
    <section className={styles.exchangeRates}>
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.title}>DAILY EXCHANGE RATES</span>
          <img src="/sites/Intranet/SiteAssets/bank-logo.png" alt="Bank Logo" className={styles.logo} />
        </div>
        
        <table className={styles.rateTable}>
          <thead>
            <tr>
              <th>Currency</th>
              <th>Buying</th>
              <th>Selling</th>
            </tr>
          </thead>
          <tbody>
            {rates.map((rate, index) => (
              <tr key={index}>
                <td className={styles.currencyName}>{rate.currency}</td>
                <td>{rate.buying.toLocaleString()}</td>
                <td className={rate.trend === 'up' ? styles.up : styles.down}>
                  {rate.selling.toLocaleString()} {rate.trend === 'up' ? '↑' : '↓'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className={styles.footer}>
          Last updated: {new Date().toLocaleDateString()}
        </div>
      </div>
    </section>
  );
};

export default ExchangeRates;
```

---

## Step 4: Adding Premium Styling

Banking apps must look trustworthy and professional. Edit `src/webparts/exchangeRates/components/ExchangeRates.module.scss`:

```scss
.exchangeRates {
  .container {
    padding: 20px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border-top: 5px solid #002e5d; // Dark Blue Banking Theme
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .title {
      font-weight: 700;
      color: #002e5d;
      letter-spacing: 1px;
    }
  }

  .rateTable {
    width: 100%;
    border-collapse: collapse;
    
    th {
      text-align: left;
      padding: 12px;
      color: #777;
      font-size: 12px;
      border-bottom: 1px solid #eee;
    }

    td {
      padding: 15px 12px;
      font-weight: 600;
      border-bottom: 1px solid #f9f9f9;
    }

    .currencyName {
      color: #333;
    }

    .up { color: #27ae60; }
    .down { color: #e74c3c; }
  }

  .footer {
    margin-top: 15px;
    font-size: 11px;
    color: #999;
    text-align: right;
  }
}
```

---

## Step 5: Testing Locally

To see your web part in action without deploying to SharePoint:

1.  Trust the dev certificate:
    ```bash
    gulp trust-dev-cert
    ```
2.  Start the local server:
    ```bash
    gulp serve
    ```
3.  Navigate to the **Hosted Workbench** on your SharePoint tenant:
    `https://your-tenant.sharepoint.com/_layouts/15/workbench.aspx`

---

## Step 6: Deployment

When you are ready for production:

1.  **Bundle**:
    ```bash
    gulp bundle --ship
    ```
2.  **Package**:
    ```bash
    gulp package-solution --ship
    ```
3.  **Upload**: Drag and drop the `.sppkg` file from `sharepoint/solution/` to your **SharePoint App Catalog**.

---

## Best Practices for Banking Intranets

*   **Security**: Never hardcode API keys in your React components. Use the `AadHttpClient` to call secured APIs.
*   **Performance**: Since exchange rates don't change every second, implement a local storage cache to reduce API calls.
*   **Theming**: Use the `ThemeProvider` to ensure your web part colors match the SharePoint site theme dynamically.

Building custom web parts with SPFx and React allows you to transform a standard SharePoint site into a high-end enterprise portal. For banks in Cambodia, where UI/UX is a competitive advantage, this technical skill is essential.

**Happy Coding!** 🚀
