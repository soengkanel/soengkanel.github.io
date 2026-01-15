# Weekly Project Update Slides

This directory contains the Slidev presentation for the weekly project updates.

## Projects Included:
1. **NGD Enhancement (BC)**
2. **NGT Budget Control Extension (BC)**
3. **HR Lab (HRMS)**
4. **Bullseye (CRM)**
5. **CryptoTrading using QuantConnect**

## How to Update Data:
This presentation is data-driven.
1. Update your project progress, status, and notes in `projects.csv`.
2. Run the sync script to update the slides:
   ```bash
   node sync_projects.js
   ```
3. Your web slides will automatically refresh with the new data!

## How to Run Slides:
To start the presentation locally:
```bash
npx slidev
```
